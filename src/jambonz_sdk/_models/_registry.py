"""Lazy map from JSON verb name to its generated pydantic model class.

Scans the generated ``_models._generated.verbs`` package once and indexes
every class that declares a ``verb: Literal[...]`` field. The literal
default becomes the key; the class becomes the value.

Used by :mod:`jambonz_sdk.verb_builder` to route verb method calls through
their corresponding model for validation and serialization.
"""

from __future__ import annotations

import importlib
import logging
import pkgutil
from typing import Any

from pydantic import BaseModel

logger = logging.getLogger("jambonz_sdk._models._registry")

_cache: dict[str, type[BaseModel]] | None = None


def _build_registry() -> dict[str, type[BaseModel]]:
    try:
        from jambonz_sdk._models._generated import verbs as verbs_pkg
    except ImportError:
        logger.warning("generated verbs package not found — regen with scripts/regen_models.py")
        return {}

    registry: dict[str, type[BaseModel]] = {}
    for _, modname, _ in pkgutil.iter_modules(verbs_pkg.__path__):
        try:
            module = importlib.import_module(f"{verbs_pkg.__name__}.{modname}")
        except Exception as exc:  # noqa: BLE001 — gracefully skip broken modules
            logger.warning("failed to import %s: %s", modname, exc)
            continue
        for name, attr in vars(module).items():
            if not isinstance(attr, type) or not issubclass(attr, BaseModel):
                continue
            if attr.__module__ != module.__name__:
                continue  # skip re-exported classes from other modules
            verb_field: Any = attr.model_fields.get("verb")
            if verb_field is None:
                continue
            default = verb_field.default
            if isinstance(default, str):
                registry[default] = attr
    return registry


def verb_model(json_verb: str) -> type[BaseModel] | None:
    """Return the generated model class for a JSON verb name, or ``None``."""
    global _cache
    if _cache is None:
        _cache = _build_registry()
    return _cache.get(json_verb)


def all_verb_models() -> dict[str, type[BaseModel]]:
    """Return a copy of the full registry, keyed by JSON verb name."""
    global _cache
    if _cache is None:
        _cache = _build_registry()
    return dict(_cache)
