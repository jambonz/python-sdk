"""Pydantic v2 models for jambonz verbs and components.

This package contains:

- ``base.JambonzModel`` — hand-written base class with alias/serialization
  config inherited by every generated model.
- ``_generated/`` — models generated from @jambonz/schema JSON Schema files
  by ``scripts/regen_models.py``. Committed to the repo but never edited by
  hand.
- ``_patches/`` — small hand-written supplements (cross-field validators,
  nested-override tables, etc.) applied either by the regen script or
  imported directly.

Users typically import the public names re-exported at the top level::

    from jambonz_sdk.verbs import Gather, Say
    from jambonz_sdk.components import Recognizer, Synthesizer
"""

from __future__ import annotations

from jambonz_sdk._models.base import JambonzModel

__all__ = ["JambonzModel"]
