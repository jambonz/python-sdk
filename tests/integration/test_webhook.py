"""Integration tests for webhook (HTTP) transport.

Spins up a real aiohttp server simulating a jambonz webhook application,
then sends real HTTP requests mimicking jambonz's behavior:
- POST with call data to get verb arrays
- OPTIONS for env vars discovery
- actionHook POSTs with gather/dial results

Each test validates the HTTP response matches the jambonz webhook contract:
- 200 status
- Content-Type: application/json
- Body is a JSON array of verb objects
"""


import pytest
from aiohttp import web
from aiohttp.test_utils import TestClient, TestServer

from jambonz_sdk.webhook import WebhookResponse, env_vars_middleware

# ── Sample app simulating a real jambonz webhook application ────────

def _create_app() -> web.Application:
    app = web.Application()

    async def incoming(req: web.Request) -> web.Response:
        body = await req.json()
        env = body.get("env_vars", {})
        greeting = env.get("GREETING", "Welcome.")

        jambonz = WebhookResponse()
        jambonz.say(text=greeting).gather(
            input=["speech", "digits"],
            actionHook="/menu",
            numDigits=1,
            timeout=10,
            say={"text": "Press 1 for sales, 2 for support."},
        ).say(text="No input. Goodbye.").hangup()
        return web.json_response(jambonz.to_json())

    async def menu(req: web.Request) -> web.Response:
        body = await req.json()
        jambonz = WebhookResponse()
        digits = body.get("digits", "")
        speech = body.get("speech", {}).get("alternatives", [{}])[0].get("transcript", "").lower()

        if digits == "1" or "sales" in speech:
            jambonz.say(text="Connecting to sales.").dial(
                target=[{"type": "phone", "number": "+15085551001"}],
                answerOnBridge=True,
                timeout=30,
                actionHook="/dial-done",
            )
        elif digits == "2" or "support" in speech:
            jambonz.say(text="Connecting to support.").dial(
                target=[{"type": "phone", "number": "+15085551002"}],
                answerOnBridge=True,
                timeout=30,
                actionHook="/dial-done",
            )
        else:
            jambonz.say(text="Invalid selection.").redirect(actionHook="/incoming")
        return web.json_response(jambonz.to_json())

    async def dial_done(req: web.Request) -> web.Response:
        body = await req.json()
        jambonz = WebhookResponse()
        status = body.get("dial_call_status", "unknown")
        jambonz.say(text=f"Call {status}. Goodbye.").hangup()
        return web.json_response(jambonz.to_json())

    async def call_status(req: web.Request) -> web.Response:
        return web.Response(status=200)

    async def options_handler(req: web.Request) -> web.Response:
        return web.json_response(env_vars_middleware({
            "GREETING": {"type": "string", "description": "Greeting text", "default": "Welcome."},
            "CARRIER": {"type": "string", "description": "Outbound carrier", "jambonzResource": "carriers"},
        }))

    app.router.add_post("/incoming", incoming)
    app.router.add_post("/menu", menu)
    app.router.add_post("/dial-done", dial_done)
    app.router.add_post("/call-status", call_status)
    app.router.add_route("OPTIONS", "/incoming", options_handler)
    return app


@pytest.fixture
async def client():
    async with TestClient(TestServer(_create_app())) as c:
        yield c


# ── Incoming call: jambonz POSTs call data, expects verb array ──────

class TestIncomingCallWebhook:
    @pytest.mark.asyncio
    async def test_returns_json_array(self, client):
        resp = await client.post("/incoming", json={"call_sid": "c1", "direction": "inbound"})
        assert resp.status == 200
        assert resp.content_type == "application/json"
        verbs = await resp.json()
        assert isinstance(verbs, list)

    @pytest.mark.asyncio
    async def test_first_verb_is_greeting(self, client):
        resp = await client.post("/incoming", json={})
        verbs = await resp.json()
        assert verbs[0]["verb"] == "say"
        assert verbs[0]["text"] == "Welcome."

    @pytest.mark.asyncio
    async def test_env_vars_override_greeting(self, client):
        """jambonz sends env_vars in the call payload."""
        resp = await client.post("/incoming", json={"env_vars": {"GREETING": "Hola!"}})
        verbs = await resp.json()
        assert verbs[0]["text"] == "Hola!"

    @pytest.mark.asyncio
    async def test_gather_with_all_properties(self, client):
        resp = await client.post("/incoming", json={})
        verbs = await resp.json()
        gather = verbs[1]
        assert gather["verb"] == "gather"
        assert gather["input"] == ["speech", "digits"]
        assert gather["actionHook"] == "/menu"
        assert gather["numDigits"] == 1
        assert gather["timeout"] == 10
        assert gather["say"]["text"] == "Press 1 for sales, 2 for support."

    @pytest.mark.asyncio
    async def test_fallback_verbs(self, client):
        resp = await client.post("/incoming", json={})
        verbs = await resp.json()
        assert verbs[2]["verb"] == "say"
        assert verbs[3]["verb"] == "hangup"


# ── Menu actionHook: jambonz POSTs gather result ────────────────────

class TestMenuActionHook:
    @pytest.mark.asyncio
    async def test_digit_1_routes_to_sales(self, client):
        resp = await client.post("/menu", json={"digits": "1", "reason": "dtmfDetected"})
        verbs = await resp.json()
        assert verbs[0]["text"] == "Connecting to sales."
        assert verbs[1]["verb"] == "dial"
        assert verbs[1]["target"][0]["number"] == "+15085551001"
        assert verbs[1]["answerOnBridge"] is True

    @pytest.mark.asyncio
    async def test_digit_2_routes_to_support(self, client):
        resp = await client.post("/menu", json={"digits": "2"})
        verbs = await resp.json()
        assert verbs[1]["target"][0]["number"] == "+15085551002"

    @pytest.mark.asyncio
    async def test_speech_input_routes_to_sales(self, client):
        resp = await client.post("/menu", json={
            "reason": "speechDetected",
            "speech": {"alternatives": [{"transcript": "I need sales help"}]},
        })
        verbs = await resp.json()
        assert verbs[0]["text"] == "Connecting to sales."

    @pytest.mark.asyncio
    async def test_invalid_digit_redirects(self, client):
        resp = await client.post("/menu", json={"digits": "9"})
        verbs = await resp.json()
        assert verbs[0]["text"] == "Invalid selection."
        assert verbs[1]["verb"] == "redirect"
        assert verbs[1]["actionHook"] == "/incoming"

    @pytest.mark.asyncio
    async def test_empty_input_redirects(self, client):
        resp = await client.post("/menu", json={"reason": "timeout"})
        verbs = await resp.json()
        assert verbs[1]["verb"] == "redirect"


# ── Dial actionHook: jambonz POSTs dial result ─────────────────────

class TestDialActionHook:
    @pytest.mark.asyncio
    async def test_completed_call(self, client):
        resp = await client.post("/dial-done", json={"dial_call_status": "completed", "duration": 120})
        verbs = await resp.json()
        assert "completed" in verbs[0]["text"]
        assert verbs[1]["verb"] == "hangup"

    @pytest.mark.asyncio
    async def test_failed_call(self, client):
        resp = await client.post("/dial-done", json={"dial_call_status": "failed"})
        verbs = await resp.json()
        assert "failed" in verbs[0]["text"]


# ── Call status: jambonz POSTs status updates ───────────────────────

class TestCallStatusWebhook:
    @pytest.mark.asyncio
    async def test_returns_200(self, client):
        resp = await client.post("/call-status", json={"call_sid": "c1", "call_status": "completed"})
        assert resp.status == 200


# ── OPTIONS: jambonz discovers env vars ─────────────────────────────

class TestEnvVarsDiscovery:
    @pytest.mark.asyncio
    async def test_options_returns_env_schema(self, client):
        resp = await client.options("/incoming")
        assert resp.status == 200
        body = await resp.json()
        assert "env" in body
        assert body["env"]["GREETING"]["type"] == "string"
        assert body["env"]["GREETING"]["default"] == "Welcome."

    @pytest.mark.asyncio
    async def test_jambonz_resource_field(self, client):
        """jambonzResource tells the portal to populate from account data."""
        resp = await client.options("/incoming")
        body = await resp.json()
        assert body["env"]["CARRIER"]["jambonzResource"] == "carriers"
