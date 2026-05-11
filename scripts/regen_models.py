#!/usr/bin/env python3
"""Regenerate pydantic v2 models from bundled jambonz JSON Schemas.

Produces ``src/jambonz_sdk/_models/_generated/`` as a committed build
artifact. Re-run whenever ``src/jambonz_sdk/schema/`` changes (e.g. after
``scripts/sync_schema.py`` pulls a new upstream version).

Pipeline:

1. Mirror bundled schemas to a temp dir with bare filenames (no
   ``.schema.json`` suffix) so that the generator's ``$ref`` resolver —
   which follows the ``$id`` URL relative to the file — finds the target.
   Also create aliases for schemas whose ``$id`` uses a colon but whose
   filename uses a hyphen (``sip-decline`` → ``sip:decline``, etc).

2. Run ``datamodel-code-generator`` across the whole mirrored tree. This
   produces one Python module per schema with shared types emitted once
   and imported where needed.

3. Apply post-generation patches:
     - rewrite ``class Foo(BaseModel):`` → ``class Foo(JambonzModel):``
       so every model inherits the populate-by-name / serialize-by-alias /
       extra="forbid" defaults. Generated ``model_config = ConfigDict(
       extra="allow")`` overrides on individual classes are preserved
       (pydantic v2 merges model_config with the parent).
     - rewrite ``AnyUrl`` to ``str``. The schemas use ``format: uri`` on
       webhook fields but accept relative paths like ``/menu``, which
       ``pydantic.AnyUrl`` rejects. Upstream schemas should switch to
       ``format: uri-reference``; until then, relax the type.
     - wire nested ``dict[str, Any]`` fields to their proper models
       (``Gather.say`` → ``Say``, ``Gather.play`` → ``Play``,
       ``Agent.llm`` → ``Llm``). The schemas declare these as
       ``additionalProperties: true`` untyped objects but in practice
       they follow the corresponding verb's shape.
     - record the upstream schema version in ``__jambonz_schema_version__``.

4. Format the output with ``ruff format``.

Usage::

    # Install the codegen toolchain into your dev venv first:
    pip install 'datamodel-code-generator[http]'

    # Then regenerate:
    python scripts/regen_models.py
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCHEMA_DIR = ROOT / "src" / "jambonz_sdk" / "schema"
OUTPUT_DIR = ROOT / "src" / "jambonz_sdk" / "_models" / "_generated"
PUBLIC_VERBS_INIT = ROOT / "src" / "jambonz_sdk" / "verbs" / "__init__.py"
PUBLIC_COMPONENTS_INIT = ROOT / "src" / "jambonz_sdk" / "components" / "__init__.py"

# Schemas whose $id uses a colon (sip:decline) but whose filename on disk
# uses a hyphen (sip-decline). The generator's ref resolver needs the
# colon form to resolve refs like "verbs/sip:decline".
COLON_ID_ALIASES = {
    "verbs/sip-decline": "verbs/sip:decline",
    "verbs/sip-refer": "verbs/sip:refer",
    "verbs/sip-request": "verbs/sip:request",
    "verbs/rest_dial": "verbs/rest:dial",
}

# Nested untyped fields in specific verbs that should reference real
# models. Schema declares these as ``additionalProperties: true`` objects
# but in practice they follow the corresponding verb's shape.
#
# Format: (verb_module, class_name, field_name, target_module, target_class)
NESTED_OVERRIDES: list[tuple[str, str, str, str, str]] = [
    ("verbs/gather.py", "Gather", "say", ".say", "Say"),
    ("verbs/gather.py", "Gather", "play", ".play", "Play"),
    ("verbs/agent.py", "Agent", "llm", ".llm", "LLM"),
]

# Nested classes the re-export heuristic wouldn't pick up (because they
# live alongside a primary class in the same file) but that users need
# typed access to. Each entry is promoted into the public
# ``jambonz_sdk.components`` module so it imports alongside the other
# component types.
#
# Format: (module_path_relative_to_generated, class_name)
PROMOTE_TO_COMPONENTS: list[tuple[str, str]] = [
    ("_generated.verbs.agent", "McpServer"),
    ("_generated.verbs.agent", "BargeIn"),
]


# Cross-field validators appended to specific generated classes after
# codegen. These express rules that don't fit cleanly into JSON Schema.
# Each entry: (module_path, class_name, imports, validator_body).
# The validator body is appended verbatim into the class body; it must
# use ``self`` and return ``self``.
CLASS_VALIDATORS: list[tuple[str, str, str, str]] = [
    (
        "verbs/gather.py",
        "Gather",
        "from pydantic import model_validator",
        '''
    @model_validator(mode="after")
    def _check_digit_bounds(self) -> "Gather":
        """``numDigits`` is mutually exclusive with ``min/maxDigits``."""
        if self.num_digits is not None and (
            self.min_digits is not None or self.max_digits is not None
        ):
            raise ValueError(
                "numDigits cannot be combined with minDigits or maxDigits"
            )
        if (
            self.min_digits is not None
            and self.max_digits is not None
            and self.min_digits > self.max_digits
        ):
            raise ValueError("minDigits cannot exceed maxDigits")
        return self
''',
    ),
]


def mirror_schemas(mirror_dir: Path) -> None:
    """Copy ``*.schema.json`` files into ``mirror_dir`` with bare names."""
    schema_dir = mirror_dir / "schema"
    for subdir in ("verbs", "components", "callbacks"):
        src_sub = SCHEMA_DIR / subdir
        if not src_sub.is_dir():
            continue
        dst_sub = schema_dir / subdir
        dst_sub.mkdir(parents=True, exist_ok=True)
        for src in src_sub.glob("*.schema.json"):
            bare_name = src.name[: -len(".schema.json")]
            shutil.copy2(src, dst_sub / bare_name)

    # Root app schema
    root = SCHEMA_DIR / "jambonz-app.schema.json"
    if root.is_file():
        shutil.copy2(root, schema_dir / "jambonz-app")

    # Colon-named aliases for sip:* and rest:dial
    for src_rel, dst_rel in COLON_ID_ALIASES.items():
        src = schema_dir / src_rel
        if src.is_file():
            shutil.copy2(src, schema_dir / dst_rel)


def read_schema_version() -> str:
    """Read the pinned schema version from ``scripts/sync_schema.py``."""
    sync_script = ROOT / "scripts" / "sync_schema.py"
    for line in sync_script.read_text().splitlines():
        m = re.match(r'SCHEMA_VERSION\s*=\s*"([^"]+)"', line)
        if m:
            return m.group(1)
    return "unknown"


def run_codegen(input_dir: Path, output_dir: Path) -> None:
    """Invoke ``datamodel-codegen`` across the mirrored schema tree."""
    if output_dir.exists():
        shutil.rmtree(output_dir)
    cmd = [
        "datamodel-codegen",
        "--input", str(input_dir),
        "--input-file-type", "jsonschema",
        "--output", str(output_dir),
        "--output-model-type", "pydantic_v2.BaseModel",
        "--use-standard-collections",
        "--use-union-operator",
        "--target-python-version", "3.10",
        "--snake-case-field",
        "--use-schema-description",
        "--use-field-description",
        "--use-double-quotes",
        "--reuse-model",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stdout, file=sys.stderr)
        print(result.stderr, file=sys.stderr)
        raise SystemExit(f"datamodel-codegen failed with exit code {result.returncode}")


# Match lines like ``class Foo(BaseModel):`` or ``class Foo(BaseModel, ...):``.
_BASEMODEL_CLASS_RE = re.compile(r"^(class\s+\w+\()BaseModel(\s*[),])", re.MULTILINE)


def rewrite_basemodel_to_jambonz(source: str) -> str:
    """Replace ``BaseModel`` base class with ``JambonzModel`` and add import."""
    new_source, n = _BASEMODEL_CLASS_RE.subn(r"\1JambonzModel\2", source)
    if n == 0:
        return source

    # Drop ``BaseModel`` from the pydantic import line (keep other names).
    new_source = re.sub(
        r"^from pydantic import (.+)$",
        lambda m: _rewrite_pydantic_import(m.group(1), drop={"BaseModel"}),
        new_source,
        count=1,
        flags=re.MULTILINE,
    )

    # Work out the relative import path to jambonz_sdk._models.base.
    # Every generated file lives under _generated/ (optionally inside a
    # subdirectory like verbs/ or components/). From _generated/* we go
    # up one level to _models, then into base.
    # Insert the import just after the last existing ``from`` line so
    # ruff-format leaves it alone.
    lines = new_source.splitlines(keepends=True)
    import_line = "from jambonz_sdk._models.base import JambonzModel\n"
    insert_at = 0
    for i, line in enumerate(lines):
        if line.startswith(("from ", "import ")):
            insert_at = i + 1
    # Preserve a blank line between imports and code if present.
    lines.insert(insert_at, import_line)
    return "".join(lines)


def _rewrite_pydantic_import(import_list: str, drop: set[str]) -> str:
    names = [n.strip() for n in import_list.split(",") if n.strip()]
    names = [n for n in names if n not in drop]
    if not names:
        return ""  # caller's regex replaces the whole line; we emit empty
    return "from pydantic import " + ", ".join(names)


def rewrite_field_default_kwarg(source: str) -> str:
    """Rewrite ``Field(None, ...)`` → ``Field(default=None, ...)``.

    Pylance's dataclass_transform pass treats the *keyword* ``default=`` as
    the authoritative default for optional-ness. When the generator emits
    ``Field(None, alias="x")`` Pylance can't always tell the field has a
    default and flags it as missing at call sites like
    ``Synthesizer(vendor="aws")``. Naming the kwarg fixes this without
    changing runtime behavior (pydantic accepts either form).

    Rewrites literal defaults (``None``, ``True``, ``False``, numbers,
    quoted strings) and the required-sentinel ``...``. Leaves complex
    expressions alone.
    """
    # Capture ``Field(`` followed by a literal default, followed by a
    # comma or closing paren. Do NOT rewrite the required sentinel
    # ``Field(...)`` — Pylance recognizes that as a no-default required
    # field, but treats ``Field(default=...)`` as optional. Optional
    # defaults (None, True, False, numbers, strings) are the ones that
    # need the explicit kwarg to be seen as having a default.
    default_literal = r"(?:None|True|False|-?\d+(?:\.\d+)?|\"[^\"]*\"|'[^']*')"
    pattern = re.compile(rf"\bField\(\s*({default_literal})(\s*[,)])")
    return pattern.sub(r"Field(default=\1\2", source)


def rewrite_anyurl_to_str(source: str) -> str:
    """Replace ``AnyUrl`` uses with ``str`` and drop the import."""
    if "AnyUrl" not in source:
        return source
    source = re.sub(r"\bAnyUrl\b", "str", source)
    # Clean up the import — AnyUrl became "str" literally in the import
    # list, which isn't valid; drop it.
    source = re.sub(
        r"^from pydantic import (.+)$",
        lambda m: _rewrite_pydantic_import(m.group(1), drop={"str"}),
        source,
        count=1,
        flags=re.MULTILINE,
    )
    # Collapse any blank "from pydantic import" lines produced above.
    source = re.sub(r"^from pydantic import\s*\n", "", source, flags=re.MULTILINE)
    return source


def apply_class_validators(output_dir: Path) -> None:
    """Append cross-field validator bodies to specific generated classes."""
    for rel_path, class_name, import_line, body in CLASS_VALIDATORS:
        path = output_dir / rel_path
        if not path.is_file():
            print(f"  warning: validator target {rel_path} missing — skipping")
            continue
        source = path.read_text()

        if import_line and import_line not in source:
            lines = source.splitlines(keepends=True)
            insert_at = 0
            for i, line in enumerate(lines):
                if line.startswith(("from ", "import ")):
                    insert_at = i + 1
            lines.insert(insert_at, import_line + "\n")
            source = "".join(lines)

        # Append the validator body at the end of the target class. The
        # class body runs to the end of file or the next top-level class.
        class_start = source.find(f"class {class_name}(")
        if class_start < 0:
            print(f"  warning: class {class_name} not found in {rel_path}")
            continue
        next_class = re.search(
            r"^class\s+\w+\(", source[class_start + 1:], re.MULTILINE
        )
        class_end = (
            class_start + 1 + next_class.start() if next_class else len(source)
        )
        # Strip trailing whitespace/newlines off the class body before
        # appending so ruff-format produces clean output.
        class_body = source[class_start:class_end].rstrip()
        source = source[:class_start] + class_body + body + source[class_end:]
        path.write_text(source)


def apply_nested_overrides(output_dir: Path) -> None:
    """Rewrite specific ``dict[str, Any]`` fields to reference real models."""
    for rel_path, class_name, field_name, target_module, target_class in NESTED_OVERRIDES:
        path = output_dir / rel_path
        if not path.is_file():
            print(f"  warning: nested-override target {rel_path} missing — skipping")
            continue
        source = path.read_text()

        # Find the target class body and rewrite the field annotation in place.
        # Pattern matches either "field: dict[str, Any]" or
        # "field: dict[str, Any] | None = ...".
        field_re = re.compile(
            rf"(^\s*{field_name}:\s*)dict\[str,\s*Any\](.*)$",
            re.MULTILINE,
        )
        class_start = source.find(f"class {class_name}(")
        if class_start < 0:
            print(f"  warning: class {class_name} not found in {rel_path}")
            continue
        # Apply the regex only to the class body (from class_start to end of file
        # or next top-level class).
        next_class = re.search(r"^class\s+\w+\(", source[class_start + 1:], re.MULTILINE)
        class_end = class_start + 1 + (next_class.start() if next_class else len(source))

        head, body, tail = source[:class_start], source[class_start:class_end], source[class_end:]
        new_body, n = field_re.subn(rf"\g<1>{target_class}\g<2>", body)
        if n == 0:
            print(f"  warning: field {class_name}.{field_name} not found to override")
            continue

        # Add the import at the module top (before the first class definition).
        import_line = f"from {target_module} import {target_class}\n"
        if import_line not in head:
            # Insert after the last existing import line in head.
            head_lines = head.splitlines(keepends=True)
            insert_at = 0
            for i, line in enumerate(head_lines):
                if line.startswith(("from ", "import ")):
                    insert_at = i + 1
            head_lines.insert(insert_at, import_line)
            head = "".join(head_lines)

        path.write_text(head + new_body + tail)


def postprocess_file(path: Path) -> None:
    source = path.read_text()
    source = rewrite_anyurl_to_str(source)
    source = rewrite_basemodel_to_jambonz(source)
    source = rewrite_field_default_kwarg(source)
    # Drop any now-empty ``from pydantic import`` lines produced by the
    # rewrites above (happens when BaseModel or AnyUrl was the sole import).
    source = re.sub(r"^from pydantic import\s*\n", "", source, flags=re.MULTILINE)
    path.write_text(source)


def write_public_reexports(output_dir: Path) -> None:
    """Emit user-facing ``jambonz_sdk.verbs`` / ``.components`` packages.

    - ``verbs/`` re-exports the one top-level class per file in
      ``_generated/verbs/`` that is named after the verb (e.g. ``Gather``,
      ``OpenaiS2S``). Files with numeric-suffixed internal class names
      (``TurnDetection1``) skip those since they're not meant to be a
      user-facing API.
    - ``components/`` re-exports the one top-level class per file in
      ``_generated/components/`` named after the schema (e.g.
      ``Recognizer``). Per-verb helper types (``Auth``, ``Method``) do
      not make it into the public surface because their names aren't
      globally unique.
    """
    # Regex finds top-level classes with their first base class name.
    class_re = re.compile(r"^class\s+(\w+)\(([\w\.]+)", re.MULTILINE)

    def _primary_class_of(path: Path, source: str) -> str | None:
        """Pick the one class in a module intended as the public surface.

        Prefers a class whose name matches the file's stem in CapWords
        (``actionHook`` → ``ActionHook``, ``sip_decline`` → ``SipDecline``).
        Falls back to the last model-class declared in the file.
        """
        stem = path.stem
        # Collect every model/root class declared in the module.
        keep_bases = ("JambonzModel", "LlmBaseProperties")
        classes: list[str] = []
        for name, base in class_re.findall(source):
            if base in keep_bases or base.startswith("RootModel"):
                classes.append(name)
        if not classes:
            return None

        cap_variants = {
            _to_cap(stem),
            _to_cap(stem).upper(),
            stem.upper(),
            stem.replace("_", "").upper(),
        }
        for name in classes:
            if name in cap_variants:
                return name
        # Fall back to the last class; the generator puts the outer
        # public class after its inner helpers.
        return classes[-1]

    verb_lines: list[tuple[str, str]] = []
    component_lines: list[tuple[str, str]] = []

    verbs_dir = output_dir / "verbs"
    for path in sorted(verbs_dir.glob("*.py")):
        if path.name == "__init__.py":
            continue
        source = path.read_text()
        primary = _primary_class_of(path, source)
        if not primary:
            continue
        module_dotted = f"jambonz_sdk._models._generated.verbs.{path.stem}"
        verb_lines.append((primary, module_dotted))

    components_dir = output_dir / "components"
    for path in sorted(components_dir.glob("*.py")):
        if path.name == "__init__.py":
            continue
        source = path.read_text()
        primary = _primary_class_of(path, source)
        if not primary:
            continue
        module_dotted = f"jambonz_sdk._models._generated.components.{path.stem}"
        component_lines.append((primary, module_dotted))

    # Explicit promotions for nested helper classes users need typed access
    # to (e.g. ``McpServer`` inside ``verbs/agent.py``).
    for rel_module, class_name in PROMOTE_TO_COMPONENTS:
        module_dotted = f"jambonz_sdk._models.{rel_module}"
        component_lines.append((class_name, module_dotted))

    PUBLIC_VERBS_INIT.parent.mkdir(parents=True, exist_ok=True)
    PUBLIC_VERBS_INIT.write_text(_render_reexport_module("verbs", verb_lines))

    PUBLIC_COMPONENTS_INIT.parent.mkdir(parents=True, exist_ok=True)
    PUBLIC_COMPONENTS_INIT.write_text(_render_reexport_module("components", component_lines))


def _to_cap(stem: str) -> str:
    """Convert a snake/kebab module stem into CapWords form."""
    parts = re.split(r"[_\-]+", stem)
    return "".join(p[:1].upper() + p[1:] for p in parts if p)


def _render_reexport_module(kind_label: str, exports: list[tuple[str, str]]) -> str:
    seen: dict[str, str] = {}
    for cls, mod in exports:
        seen.setdefault(cls, mod)
    lines = [
        f'"""Public re-exports of generated jambonz {kind_label} models.',
        "",
        "Auto-generated by ``scripts/regen_models.py`` — do not edit by hand.",
        "",
        "Typical usage::",
        "",
        f"    from jambonz_sdk.{kind_label} import Gather, Say",
        '"""',
        "",
        "from __future__ import annotations",
        "",
    ]
    for cls in sorted(seen):
        lines.append(f"from {seen[cls]} import {cls}")
    lines.append("")
    lines.append("__all__ = [")
    for cls in sorted(seen):
        lines.append(f'    "{cls}",')
    lines.append("]")
    lines.append("")
    return "\n".join(lines)


def write_schema_version(output_dir: Path, version: str) -> None:
    init = output_dir / "__init__.py"
    if not init.is_file():
        return
    text = init.read_text()
    marker = f'__jambonz_schema_version__ = "{version}"\n'
    if "__jambonz_schema_version__" in text:
        text = re.sub(
            r'__jambonz_schema_version__\s*=\s*".*?"\n',
            marker,
            text,
        )
    else:
        text = marker + text
    init.write_text(text)


def ruff_format(output_dir: Path) -> None:
    subprocess.run(
        ["ruff", "format", str(output_dir)],
        check=False,
        capture_output=True,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Regenerate pydantic models from JSON Schemas.")
    parser.add_argument(
        "--keep-mirror",
        action="store_true",
        help="Keep the temp mirror dir for debugging (normally cleaned up).",
    )
    args = parser.parse_args()

    version = read_schema_version()
    print(f"Regenerating models for schema version {version}")

    tmp = Path(tempfile.mkdtemp(prefix="jambonz-schema-mirror-"))
    try:
        mirror_schemas(tmp)
        print(f"  mirrored schemas → {tmp / 'schema'}")

        run_codegen(tmp / "schema", OUTPUT_DIR)
        print(f"  generated → {OUTPUT_DIR.relative_to(ROOT)}")

        # Every .py file gets BaseModel → JambonzModel and AnyUrl → str.
        py_files = list(OUTPUT_DIR.rglob("*.py"))
        for path in py_files:
            postprocess_file(path)
        print(f"  post-processed {len(py_files)} files")

        apply_nested_overrides(OUTPUT_DIR)
        print("  applied nested-object overrides")

        apply_class_validators(OUTPUT_DIR)
        print("  applied cross-field validators")

        write_schema_version(OUTPUT_DIR, version)

        write_public_reexports(OUTPUT_DIR)
        print(
            f"  wrote public re-exports → "
            f"{PUBLIC_VERBS_INIT.relative_to(ROOT)}, "
            f"{PUBLIC_COMPONENTS_INIT.relative_to(ROOT)}"
        )

        ruff_format(OUTPUT_DIR)
        ruff_format(PUBLIC_VERBS_INIT.parent)
        ruff_format(PUBLIC_COMPONENTS_INIT.parent)
        print("  formatted with ruff")
    finally:
        if args.keep_mirror:
            print(f"  (kept mirror at {tmp})")
        else:
            shutil.rmtree(tmp, ignore_errors=True)

    print("Done.")


if __name__ == "__main__":
    main()
