"""Shared base class for all jambonz verb/component pydantic models.

Every generated model inherits from ``JambonzModel``. The regen script
rewrites ``pydantic.BaseModel`` imports to point at this class so the
generated output picks up the shared configuration automatically.

Configuration:

- ``populate_by_name=True`` — constructors accept either the Python field
  name (``action_hook``) or the camelCase alias (``actionHook``). This is
  what lets users pass raw dicts (camelCase or snake_case) and have them
  coerce into typed models.
- ``serialize_by_alias=True`` — ``model_dump()`` emits camelCase, matching
  the on-the-wire format jambonz expects.
- ``extra="forbid"`` — unknown fields raise at construction time, so typos
  fail fast instead of silently hitting the jambonz server. Per-model
  overrides (e.g. ``BargeIn``, ``LlmOptions``) use ``extra="allow"`` when
  the schema declares ``additionalProperties: true``; the regen script
  reads this from the schema and emits the override per class.

Per-field camelCase aliases are emitted by the code generator rather than
derived from an ``alias_generator`` — this is more robust for fields where
the mapping isn't a clean snake→camel (e.g. ``naicsCode``).
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class JambonzModel(BaseModel):
    """Base for all jambonz verb and component models."""

    model_config = ConfigDict(
        populate_by_name=True,
        serialize_by_alias=True,
        extra="forbid",
        # Store enum fields as their underlying str/int value so that
        # ``model_dump(mode='json')`` emits the value directly without
        # emitting "expected enum" serializer warnings when a caller
        # passes the raw value (``method='POST'``) via a dict or kwargs.
        use_enum_values=True,
    )
