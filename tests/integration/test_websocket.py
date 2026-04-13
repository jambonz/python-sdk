"""Integration tests for WebSocket transport.

Spins up a real aiohttp WebSocket server using create_endpoint and connects
with real WebSocket clients, simulating the jambonz ↔ application protocol:

1. jambonz connects with Sec-WebSocket-Protocol: ws.jambonz.org
2. jambonz sends session:new with call data
3. App responds with ack containing verb array
4. jambonz sends verb:hook when verbs complete (e.g., gather result)
5. App responds with ack containing next verbs
6. App can inject commands (mute, whisper, record) at any time
7. App can stream TTS tokens
8. App can send agent updates
9. jambonz sends OPTIONS for env vars discovery (HTTP, not WS)
"""

import asyncio
import json

import aiohttp
import pytest

from jambonz_sdk.websocket import create_endpoint

# ── Helpers ─────────────────────────────────────────────────────────

def _session_new(call_sid="call-123", msgid="msg-1", **extra):
    data = {
        "call_sid": call_sid,
        "account_sid": "acct-456",
        "application_sid": "app-789",
        "direction": "inbound",
        "from": "+15085551212",
        "to": "+15085559876",
        "call_id": "sip-call-id",
        **extra,
    }
    return json.dumps({"type": "session:new", "msgid": msgid, "data": data})


def _verb_hook(hook, data=None, msgid="msg-2"):
    return json.dumps({"type": "verb:hook", "msgid": msgid, "hook": hook, "data": data or {}})


async def _ws_connect(port, path="/"):
    http = aiohttp.ClientSession()
    ws = await http.ws_connect(f"http://localhost:{port}{path}", protocols=["ws.jambonz.org"])
    return http, ws


async def _recv(ws, timeout=2):
    msg = await asyncio.wait_for(ws.receive(), timeout=timeout)
    return json.loads(msg.data)


# ── Basic protocol: session:new → ack with verbs ───────────────────

class TestSessionNewProtocol:
    """jambonz sends session:new, app must reply with ack containing verbs."""

    @pytest.mark.asyncio
    async def test_hello_world(self):
        port = 19101
        make_service, runner = await create_endpoint(port=port)
        svc = make_service(path="/")

        async def handler(session):
            session.say(text="Hello!").hangup()
            await session.send()

        svc.on("session:new", handler)
        try:
            http, ws = await _ws_connect(port)
            await ws.send_str(_session_new())
            msg = await _recv(ws)
            assert msg["type"] == "ack"
            assert msg["msgid"] == "msg-1"
            assert msg["data"][0]["verb"] == "say"
            assert msg["data"][0]["text"] == "Hello!"
            assert msg["data"][1]["verb"] == "hangup"
            await ws.close()
            await http.close()
        finally:
            await runner.cleanup()

    @pytest.mark.asyncio
    async def test_session_properties_from_call_data(self):
        port = 19102
        make_service, runner = await create_endpoint(port=port)
        svc = make_service(path="/")
        captured = {}

        async def handler(session):
            captured.update({
                "call_sid": session.call_sid,
                "from": session.from_,
                "to": session.to,
                "direction": session.direction,
            })
            session.hangup()
            await session.send()

        svc.on("session:new", handler)
        try:
            http, ws = await _ws_connect(port)
            await ws.send_str(_session_new(call_sid="call-xyz"))
            await _recv(ws)
            assert captured["call_sid"] == "call-xyz"
            assert captured["from"] == "+15085551212"
            assert captured["direction"] == "inbound"
            await ws.close()
            await http.close()
        finally:
            await runner.cleanup()


# ── actionHook flow: gather → verb:hook → reply ────────────────────

class TestActionHookProtocol:
    """When a verb completes, jambonz sends verb:hook. App must reply with ack."""

    @pytest.mark.asyncio
    async def test_gather_speech_echo(self):
        port = 19103
        make_service, runner = await create_endpoint(port=port)
        svc = make_service(path="/")

        async def handler(session):
            async def on_echo(evt):
                transcript = evt.get("speech", {}).get("alternatives", [{}])[0].get("transcript", "")
                session.say(text=f"You said: {transcript}.").hangup()
                await session.reply()

            session.on("/echo", on_echo)
            session.gather(input=["speech"], actionHook="/echo", timeout=10)
            await session.send()

        svc.on("session:new", handler)
        try:
            http, ws = await _ws_connect(port)
            # session:new → gather
            await ws.send_str(_session_new())
            initial = await _recv(ws)
            assert initial["data"][0]["verb"] == "gather"

            # verb:hook → reply
            await ws.send_str(_verb_hook("/echo", {
                "reason": "speechDetected",
                "speech": {"alternatives": [{"transcript": "hello"}]},
            }))
            reply = await _recv(ws)
            assert reply["type"] == "ack"
            assert reply["data"][0]["text"] == "You said: hello."
            assert reply["data"][1]["verb"] == "hangup"
            await ws.close()
            await http.close()
        finally:
            await runner.cleanup()

    @pytest.mark.asyncio
    async def test_multi_step_conversation(self):
        """Multiple actionHook round-trips on the same session."""
        port = 19104
        make_service, runner = await create_endpoint(port=port)
        svc = make_service(path="/")

        async def handler(session):
            async def on_step1(evt):
                session.say(text="Step 1 done.").gather(
                    input=["speech"], actionHook="/step2", timeout=10
                )
                await session.reply()

            async def on_step2(evt):
                session.say(text="Step 2 done.").hangup()
                await session.reply()

            session.on("/step1", on_step1)
            session.on("/step2", on_step2)
            session.gather(input=["speech"], actionHook="/step1", timeout=10)
            await session.send()

        svc.on("session:new", handler)
        try:
            http, ws = await _ws_connect(port)
            await ws.send_str(_session_new())
            await _recv(ws)  # initial gather

            await ws.send_str(_verb_hook("/step1", {"reason": "speechDetected", "speech": {"alternatives": [{"transcript": "go"}]}}))
            r1 = await _recv(ws)
            assert r1["data"][0]["text"] == "Step 1 done."
            assert r1["data"][1]["actionHook"] == "/step2"

            await ws.send_str(_verb_hook("/step2", {"reason": "speechDetected"}, msgid="msg-3"))
            r2 = await _recv(ws)
            assert r2["data"][0]["text"] == "Step 2 done."
            assert r2["data"][1]["verb"] == "hangup"
            await ws.close()
            await http.close()
        finally:
            await runner.cleanup()

    @pytest.mark.asyncio
    async def test_unhandled_hook_auto_replies(self):
        port = 19105
        make_service, runner = await create_endpoint(port=port)
        svc = make_service(path="/")

        async def handler(session):
            session.say(text="Hello")
            await session.send()

        svc.on("session:new", handler)
        try:
            http, ws = await _ws_connect(port)
            await ws.send_str(_session_new())
            await _recv(ws)
            await ws.send_str(_verb_hook("/no-handler", {}))
            reply = await _recv(ws)
            assert reply["data"] == []
            await ws.close()
            await http.close()
        finally:
            await runner.cleanup()


# ── Inject commands: mid-call control ───────────────────────────────

class TestInjectCommandsProtocol:
    """App sends command messages that jambonz executes immediately."""

    @pytest.mark.asyncio
    async def test_inject_mute(self):
        port = 19106
        make_service, runner = await create_endpoint(port=port)
        svc = make_service(path="/")

        async def handler(session):
            session.say(text="Hello")
            await session.send()
            await session.inject_mute("mute")

        svc.on("session:new", handler)
        try:
            http, ws = await _ws_connect(port)
            await ws.send_str(_session_new())
            await _recv(ws)  # ack
            cmd = await _recv(ws)  # inject
            assert cmd["type"] == "command"
            assert cmd["command"] == "mute"
            assert cmd["data"]["mute_status"] == "mute"
            await ws.close()
            await http.close()
        finally:
            await runner.cleanup()

    @pytest.mark.asyncio
    async def test_inject_whisper(self):
        port = 19107
        make_service, runner = await create_endpoint(port=port)
        svc = make_service(path="/")

        async def handler(session):
            session.say(text="Hello")
            await session.send()
            await session.inject_whisper({"verb": "say", "text": "Supervisor here."})

        svc.on("session:new", handler)
        try:
            http, ws = await _ws_connect(port)
            await ws.send_str(_session_new())
            await _recv(ws)
            cmd = await _recv(ws)
            assert cmd["command"] == "whisper"
            assert cmd["data"]["whisper"]["text"] == "Supervisor here."
            await ws.close()
            await http.close()
        finally:
            await runner.cleanup()


# ── TTS token streaming ────────────────────────────────────────────

class TestTtsStreamingProtocol:
    @pytest.mark.asyncio
    async def test_token_stream_and_flush(self):
        port = 19108
        make_service, runner = await create_endpoint(port=port)
        svc = make_service(path="/")

        async def handler(session):
            session.say(text="Placeholder")
            await session.send()
            await session.send_tts_tokens("Hello, ")
            await session.send_tts_tokens("how can I help?")
            await session.flush_tts_tokens()

        svc.on("session:new", handler)
        try:
            http, ws = await _ws_connect(port)
            await ws.send_str(_session_new())
            await _recv(ws)  # ack
            t1 = await _recv(ws)
            assert t1["type"] == "tts:tokens"
            assert t1["data"]["tokens"] == "Hello, "
            t2 = await _recv(ws)
            assert t2["data"]["tokens"] == "how can I help?"
            t3 = await _recv(ws)
            assert t3["type"] == "tts:flush"
            await ws.close()
            await http.close()
        finally:
            await runner.cleanup()


# ── Agent updates ────────────────────────────────────────────────

class TestAgentUpdateProtocol:
    @pytest.mark.asyncio
    async def test_update_instructions(self):
        port = 19109
        make_service, runner = await create_endpoint(port=port)
        svc = make_service(path="/")

        async def handler(session):
            session.agent(
                stt={"vendor": "deepgram"},
                tts={"vendor": "cartesia", "voice": "sonic"},
                llm={"vendor": "openai", "model": "gpt-4o", "llmOptions": {}},
                actionHook="/done",
            )
            await session.send()
            await session.update_agent({
                "type": "update_instructions",
                "instructions": "Now help with billing.",
            })

        svc.on("session:new", handler)
        try:
            http, ws = await _ws_connect(port)
            await ws.send_str(_session_new())
            ack = await _recv(ws)
            assert ack["data"][0]["verb"] == "agent"
            update = await _recv(ws)
            assert update["type"] == "agent:update"
            assert update["data"]["instructions"] == "Now help with billing."
            await ws.close()
            await http.close()
        finally:
            await runner.cleanup()


# ── Env vars: OPTIONS for portal discovery ──────────────────────────

class TestWebSocketEnvVars:
    @pytest.mark.asyncio
    async def test_options_returns_env_schema(self):
        port = 19110
        env_vars = {"GREETING": {"type": "string", "default": "Hello!"}}
        make_service, runner = await create_endpoint(port=port, env_vars=env_vars)
        make_service(path="/")
        try:
            async with aiohttp.ClientSession() as http:
                async with http.request("OPTIONS", f"http://localhost:{port}/") as resp:
                    assert resp.status == 200
                    body = await resp.json()
                    assert body["env"]["GREETING"]["default"] == "Hello!"
        finally:
            await runner.cleanup()

    @pytest.mark.asyncio
    async def test_session_receives_env_vars_from_call_data(self):
        port = 19111
        make_service, runner = await create_endpoint(port=port)
        svc = make_service(path="/")
        captured_env = {}

        async def handler(session):
            captured_env.update(session.data.get("env_vars", {}))
            session.say(text=captured_env.get("GREETING", "default"))
            await session.send()

        svc.on("session:new", handler)
        try:
            http, ws = await _ws_connect(port)
            await ws.send_str(_session_new(env_vars={"GREETING": "Hola!"}))
            ack = await _recv(ws)
            assert ack["data"][0]["text"] == "Hola!"
            assert captured_env["GREETING"] == "Hola!"
            await ws.close()
            await http.close()
        finally:
            await runner.cleanup()
