"""Middleware utilities for webhook applications.

These are framework-agnostic helpers. For framework-specific integration,
wrap these in your framework's middleware pattern.
"""

from __future__ import annotations

import json
from typing import Any

from jambonz_sdk._signature import verify_signature


def verify_signature_middleware(
    payload: bytes,
    signature_header: str | None,
    secret: str,
    tolerance: int = 300,
) -> bool:
    """Verify a jambonz webhook signature.

    Args:
        payload: Raw request body bytes.
        signature_header: Value of the ``Jambonz-Signature`` header.
        secret: The webhook signing secret.
        tolerance: Maximum age in seconds for the timestamp.

    Returns:
        True if valid.

    Raises:
        ValueError: If verification fails.
    """
    if not signature_header:
        raise ValueError("Missing Jambonz-Signature header")
    return verify_signature(payload, signature_header, secret, tolerance)


def env_vars_middleware(env_vars: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """Build the OPTIONS response body for environment variable discovery.

    jambonz sends an OPTIONS request to discover configurable parameters.
    Return this dict as the JSON response body for OPTIONS requests.

    Args:
        env_vars: Environment variable schema. Each key is a parameter name,
            the value describes type, description, default, etc.

    Returns:
        A dict suitable for JSON serialization as the OPTIONS response body.

    Example::

        env_schema = {
            "API_KEY": {"type": "string", "description": "API key", "required": True, "obscure": True},
            "LANGUAGE": {"type": "string", "description": "TTS language", "default": "en-US"},
        }

        # In your OPTIONS handler:
        return json.dumps(env_vars_middleware(env_schema))
    """
    return {"env": json.loads(json.dumps(env_vars))}
