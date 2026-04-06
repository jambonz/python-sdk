"""Spec-driven tests for WebhookResponse and webhook middleware.

Tests validate:
- WebhookResponse produces JSON arrays matching jambonz webhook contract
- Signature verification follows jambonz HMAC-SHA256 spec:
  Header: Jambonz-Signature: t=<timestamp>,v1=<HMAC-SHA256(secret, timestamp.body)>
- Env vars middleware returns correct OPTIONS response format
"""

import hashlib
import hmac
import json
import time

import pytest

from jambonz_sdk._signature import verify_signature
from jambonz_sdk.webhook import WebhookResponse, env_vars_middleware, verify_signature_middleware

# ── WebhookResponse: must produce valid jambonz verb arrays ─────────

class TestWebhookResponseContract:
    """WebhookResponse.to_json() must return a list of verb dicts
    that jambonz can parse and execute."""

    def test_to_json_returns_list(self):
        resp = WebhookResponse()
        resp.say(text="Hello")
        result = resp.to_json()
        assert isinstance(result, list)

    def test_each_item_has_verb_key(self):
        resp = WebhookResponse()
        resp.say(text="Hello").pause(length=1).hangup()
        for item in resp.to_json():
            assert "verb" in item

    def test_to_json_resets_state(self):
        """After to_json(), builder is empty for the next response."""
        resp = WebhookResponse()
        resp.say(text="Hello")
        resp.to_json()
        assert resp.to_json() == []

    def test_to_json_string_is_valid_json(self):
        resp = WebhookResponse()
        resp.say(text="Hello").hangup()
        parsed = json.loads(resp.to_json_string())
        assert isinstance(parsed, list)
        assert len(parsed) == 2

    def test_inherits_all_verb_methods(self):
        """WebhookResponse must have the same verb methods as VerbBuilder."""
        from jambonz_sdk.verb_registry import VERB_DEFS
        for verb_def in VERB_DEFS:
            assert hasattr(WebhookResponse, verb_def.method_name)

    def test_chaining_returns_self(self):
        resp = WebhookResponse()
        assert resp.say(text="a") is resp

    def test_complete_ivr_response(self):
        """A complete IVR response must serialize correctly."""
        resp = WebhookResponse()
        resp.say(text="Welcome.").gather(
            input=["speech", "digits"],
            actionHook="/menu",
            numDigits=1,
            timeout=10,
            say={"text": "Press 1 for sales."},
        ).say(text="No input.").hangup()
        verbs = resp.to_json()
        assert len(verbs) == 4
        assert verbs[0]["verb"] == "say"
        assert verbs[1]["verb"] == "gather"
        assert verbs[1]["actionHook"] == "/menu"
        assert verbs[3]["verb"] == "hangup"


# ── Signature verification: jambonz HMAC-SHA256 protocol ────────────

class TestSignatureVerification:
    """jambonz signs webhooks with:
    Header: Jambonz-Signature: t=<unix_timestamp>,v1=<hex_hmac_sha256>
    Signature = HMAC-SHA256(secret, "<timestamp>.<body_bytes>")
    """

    def _sign(self, payload: bytes, secret: str, timestamp: int | None = None) -> str:
        ts = timestamp or int(time.time())
        signed = f"{ts}.".encode() + payload
        sig = hmac.new(secret.encode(), signed, hashlib.sha256).hexdigest()
        return f"t={ts},v1={sig}"

    def test_valid_signature_accepted(self):
        payload = b'{"call_sid":"abc123"}'
        secret = "test-secret"
        header = self._sign(payload, secret)
        assert verify_signature(payload, header, secret) is True

    def test_wrong_secret_rejected(self):
        payload = b'{"call_sid":"abc123"}'
        header = self._sign(payload, "correct-secret")
        with pytest.raises(ValueError, match="Signature verification failed"):
            verify_signature(payload, header, "wrong-secret")

    def test_tampered_body_rejected(self):
        payload = b'{"call_sid":"abc123"}'
        header = self._sign(payload, "secret")
        with pytest.raises(ValueError, match="Signature verification failed"):
            verify_signature(b'{"call_sid":"TAMPERED"}', header, "secret")

    def test_expired_timestamp_rejected(self):
        payload = b"test"
        old_ts = int(time.time()) - 600
        header = self._sign(payload, "secret", old_ts)
        with pytest.raises(ValueError, match="too old"):
            verify_signature(payload, header, "secret", tolerance=300)

    def test_custom_tolerance(self):
        payload = b"test"
        old_ts = int(time.time()) - 400
        header = self._sign(payload, "secret", old_ts)
        # Fails with 300s tolerance
        with pytest.raises(ValueError):
            verify_signature(payload, header, "secret", tolerance=300)
        # Passes with 600s tolerance
        assert verify_signature(payload, header, "secret", tolerance=600) is True

    def test_zero_tolerance_disables_time_check(self):
        payload = b"test"
        header = self._sign(payload, "secret", timestamp=1000)
        assert verify_signature(payload, header, "secret", tolerance=0) is True

    def test_malformed_header_missing_t(self):
        with pytest.raises(ValueError, match="Invalid"):
            verify_signature(b"test", "v1=abc", "secret")

    def test_malformed_header_missing_v1(self):
        with pytest.raises(ValueError, match="Invalid"):
            verify_signature(b"test", "t=12345", "secret")

    def test_malformed_header_garbage(self):
        with pytest.raises(ValueError, match="Invalid"):
            verify_signature(b"test", "garbage", "secret")

    def test_non_integer_timestamp(self):
        with pytest.raises(ValueError, match="Invalid timestamp"):
            verify_signature(b"test", "t=notanumber,v1=abc", "secret")


class TestVerifySignatureMiddleware:
    """The middleware wrapper must enforce header presence."""

    def test_missing_header_raises(self):
        with pytest.raises(ValueError, match="Missing"):
            verify_signature_middleware(b"test", None, "secret")

    def test_empty_header_raises(self):
        with pytest.raises(ValueError, match="Missing"):
            verify_signature_middleware(b"test", "", "secret")

    def test_valid_header_passes(self):
        payload = b"test"
        secret = "secret"
        ts = int(time.time())
        signed = f"{ts}.".encode() + payload
        sig = hmac.new(secret.encode(), signed, hashlib.sha256).hexdigest()
        assert verify_signature_middleware(payload, f"t={ts},v1={sig}", secret) is True


# ── Env vars middleware: OPTIONS response format ────────────────────

class TestEnvVarsMiddleware:
    """jambonz portal sends OPTIONS to discover configurable env vars.
    Response must be: {"env": {<schema>}}"""

    def test_returns_env_wrapper(self):
        schema = {"API_KEY": {"type": "string", "required": True}}
        result = env_vars_middleware(schema)
        assert "env" in result

    def test_preserves_schema_structure(self):
        schema = {
            "API_KEY": {"type": "string", "description": "API key", "required": True, "obscure": True},
            "LANGUAGE": {"type": "string", "description": "Language", "default": "en-US", "enum": ["en-US", "es-ES"]},
            "MAX_RETRIES": {"type": "number", "description": "Max retries", "default": 3},
        }
        result = env_vars_middleware(schema)
        assert result["env"]["API_KEY"]["obscure"] is True
        assert result["env"]["LANGUAGE"]["enum"] == ["en-US", "es-ES"]
        assert result["env"]["MAX_RETRIES"]["default"] == 3

    def test_empty_schema(self):
        result = env_vars_middleware({})
        assert result == {"env": {}}
