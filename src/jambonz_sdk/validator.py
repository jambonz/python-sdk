"""JSON Schema validation for jambonz verb applications.

Uses the ``jsonschema`` library to validate verb dicts against the
bundled JSON Schema files from @jambonz/schema.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
from referencing import Registry, Resource


def _load_schema(path: Path) -> dict[str, Any]:
    with path.open() as f:
        return json.load(f)


class JambonzValidator:
    """Validates jambonz verb dicts against JSON Schema (draft 2020-12).

    Schemas are loaded once at construction time from the bundled
    ``schema/`` directory.

    Example::

        validator = JambonzValidator()
        errors = validator.validate_verb({"verb": "say", "text": "Hello"})
        assert errors == []
    """

    def __init__(self, schema_dir: str | Path | None = None) -> None:
        self._schema_dir = Path(schema_dir) if schema_dir else (
            Path(__file__).resolve().parent / "schema"
        )

        # Load the root app schema
        app_schema_path = self._schema_dir / "jambonz-app.schema.json"
        self._app_schema = _load_schema(app_schema_path)

        # Build a registry of all schemas for $ref resolution
        resources: list[tuple[str, Resource]] = []  # type: ignore[type-arg]
        self._store: dict[str, dict[str, Any]] = {}

        for subdir in ("components", "callbacks", "verbs"):
            subdir_path = self._schema_dir / subdir
            if not subdir_path.is_dir():
                continue
            for schema_file in subdir_path.glob("*.schema.json"):
                schema = _load_schema(schema_file)
                if "$id" in schema:
                    self._store[schema["$id"]] = schema
                    resources.append((
                        schema["$id"],
                        Resource.from_contents(schema),  # type: ignore[arg-type]
                    ))

        # Add the root schema
        self._store[self._app_schema["$id"]] = self._app_schema
        resources.append((
            self._app_schema["$id"],
            Resource.from_contents(self._app_schema),  # type: ignore[arg-type]
        ))

        self._registry: Registry = Registry().with_resources(resources)  # type: ignore[assignment]

        # Pre-compile the app validator
        self._app_validator = Draft202012Validator(
            self._app_schema,
            registry=self._registry,
        )

    def validate_app(self, verbs: list[dict[str, Any]]) -> list[str]:
        """Validate a complete verb array against the root app schema.

        Returns a list of error messages (empty if valid).
        """
        errors: list[str] = []
        for error in self._app_validator.iter_errors(verbs):
            path = "/".join(str(p) for p in error.absolute_path) or "/"
            errors.append(f"{path}: {error.message}")
        return errors

    def validate_verb(self, verb: dict[str, Any]) -> list[str]:
        """Validate a single verb dict against its schema.

        Returns a list of error messages (empty if valid).
        """
        verb_name = verb.get("verb")
        if not verb_name:
            return ["missing 'verb' property"]

        # Look up the verb schema by $id
        schema_id = f"https://jambonz.org/schema/verbs/{verb_name}"
        schema = self._store.get(schema_id)
        if schema is None:
            return [f"unknown verb: {verb_name}"]

        validator = Draft202012Validator(schema, registry=self._registry)
        errors: list[str] = []
        for error in validator.iter_errors(verb):
            path = "/".join(str(p) for p in error.absolute_path) or "/"
            errors.append(f"{path}: {error.message}")
        return errors
