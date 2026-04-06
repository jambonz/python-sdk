"""VerbBuilder base class with auto-generated chainable verb methods.

Methods are generated at import time from ``specs.json`` + the verb registry.
When the spec changes, the SDK automatically picks up new parameters —
no manual method signatures to maintain.

Each generated method has a real ``inspect.Signature`` with typed parameters
so IDEs (VS Code, PyCharm) show proper autocomplete and type hints.
"""

from __future__ import annotations

import inspect
import json
import logging
from pathlib import Path
from typing import Any, Self, Union

from jambonz_sdk.types.verbs import AnyVerb
from jambonz_sdk.verb_registry import VERB_DEFS, VerbDef

logger = logging.getLogger("jambonz_sdk.verb_builder")

# ── Spec type → Python type mapping ────────────────────────────────
# Used for both docstrings (human-readable) and runtime annotations (IDE).

_TYPE_ANNOTATION_MAP: dict[str, type | object] = {
    "string": str,
    "number": Union[int, float],
    "boolean": bool,
    "object": dict,
    "array": list,
}


def _resolve_type(spec_type: Any) -> type | object:
    """Convert a specs.json type descriptor to a Python type annotation."""
    if isinstance(spec_type, str):
        if spec_type.startswith("#"):
            return dict
        if "|" in spec_type:
            parts = []
            for t in spec_type.split("|"):
                t = t.strip()
                if t.startswith("#"):
                    parts.append(dict)
                else:
                    resolved = _TYPE_ANNOTATION_MAP.get(t)
                    if resolved is not None:
                        if resolved is Union[int, float]:
                            parts.extend([int, float])
                        else:
                            parts.append(resolved)
                    else:
                        parts.append(Any)
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
        return _TYPE_ANNOTATION_MAP.get(spec_type, Any)
    if isinstance(spec_type, list):
        return list
    if isinstance(spec_type, dict):
        return _TYPE_ANNOTATION_MAP.get(spec_type.get("type", ""), Any)
    return Any


def _python_type_str(spec_type: Any) -> str:
    """Convert a specs.json type descriptor to a human-readable type string."""
    _str_map = {
        "string": "str",
        "number": "int | float",
        "boolean": "bool",
        "object": "dict[str, Any]",
        "array": "list[Any]",
    }
    if isinstance(spec_type, str):
        if spec_type.startswith("#"):
            return "dict[str, Any]"
        if "|" in spec_type:
            parts = [_str_map.get(t.strip(), "Any") if not t.strip().startswith("#") else "dict[str, Any]"
                     for t in spec_type.split("|")]
            return " | ".join(dict.fromkeys(parts))
        return _str_map.get(spec_type, "Any")
    if isinstance(spec_type, list):
        return "list[Any]"
    if isinstance(spec_type, dict):
        return _str_map.get(spec_type.get("type", ""), "Any")
    return "Any"


# ── Load specs ──────────────────────────────────────────────────────

def _load_specs() -> dict[str, Any]:
    """Load specs.json bundled alongside this package."""
    specs_path = Path(__file__).resolve().parent / "specs.json"
    with specs_path.open() as f:
        return json.load(f)


_SPECS: dict[str, Any] = _load_specs()


# ── Method factory ──────────────────────────────────────────────────

def _make_verb_method(verb_def: VerbDef, spec: dict[str, Any]) -> Any:
    """Create a verb method with a real typed signature from the spec.

    Each generated method has:
    - ``inspect.Signature`` with keyword-only parameters (default ``None``)
    - ``__annotations__`` with resolved Python types (not ``Any``)
    - Docstring with parameter types and required markers
    """
    properties = spec.get("properties", {})
    required = set(spec.get("required", []))
    json_verb = verb_def.json_verb
    inject = verb_def.inject

    def verb_method(self: VerbBuilder, **kwargs: Any) -> Self:
        data: dict[str, Any] = {}
        if inject:
            data.update(inject)
        for key, value in kwargs.items():
            if value is None:
                continue
            if key == "from_":
                data["from"] = value
            else:
                data[key] = value
        verb: dict[str, Any] = {"verb": json_verb, **data}
        self._verbs.append(verb)  # type: ignore[arg-type]
        return self

    # ── Build inspect.Signature with typed keyword-only params ──────
    params = [inspect.Parameter("self", inspect.Parameter.POSITIONAL_OR_KEYWORD)]
    annotations: dict[str, Any] = {}

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

    All verb methods are auto-generated from ``specs.json`` and accept
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
    """Generate and attach verb methods to VerbBuilder from specs + registry."""
    for verb_def in VERB_DEFS:
        spec = _SPECS.get(verb_def.spec_name)
        if spec is None:
            logger.warning(
                "Spec '%s' not found in specs.json for method '%s' — skipping",
                verb_def.spec_name,
                verb_def.method_name,
            )
            continue
        method = _make_verb_method(verb_def, spec)
        setattr(VerbBuilder, verb_def.method_name, method)


_build_methods()
