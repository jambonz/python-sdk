"""HMAC-SHA256 webhook signature verification.

jambonz signs webhook requests with the header:
    Jambonz-Signature: t=<timestamp>,v1=<signature>

The signature is computed as:
    HMAC-SHA256(secret, timestamp + "." + raw_body)
"""

from __future__ import annotations

import hashlib
import hmac
import time

DEFAULT_TOLERANCE = 300  # 5 minutes


def verify_signature(
    payload: bytes,
    signature_header: str,
    secret: str,
    tolerance: int = DEFAULT_TOLERANCE,
) -> bool:
    """Verify a jambonz webhook signature.

    Args:
        payload: Raw request body bytes.
        signature_header: Value of the ``Jambonz-Signature`` header.
        secret: The webhook signing secret.
        tolerance: Maximum age in seconds for the timestamp (default 300).

    Returns:
        True if the signature is valid.

    Raises:
        ValueError: If the signature header is malformed, the signature
            doesn't match, or the timestamp is outside the tolerance window.
    """
    parts: dict[str, str] = {}
    for item in signature_header.split(","):
        key, _, value = item.strip().partition("=")
        parts[key] = value

    timestamp_str = parts.get("t")
    sig = parts.get("v1")

    if not timestamp_str or not sig:
        raise ValueError("Invalid Jambonz-Signature header format")

    try:
        timestamp = int(timestamp_str)
    except (ValueError, TypeError) as exc:
        raise ValueError("Invalid timestamp in Jambonz-Signature header") from exc

    if tolerance > 0:
        age = int(time.time()) - timestamp
        if age > tolerance:
            raise ValueError(
                f"Signature timestamp too old: {age}s > {tolerance}s tolerance"
            )

    signed_payload = f"{timestamp}.".encode() + payload
    expected = hmac.new(
        secret.encode(),
        signed_payload,
        hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(expected, sig):
        raise ValueError("Signature verification failed")

    return True
