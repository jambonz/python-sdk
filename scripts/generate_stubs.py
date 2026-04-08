#!/usr/bin/env python3
"""Generate verb_builder.pyi stub file from JSON Schema + verb_registry.

This creates a .pyi type stub that IDEs (VS Code Pylance, PyCharm, mypy)
read for static type checking and autocomplete. Run this after syncing
the schema or updating verb_registry.py.

Usage:
    python scripts/generate_stubs.py
"""

import json
import sys
from pathlib import Path

# Add src to path so we can import the registry
SRC_DIR = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(SRC_DIR))

from jambonz_sdk.verb_registry import VERB_DEFS

SCHEMA_DIR = SRC_DIR / "jambonz_sdk" / "schema" / "verbs"
STUB_PATH = SRC_DIR / "jambonz_sdk" / "verb_builder.pyi"

# Maps JSON Schema type strings to Python type annotation strings for .pyi
TYPE_MAP = {
    "string": "str",
    "number": "int | float",
    "boolean": "bool",
    "object": "dict[str, Any]",
    "array": "list[Any]",
}


def resolve_type(spec_type) -> str:
    """Convert a JSON Schema type descriptor to a .pyi type string."""
    if isinstance(spec_type, str):
        if spec_type.startswith("#"):
            return "dict[str, Any]"
        if "|" in spec_type:
            parts = []
            for t in spec_type.split("|"):
                t = t.strip()
                if t.startswith("#"):
                    parts.append("dict[str, Any]")
                else:
                    parts.append(TYPE_MAP.get(t, "Any"))
            # Dedupe preserving order
            seen = set()
            unique = []
            for p in parts:
                if p not in seen:
                    seen.add(p)
                    unique.append(p)
            return " | ".join(unique)
        return TYPE_MAP.get(spec_type, "Any")
    if isinstance(spec_type, list):
        return "list[Any]"
    if isinstance(spec_type, dict):
        return TYPE_MAP.get(spec_type.get("type", ""), "Any")
    return "Any"


def _load_schemas() -> dict:
    """Load verb JSON Schemas from the bundled schema directory."""
    schemas: dict = {}
    for schema_file in sorted(SCHEMA_DIR.glob("*.schema.json")):
        with schema_file.open() as f:
            schema = json.load(f)
        schema_id = schema.get("$id", "")
        if schema_id:
            spec_name = schema_id.rsplit("/", 1)[-1]
        else:
            spec_name = schema_file.stem.replace(".schema", "")
        properties = {}
        for prop_name, prop_def in schema.get("properties", {}).items():
            if prop_name == "verb":
                continue
            properties[prop_name] = prop_def
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


def generate() -> str:
    specs = _load_schemas()

    lines = [
        '"""Auto-generated type stubs for VerbBuilder.',
        "",
        "DO NOT EDIT — regenerate with: python scripts/generate_stubs.py",
        '"""',
        "",
        "from typing import Any, Self",
        "",
        "from jambonz_sdk.types.verbs import AnyVerb",
        "",
        "class VerbBuilder:",
        "    _verbs: list[AnyVerb]",
        "",
        "    def __init__(self) -> None: ...",
        "    def to_list(self) -> list[AnyVerb]: ...",
    ]

    for verb_def in VERB_DEFS:
        spec = specs.get(verb_def.spec_name)
        if spec is None:
            continue

        properties = spec.get("properties", {})
        required = set(spec.get("required", []))

        # Build parameter list
        params = ["self"]
        for prop_name, prop_spec in properties.items():
            py_name = "from_" if prop_name == "from" else prop_name
            py_type = resolve_type(prop_spec)
            params.append(f"{py_name}: {py_type} = ...")

        # Add **kwargs for forward compatibility
        params.append("**kwargs: Any")

        param_str = ",\n        ".join(params)

        # Build docstring
        doc_lines = [f'        """{verb_def.doc}']
        if required:
            doc_lines.append("")
            doc_lines.append(f"        Required: {', '.join(sorted(required))}")
        doc_lines.append("")
        doc_lines.append("        Args:")
        for prop_name, prop_spec in properties.items():
            py_name = "from_" if prop_name == "from" else prop_name
            py_type = resolve_type(prop_spec)
            req = " (required)" if prop_name in required else ""
            doc_lines.append(f"            {py_name}: {py_type}{req}")
        doc_lines.append("")
        doc_lines.append("        Returns:")
        doc_lines.append("            self for chaining.")
        doc_lines.append('        """')

        lines.append("")
        lines.append(f"    def {verb_def.method_name}(")
        lines.append(f"        {param_str},")
        lines.append(f"    ) -> Self:")
        lines.extend(doc_lines)
        lines.append("        ...")

    lines.append("")
    return "\n".join(lines)


def main():
    stub = generate()
    STUB_PATH.write_text(stub)
    # Count methods
    method_count = sum(1 for line in stub.split("\n") if line.strip().startswith("def ") and line.strip() != "def __init__(self) -> None: ..." and line.strip() != "def to_list(self) -> list[AnyVerb]: ...")
    print(f"Generated {STUB_PATH} ({method_count} verb methods)")


if __name__ == "__main__":
    main()
