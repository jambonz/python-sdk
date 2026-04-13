"""Spec-driven tests for WebSocket Session.

Tests validate the jambonz WebSocket protocol contract:
- session.send() produces an "ack" message with verbs for session:new
- session.reply() produces an "ack" message with verbs for verb:hook responses
- Inject commands produce "command" messages per the jambonz WS spec
- TTS streaming produces tts:tokens/tts:flush/tts:clear messages
- Tool output produces llm:tool-output messages
- Agent updates produce agent:update messages
- Session properties are correctly extracted from session:new data
"""

import json
from unittest.mock import AsyncMock

import pytest

from jambonz_sdk.websocket.session import Session


def _make_session(data: dict | None = None, msgid: str = "msg-1") -> tuple[Session, AsyncMock]:
    ws = AsyncMock()
    ws.send = AsyncMock()
    session_data = data or {
        "call_sid": "call-123",
        "account_sid": "acct-456",
        "application_sid": "app-789",
        "direction": "inbound",
        "from": "+15085551212",
        "to": "+15085559876",
        "call_id": "sip-call-id",
        "b3": "trace-id",
        "env_vars": {"GREETING": "Hello!"},
    }
    return Session(ws, session_data, msgid), ws


# ── Session properties from session:new payload ────────────────────

class TestSessionProperties:
    """Session must expose all standard jambonz call properties."""

    def test_call_sid(self):
        s, _ = _make_session()
        assert s.call_sid == "call-123"

    def test_account_sid(self):
        s, _ = _make_session()
        assert s.account_sid == "acct-456"

    def test_direction(self):
        s, _ = _make_session()
        assert s.direction == "inbound"

    def test_from(self):
        s, _ = _make_session()
        assert s.from_ == "+15085551212"

    def test_to(self):
        s, _ = _make_session()
        assert s.to == "+15085559876"

    def test_call_id(self):
        s, _ = _make_session()
        assert s.call_id == "sip-call-id"

    def test_env_vars_accessible(self):
        s, _ = _make_session()
        assert s.data["env_vars"]["GREETING"] == "Hello!"

    def test_locals_is_independent_storage(self):
        s, _ = _make_session()
        s.locals["key"] = "value"
        assert s.locals["key"] == "value"
        assert "key" not in s.data


# ── send() — initial response to session:new ───────────────────────

class TestSessionSend:
    """send() must produce: {"type": "ack", "msgid": <original_msgid>, "data": [verbs]}"""

    @pytest.mark.asyncio
    async def test_send_produces_ack(self):
        s, ws = _make_session(msgid="msg-1")
        s.say(text="Hello").hangup()
        await s.send()
        msg = json.loads(ws.send.call_args[0][0])
        assert msg["type"] == "ack"
        assert msg["msgid"] == "msg-1"

    @pytest.mark.asyncio
    async def test_send_includes_verbs(self):
        s, ws = _make_session()
        s.say(text="Hello").hangup()
        await s.send()
        msg = json.loads(ws.send.call_args[0][0])
        assert len(msg["data"]) == 2
        assert msg["data"][0]["verb"] == "say"
        assert msg["data"][1]["verb"] == "hangup"

    @pytest.mark.asyncio
    async def test_send_resets_verb_queue(self):
        s, ws = _make_session()
        s.say(text="first")
        await s.send()
        s.hangup()
        await s.send()
        msg = json.loads(ws.send.call_args[0][0])
        assert len(msg["data"]) == 1
        assert msg["data"][0]["verb"] == "hangup"


# ── reply() — response to verb:hook events ──────────────────────────

class TestSessionReply:
    """reply() must produce: {"type": "ack", "msgid": <hook_msgid>, "data": [verbs]}
    and must use the UPDATED msgid from the most recent verb:hook."""

    @pytest.mark.asyncio
    async def test_reply_uses_updated_msgid(self):
        s, ws = _make_session(msgid="msg-1")
        s._update_msgid("msg-2")
        s.say(text="Reply")
        await s.reply()
        msg = json.loads(ws.send.call_args[0][0])
        assert msg["type"] == "ack"
        assert msg["msgid"] == "msg-2"

    @pytest.mark.asyncio
    async def test_empty_reply(self):
        """reply() with no verbs sends empty array (valid per jambonz protocol)."""
        s, ws = _make_session()
        await s.reply()
        msg = json.loads(ws.send.call_args[0][0])
        assert msg["data"] == []


# ── Event handling ──────────────────────────────────────────────────

class TestSessionEvents:
    """Session must support event registration and emission for actionHook handling."""

    def test_on_returns_self(self):
        s, _ = _make_session()
        assert s.on("/echo", lambda d: None) is s

    def test_sync_handler_called(self):
        s, _ = _make_session()
        received = []
        s.on("/echo", lambda d: received.append(d))
        s._emit("/echo", {"reason": "speechDetected"})
        assert len(received) == 1
        assert received[0]["reason"] == "speechDetected"

    @pytest.mark.asyncio
    async def test_async_handler_awaited(self):
        s, _ = _make_session()
        received = []

        async def handler(d):
            received.append(d)

        s.on("/echo", handler)
        await s._emit_async("/echo", {"transcript": "hello"})
        assert received == [{"transcript": "hello"}]

    def test_no_handler_returns_false(self):
        s, _ = _make_session()
        assert s._emit("/nonexistent") is False

    def test_multiple_handlers(self):
        s, _ = _make_session()
        calls = []
        s.on("/hook", lambda d: calls.append("h1"))
        s.on("/hook", lambda d: calls.append("h2"))
        s._emit("/hook", {})
        assert calls == ["h1", "h2"]


# ── Inject commands: immediate mid-call control ─────────────────────

class TestInjectCommands:
    """Inject commands produce: {"type": "command", "command": <name>, "data": {...}}
    These bypass the verb queue and execute immediately on jambonz."""

    @pytest.mark.asyncio
    async def test_inject_mute(self):
        s, ws = _make_session()
        await s.inject_mute("mute")
        msg = json.loads(ws.send.call_args[0][0])
        assert msg["type"] == "command"
        assert msg["command"] == "mute"
        assert msg["data"]["mute_status"] == "mute"

    @pytest.mark.asyncio
    async def test_inject_unmute(self):
        s, ws = _make_session()
        await s.inject_mute("unmute")
        msg = json.loads(ws.send.call_args[0][0])
        assert msg["data"]["mute_status"] == "unmute"

    @pytest.mark.asyncio
    async def test_inject_whisper(self):
        s, ws = _make_session()
        await s.inject_whisper({"verb": "say", "text": "5 minutes left."})
        msg = json.loads(ws.send.call_args[0][0])
        assert msg["command"] == "whisper"
        assert msg["data"]["whisper"]["text"] == "5 minutes left."

    @pytest.mark.asyncio
    async def test_inject_record_start(self):
        s, ws = _make_session()
        await s.inject_record("startCallRecording", {"siprecServerURL": "sip:rec@example.com"})
        msg = json.loads(ws.send.call_args[0][0])
        assert msg["command"] == "record"
        assert msg["data"]["action"] == "startCallRecording"
        assert msg["data"]["siprecServerURL"] == "sip:rec@example.com"

    @pytest.mark.asyncio
    async def test_inject_record_stop(self):
        s, ws = _make_session()
        await s.inject_record("stopCallRecording")
        msg = json.loads(ws.send.call_args[0][0])
        assert msg["data"]["action"] == "stopCallRecording"

    @pytest.mark.asyncio
    async def test_inject_dtmf(self):
        s, ws = _make_session()
        await s.inject_dtmf("1234#")
        msg = json.loads(ws.send.call_args[0][0])
        assert msg["command"] == "dtmf"
        assert msg["data"]["dtmf"] == "1234#"

    @pytest.mark.asyncio
    async def test_inject_tag(self):
        s, ws = _make_session()
        await s.inject_tag({"supervisor": "jane", "priority": "high"})
        msg = json.loads(ws.send.call_args[0][0])
        assert msg["command"] == "tag"
        assert msg["data"]["supervisor"] == "jane"

    @pytest.mark.asyncio
    async def test_inject_redirect(self):
        s, ws = _make_session()
        await s.inject_redirect("/new-flow")
        msg = json.loads(ws.send.call_args[0][0])
        assert msg["command"] == "redirect"
        assert msg["data"]["call_hook"] == "/new-flow"

    @pytest.mark.asyncio
    async def test_inject_listen_status(self):
        s, ws = _make_session()
        await s.inject_listen_status("pause")
        msg = json.loads(ws.send.call_args[0][0])
        assert msg["command"] == "listen:status"
        assert msg["data"]["listen_status"] == "pause"


# ── TTS token streaming ────────────────────────────────────────────

class TestTtsStreaming:
    """TTS token streaming messages per jambonz protocol:
    - tts:tokens: {"type": "tts:tokens", "data": {"tokens": "<text>"}}
    - tts:flush: {"type": "tts:flush", "data": {}}
    - tts:clear: {"type": "tts:clear", "data": {}}
    """

    @pytest.mark.asyncio
    async def test_send_tts_tokens(self):
        s, ws = _make_session()
        await s.send_tts_tokens("Hello, how ")
        msg = json.loads(ws.send.call_args[0][0])
        assert msg["type"] == "tts:tokens"
        assert msg["data"]["tokens"] == "Hello, how "

    @pytest.mark.asyncio
    async def test_flush_tts_tokens(self):
        s, ws = _make_session()
        await s.flush_tts_tokens()
        msg = json.loads(ws.send.call_args[0][0])
        assert msg["type"] == "tts:flush"

    @pytest.mark.asyncio
    async def test_clear_tts_tokens(self):
        s, ws = _make_session()
        await s.clear_tts_tokens()
        msg = json.loads(ws.send.call_args[0][0])
        assert msg["type"] == "tts:clear"


# ── Tool output ─────────────────────────────────────────────────────

class TestToolOutput:
    """Tool output per jambonz protocol:
    {"type": "llm:tool-output", "data": {"tool_call_id": ..., "output": ...}}"""

    @pytest.mark.asyncio
    async def test_tool_output(self):
        s, ws = _make_session()
        result = await s.tool_output("call_abc", {"temperature": 72})
        assert result is s  # returns self for chaining
        msg = json.loads(ws.send.call_args[0][0])
        assert msg["type"] == "llm:tool-output"
        assert msg["data"]["tool_call_id"] == "call_abc"
        assert msg["data"]["output"]["temperature"] == 72


# ── Agent updates ────────────────────────────────────────────────

class TestAgentUpdate:
    """Agent updates per jambonz protocol:
    {"type": "agent:update", "data": {"type": ..., ...}}"""

    @pytest.mark.asyncio
    async def test_update_instructions(self):
        s, ws = _make_session()
        await s.update_agent({"type": "update_instructions", "instructions": "Be a billing agent."})
        msg = json.loads(ws.send.call_args[0][0])
        assert msg["type"] == "agent:update"
        assert msg["data"]["type"] == "update_instructions"
        assert msg["data"]["instructions"] == "Be a billing agent."

    @pytest.mark.asyncio
    async def test_inject_context(self):
        s, ws = _make_session()
        await s.update_agent({
            "type": "inject_context",
            "messages": [{"role": "system", "content": "Customer is Gold tier."}],
        })
        msg = json.loads(ws.send.call_args[0][0])
        assert msg["data"]["type"] == "inject_context"

    @pytest.mark.asyncio
    async def test_generate_reply_with_interrupt(self):
        s, ws = _make_session()
        await s.update_agent({
            "type": "generate_reply",
            "user_input": "Urgent override",
            "interrupt": True,
        })
        msg = json.loads(ws.send.call_args[0][0])
        assert msg["data"]["interrupt"] is True
