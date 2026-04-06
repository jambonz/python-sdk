"""Spec-driven tests for WsClient message routing.

Tests validate the jambonz WebSocket protocol:
- session:new → creates Session, emits 'session:new'
- session:redirect → emits 'session:redirect'
- verb:hook → dispatches to session event handler by hook name
- verb:hook with no handler → auto-replies with empty verbs
- Binary frames are ignored (audio protocol uses separate path)
- Invalid JSON is silently skipped
"""

import json
from unittest.mock import AsyncMock

import pytest

from jambonz_sdk.websocket.client import WsClient


def _make_ws(*messages) -> AsyncMock:
    """Create a mock WS that yields the given messages in order."""
    ws = AsyncMock()
    ws.send = AsyncMock()

    async def message_iter():
        for msg in messages:
            if isinstance(msg, bytes):
                yield msg
            else:
                yield json.dumps(msg)

    ws.__aiter__ = lambda self: message_iter()
    return ws


# ── session:new handling ────────────────────────────────────────────

class TestSessionNew:
    @pytest.mark.asyncio
    async def test_emits_session_new(self):
        sessions = []
        ws = _make_ws({
            "type": "session:new",
            "msgid": "msg-1",
            "data": {"call_sid": "call-123", "from": "+1", "to": "+2", "direction": "inbound"},
        })
        client = WsClient("/")
        client.on("session:new", lambda s: sessions.append(s))
        await client.handle_connection(ws)
        assert len(sessions) == 1
        assert sessions[0].call_sid == "call-123"

    @pytest.mark.asyncio
    async def test_session_has_correct_properties(self):
        captured = {}
        ws = _make_ws({
            "type": "session:new",
            "msgid": "msg-1",
            "data": {
                "call_sid": "call-xyz",
                "account_sid": "acct-1",
                "from": "+1234",
                "to": "+5678",
                "direction": "outbound",
                "call_id": "sip-id",
                "env_vars": {"LANG": "en-US"},
            },
        })

        async def on_session(s):
            captured["call_sid"] = s.call_sid
            captured["from"] = s.from_
            captured["direction"] = s.direction
            captured["env"] = s.data.get("env_vars", {})

        client = WsClient("/")
        client.on("session:new", on_session)
        await client.handle_connection(ws)
        assert captured["call_sid"] == "call-xyz"
        assert captured["from"] == "+1234"
        assert captured["direction"] == "outbound"
        assert captured["env"]["LANG"] == "en-US"


# ── verb:hook dispatch ──────────────────────────────────────────────

class TestVerbHookDispatch:
    @pytest.mark.asyncio
    async def test_dispatches_to_session_handler(self):
        hook_data = []

        async def on_session(session):
            session.on("/gather-result", lambda d: hook_data.append(d))

        ws = _make_ws(
            {"type": "session:new", "msgid": "m1",
             "data": {"call_sid": "c1", "from": "+1", "to": "+2", "direction": "inbound"}},
            {"type": "verb:hook", "msgid": "m2", "hook": "/gather-result",
             "data": {"reason": "speechDetected", "speech": {"alternatives": [{"transcript": "hi"}]}}},
        )
        client = WsClient("/")
        client.on("session:new", on_session)
        await client.handle_connection(ws)
        assert len(hook_data) == 1
        assert hook_data[0]["reason"] == "speechDetected"

    @pytest.mark.asyncio
    async def test_auto_replies_when_no_handler(self):
        """Unhandled verb:hook must auto-reply with empty verb array."""
        ws = _make_ws(
            {"type": "session:new", "msgid": "m1",
             "data": {"call_sid": "c1", "from": "+1", "to": "+2", "direction": "inbound"}},
            {"type": "verb:hook", "msgid": "m2", "hook": "/unregistered", "data": {}},
        )
        client = WsClient("/")
        client.on("session:new", lambda s: None)
        await client.handle_connection(ws)

        # Find the auto-reply
        for call in ws.send.call_args_list:
            msg = json.loads(call[0][0])
            if msg.get("msgid") == "m2":
                assert msg["type"] == "ack"
                assert msg["data"] == []
                return
        pytest.fail("No auto-reply sent for unhandled verb:hook")

    @pytest.mark.asyncio
    async def test_falls_back_to_generic_verb_hook_handler(self):
        """If no specific handler, 'verb:hook' catch-all is tried before auto-reply."""
        caught = []

        async def on_session(session):
            session.on("verb:hook", lambda hook, data: caught.append(hook))

        ws = _make_ws(
            {"type": "session:new", "msgid": "m1",
             "data": {"call_sid": "c1", "from": "+1", "to": "+2", "direction": "inbound"}},
            {"type": "verb:hook", "msgid": "m2", "hook": "/some-hook", "data": {}},
        )
        client = WsClient("/")
        client.on("session:new", on_session)
        await client.handle_connection(ws)
        assert caught == ["/some-hook"]


# ── session:redirect ────────────────────────────────────────────────

class TestSessionRedirect:
    @pytest.mark.asyncio
    async def test_emits_session_redirect(self):
        redirects = []
        ws = _make_ws(
            {"type": "session:new", "msgid": "m1",
             "data": {"call_sid": "c1", "from": "+1", "to": "+2", "direction": "inbound"}},
            {"type": "session:redirect", "msgid": "m2",
             "data": {"call_sid": "c1", "from": "+1", "to": "+2", "direction": "inbound"}},
        )
        client = WsClient("/")
        client.on("session:new", lambda s: None)
        client.on("session:redirect", lambda s: redirects.append(s.call_sid))
        await client.handle_connection(ws)
        assert redirects == ["c1"]


# ── Binary frames and invalid JSON ──────────────────────────────────

class TestProtocolRobustness:
    @pytest.mark.asyncio
    async def test_binary_frames_ignored(self):
        """Binary frames (audio protocol) must not crash the control handler."""
        sessions = []
        ws = _make_ws(
            b"\x00\x01\x02\x03",  # Binary frame
            {"type": "session:new", "msgid": "m1",
             "data": {"call_sid": "c1", "from": "+1", "to": "+2", "direction": "inbound"}},
        )
        client = WsClient("/")
        client.on("session:new", lambda s: sessions.append(s))
        await client.handle_connection(ws)
        assert len(sessions) == 1

    @pytest.mark.asyncio
    async def test_invalid_json_skipped(self):
        sessions = []

        async def fake_iter():
            yield "not valid json {"
            yield json.dumps({
                "type": "session:new", "msgid": "m1",
                "data": {"call_sid": "c1", "from": "+1", "to": "+2", "direction": "inbound"},
            })

        ws = AsyncMock()
        ws.send = AsyncMock()
        ws.__aiter__ = lambda self: fake_iter()

        client = WsClient("/")
        client.on("session:new", lambda s: sessions.append(s))
        await client.handle_connection(ws)
        assert len(sessions) == 1
