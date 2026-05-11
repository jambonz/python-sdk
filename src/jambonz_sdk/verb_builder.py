"""VerbBuilder base class with chainable verb methods.

Each verb method accepts three interchangeable forms:

1. A typed pydantic model: ``session.gather(Gather(input=["speech"], ...))``
2. A raw dict: ``session.gather({"input": ["speech"], "actionHook": "/x"})``
3. Keyword arguments: ``session.gather(input=["speech"], actionHook="/x")``

All three are validated and normalized through the verb's generated pydantic
model before being appended to the queue. Validation errors (unknown fields,
wrong types, cross-field rule violations) are raised at construction time,
not hours later on the jambonz server.

Methods are built from the verb registry at import time. Each method also
carries a real ``inspect.Signature`` + ``__annotations__`` so IDEs show
autocomplete hints for the kwargs style. For full typed autocomplete,
users should import and pass the model classes directly.
"""

from __future__ import annotations

import inspect
import json
import logging
import sys
from pathlib import Path
from typing import Any, Union

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

from pydantic import ValidationError

from jambonz_sdk._models._registry import verb_model
from jambonz_sdk.types.verbs import AnyVerb
from jambonz_sdk.verb_registry import VERB_DEFS, VerbDef

logger = logging.getLogger("jambonz_sdk.verb_builder")

# ── JSON Schema type → Python type mapping ────────────────────────────

_TYPE_ANNOTATION_MAP: dict[str, type | object] = {
    "string": str,
    "number": Union[int, float],
    "integer": int,
    "boolean": bool,
    "object": dict,
    "array": list,
}

_TYPE_STR_MAP: dict[str, str] = {
    "string": "str",
    "number": "int | float",
    "integer": "int",
    "boolean": "bool",
    "object": "dict[str, Any]",
    "array": "list[Any]",
}


def _resolve_type(prop_schema: Any) -> type | object:
    """Convert a JSON Schema property definition to a Python type annotation."""
    if isinstance(prop_schema, str):
        # Backward compat: simple type string (shouldn't happen with JSON Schema)
        return _TYPE_ANNOTATION_MAP.get(prop_schema, Any)

    if not isinstance(prop_schema, dict):
        return Any

    # $ref → component reference → dict
    if "$ref" in prop_schema:
        return dict

    # const → the type of the const value
    if "const" in prop_schema:
        val = prop_schema["const"]
        return type(val)

    # oneOf → union of the branch types
    if "oneOf" in prop_schema:
        parts: list[type | object] = []
        for branch in prop_schema["oneOf"]:
            resolved = _resolve_type(branch)
            if resolved is Union[int, float]:
                parts.extend([int, float])
            elif resolved not in parts:
                parts.append(resolved)
        # Deduplicate while preserving order
        seen: set[type | object] = set()
        unique = []
        for p in parts:
            if p not in seen:
                seen.add(p)
                unique.append(p)
        if len(unique) == 1:
            return unique[0]
        return Union[tuple(unique)]

    # Simple type
    schema_type = prop_schema.get("type")
    if isinstance(schema_type, str):
        return _TYPE_ANNOTATION_MAP.get(schema_type, Any)

    # Array of types
    if isinstance(schema_type, list):
        parts = []
        for t in schema_type:
            resolved = _TYPE_ANNOTATION_MAP.get(t, Any)
            if resolved is Union[int, float]:
                parts.extend([int, float])
            elif resolved not in parts:
                parts.append(resolved)
        if len(parts) == 1:
            return parts[0]
        return Union[tuple(parts)]

    return Any


def _python_type_str(prop_schema: Any) -> str:
    """Convert a JSON Schema property definition to a human-readable type string."""
    if isinstance(prop_schema, str):
        return _TYPE_STR_MAP.get(prop_schema, "Any")

    if not isinstance(prop_schema, dict):
        return "Any"

    if "$ref" in prop_schema:
        return "dict[str, Any]"

    if "const" in prop_schema:
        return repr(type(prop_schema["const"]).__name__)

    if "oneOf" in prop_schema:
        parts = [_python_type_str(branch) for branch in prop_schema["oneOf"]]
        return " | ".join(dict.fromkeys(parts))

    schema_type = prop_schema.get("type")
    if isinstance(schema_type, str):
        return _TYPE_STR_MAP.get(schema_type, "Any")
    if isinstance(schema_type, list):
        parts = [_TYPE_STR_MAP.get(t, "Any") for t in schema_type]
        return " | ".join(dict.fromkeys(parts))

    return "Any"


# ── Load JSON Schemas ──────────────────────────────────────────────────

def _load_schemas() -> dict[str, Any]:
    """Load verb JSON Schemas bundled alongside this package.

    Returns a dict mapping verb spec names (e.g. 'say', 'sip:decline')
    to their schema dicts, with a 'properties' key and optionally 'required'.
    """
    schema_dir = Path(__file__).resolve().parent / "schema" / "verbs"
    schemas: dict[str, Any] = {}

    if not schema_dir.is_dir():
        logger.warning("Schema directory not found: %s", schema_dir)
        return schemas

    for schema_file in sorted(schema_dir.glob("*.schema.json")):
        with schema_file.open() as f:
            schema = json.load(f)

        # Derive the spec name from the $id or filename
        schema_id = schema.get("$id", "")
        if schema_id:
            # e.g. "https://jambonz.org/schema/verbs/say" → "say"
            # e.g. "https://jambonz.org/schema/verbs/sip:decline" → "sip:decline"
            spec_name = schema_id.rsplit("/", 1)[-1]
        else:
            # Fallback: filename without .schema.json
            spec_name = schema_file.stem.replace(".schema", "")

        # Collect properties, skipping 'verb' (it's a const, not a user param)
        properties = {}
        for prop_name, prop_def in schema.get("properties", {}).items():
            if prop_name == "verb":
                continue
            properties[prop_name] = prop_def

        # Handle allOf (used by vendor-specific s2s verbs that extend llm-base)
        for entry in schema.get("allOf", []):
            if "properties" in entry:
                for prop_name, prop_def in entry["properties"].items():
                    if prop_name == "verb":
                        continue
                    properties[prop_name] = prop_def

        schemas[spec_name] = {
            "properties": properties,
            "required": schema.get("required", []),
        }

    return schemas


_SPECS: dict[str, Any] = _load_schemas()


# ── Method factory ──────────────────────────────────────────────────

def _make_verb_method(verb_def: VerbDef, spec: dict[str, Any]) -> Any:
    """Create a verb method that routes through the generated pydantic model.

    The returned method accepts either a positional ``Model`` / ``dict``
    argument or keyword arguments matching the verb's schema. The payload
    is validated via the model (raising ``ValidationError`` on typos,
    wrong types, or cross-field rule violations) then dumped with
    ``mode='json', by_alias=True, exclude_none=True`` to produce the exact
    wire format jambonz expects.

    Each method also carries a real ``inspect.Signature`` derived from the
    verb schema, so IDEs show kwargs-style hints. For richer hints, users
    should pass the model classes directly (``session.gather(Gather(...))``).
    """
    properties = spec.get("properties", {})
    required = set(spec.get("required", []))
    json_verb = verb_def.json_verb
    inject = dict(verb_def.inject)  # copy; never mutated but defensive
    model_cls = verb_model(json_verb)

    def verb_method(
        self: VerbBuilder,
        arg: Any = None,
        /,
        **kwargs: Any,
    ) -> Self:
        if arg is not None and kwargs:
            raise TypeError(
                f"{verb_def.method_name}() takes either a model/dict or keyword "
                "arguments, not both"
            )

        if model_cls is not None and isinstance(arg, model_cls):
            data = arg.model_dump(mode="json", by_alias=True, exclude_none=True)
        else:
            # Build a payload dict from arg (if a dict) or kwargs, then merge
            # the registry's injected fields and coerce ``from_`` → ``from``.
            if isinstance(arg, dict):
                payload: dict[str, Any] = dict(arg)
            elif arg is None:
                payload = {}
            else:
                raise TypeError(
                    f"{verb_def.method_name}() expected a {model_cls.__name__ if model_cls else 'dict'} "
                    f"or dict, got {type(arg).__name__}"
                )

            for key, value in kwargs.items():
                if value is None:
                    continue
                payload["from" if key == "from_" else key] = value

            # Inject verb-registry defaults (e.g. vendor for vendor-specific
            # shortcuts) if not already set by the caller.
            for key, value in inject.items():
                payload.setdefault(key, value)

            if model_cls is not None:
                try:
                    model = model_cls.model_validate(payload)
                except ValidationError as exc:
                    raise exc
                data = model.model_dump(mode="json", by_alias=True, exclude_none=True)
            else:
                # Fallback when no generated model exists (e.g. fresh checkout
                # before scripts/regen_models.py has run). Preserve legacy
                # behavior: raw dict assembly with the verb tag.
                data = {"verb": json_verb, **payload}

        self._verbs.append(data)  # type: ignore[arg-type]
        return self

    # ── Build inspect.Signature with typed keyword-only params ──────
    # The first param is a positional-only model/dict. Subsequent params
    # mirror the schema's top-level properties for kwargs-style autocomplete.
    params = [
        inspect.Parameter("self", inspect.Parameter.POSITIONAL_ONLY),
        inspect.Parameter(
            "arg",
            inspect.Parameter.POSITIONAL_ONLY,
            default=None,
            annotation=Union[model_cls, dict, None] if model_cls else Union[dict, None],
        ),
    ]
    annotations: dict[str, Any] = {"arg": Union[model_cls, dict, None] if model_cls else Union[dict, None]}

    for prop_name, prop_spec in properties.items():
        py_name = "from_" if prop_name == "from" else prop_name
        py_type = _resolve_type(prop_spec)
        params.append(inspect.Parameter(
            py_name,
            inspect.Parameter.KEYWORD_ONLY,
            default=None,
            annotation=py_type,
        ))
        annotations[py_name] = py_type

    # Add **kwargs for forward compatibility
    params.append(inspect.Parameter("kwargs", inspect.Parameter.VAR_KEYWORD))
    annotations["return"] = Self

    verb_method.__signature__ = inspect.Signature(params)
    verb_method.__annotations__ = annotations

    # ── Build docstring ─────────────────────────────────────────────
    doc_lines = [verb_def.doc, ""]
    if required:
        doc_lines.append(f"Required: {', '.join(sorted(required))}")
        doc_lines.append("")
    doc_lines.append("Args:")
    for prop_name, prop_spec in properties.items():
        py_name = "from_" if prop_name == "from" else prop_name
        py_type_str = _python_type_str(prop_spec)
        req_marker = " **(required)**" if prop_name in required else ""
        doc_lines.append(f"    {py_name} ({py_type_str}):{req_marker}")
    doc_lines.append("")
    doc_lines.append("Returns:")
    doc_lines.append("    self for chaining.")

    verb_method.__doc__ = "\n".join(doc_lines)
    verb_method.__name__ = verb_def.method_name
    verb_method.__qualname__ = f"VerbBuilder.{verb_def.method_name}"

    return verb_method


# ── VerbBuilder class ───────────────────────────────────────────────

class VerbBuilder:
    """Builds an ordered list of jambonz verbs using a fluent API.

    All verb methods are auto-generated from JSON Schema files and accept
    keyword arguments matching the verb's specification. Methods return
    ``self`` for chaining.

    Example::

        builder = VerbBuilder()
        verbs = (
            builder
            .say(text="Hello!")
            .pause(length=1)
            .gather(input=["speech"], actionHook="/result", timeout=10)
            .hangup()
            .to_list()
        )
    """

    def __init__(self) -> None:
        self._verbs: list[AnyVerb] = []

    def to_list(self) -> list[AnyVerb]:
        """Return the verb list and reset the builder."""
        verbs = list(self._verbs)
        self._verbs = []
        return verbs


# ── Attach generated methods to VerbBuilder ─────────────────────────

def _build_methods() -> None:
    """Generate and attach verb methods to VerbBuilder from schemas + registry."""
    for verb_def in VERB_DEFS:
        spec = _SPECS.get(verb_def.spec_name)
        if spec is None:
            logger.warning(
                "Schema for '%s' not found for method '%s' — skipping",
                verb_def.spec_name,
                verb_def.method_name,
            )
            continue
        method = _make_verb_method(verb_def, spec)
        setattr(VerbBuilder, verb_def.method_name, method)


_build_methods()
