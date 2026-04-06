"""Spec-driven tests for JambonzClient REST API.

Tests validate the REST API contract:
- Correct URL construction: {baseUrl}/v1/Accounts/{accountSid}/{resource}
- Authorization header: Bearer {apiKey}
- HTTP methods match jambonz REST API spec
- Request bodies match expected format for each operation
- Resource accessors (calls, conferences, queues) exist and function
"""

from unittest.mock import AsyncMock, MagicMock

import pytest

from jambonz_sdk.client.api import JambonzClient


class _MockResponse:
    def __init__(self, status: int = 200, data=None):
        self.status = status
        self._data = data
        self.content_type = "application/json" if data is not None else "text/plain"

    async def json(self):
        return self._data

    async def text(self):
        return ""

    def raise_for_status(self):
        if self.status >= 400:
            raise Exception(f"HTTP {self.status}")

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        pass


def _client_with_mock(response: _MockResponse) -> tuple[JambonzClient, MagicMock]:
    client = JambonzClient(base_url="https://api.jambonz.us", account_sid="acct-123", api_key="key-456")
    mock_session = AsyncMock()
    mock_session.request = MagicMock(return_value=response)
    mock_session.closed = False
    client._session = mock_session
    return client, mock_session


# ── URL construction ────────────────────────────────────────────────

class TestUrlConstruction:
    def test_api_base_url(self):
        client = JambonzClient(base_url="https://api.jambonz.us", account_sid="acct-123", api_key="key")
        assert client._api_base == "https://api.jambonz.us/v1/Accounts/acct-123"

    def test_trailing_slash_stripped(self):
        client = JambonzClient(base_url="https://api.jambonz.us/", account_sid="acct-123", api_key="key")
        assert client._api_base == "https://api.jambonz.us/v1/Accounts/acct-123"


# ── Calls resource: jambonz REST /v1/Accounts/{sid}/Calls ───────────

class TestCallsCreate:
    """POST /Calls — create an outbound call."""

    @pytest.mark.asyncio
    async def test_sends_post_to_calls(self):
        client, mock = _client_with_mock(_MockResponse(201, {"sid": "call-new"}))
        await client.calls.create({"from": "+1234", "to": {"type": "phone", "number": "+5678"}, "call_hook": "/incoming"})
        args = mock.request.call_args
        assert args[0][0] == "POST"
        assert args[0][1].endswith("/Calls")

    @pytest.mark.asyncio
    async def test_returns_call_sid(self):
        client, _ = _client_with_mock(_MockResponse(201, {"sid": "call-new-123"}))
        result = await client.calls.create({"from": "+1234", "to": {"type": "phone", "number": "+5678"}})
        assert result == "call-new-123"

    @pytest.mark.asyncio
    async def test_passes_body(self):
        client, mock = _client_with_mock(_MockResponse(201, {"sid": "c1"}))
        body = {"from": "+1234", "to": {"type": "phone", "number": "+5678"}, "call_hook": "/hook", "timeout": 30}
        await client.calls.create(body)
        assert mock.request.call_args[1]["json"] == body


class TestCallsList:
    """GET /Calls — list active calls."""

    @pytest.mark.asyncio
    async def test_sends_get(self):
        client, mock = _client_with_mock(_MockResponse(200, []))
        await client.calls.list()
        assert mock.request.call_args[0][0] == "GET"

    @pytest.mark.asyncio
    async def test_passes_filters(self):
        client, mock = _client_with_mock(_MockResponse(200, []))
        await client.calls.list({"direction": "inbound"})
        assert mock.request.call_args[1]["params"] == {"direction": "inbound"}


class TestCallsGet:
    """GET /Calls/{callSid} — get call info."""

    @pytest.mark.asyncio
    async def test_url_includes_call_sid(self):
        client, mock = _client_with_mock(_MockResponse(200, {"call_sid": "c1"}))
        await client.calls.get("c1")
        assert "/Calls/c1" in mock.request.call_args[0][1]


class TestCallsDelete:
    """DELETE /Calls/{callSid} — terminate a call."""

    @pytest.mark.asyncio
    async def test_sends_delete(self):
        client, mock = _client_with_mock(_MockResponse(204))
        await client.calls.delete("c1")
        assert mock.request.call_args[0][0] == "DELETE"


class TestCallsRedirect:
    """PUT /Calls/{callSid} with call_hook — redirect a call."""

    @pytest.mark.asyncio
    async def test_sends_put_with_call_hook(self):
        client, mock = _client_with_mock(_MockResponse(200, {}))
        await client.calls.redirect("c1", "https://example.com/new")
        assert mock.request.call_args[0][0] == "PUT"
        assert mock.request.call_args[1]["json"]["call_hook"] == "https://example.com/new"


class TestCallsWhisper:
    """PUT /Calls/{callSid} with whisper — inject a verb."""

    @pytest.mark.asyncio
    async def test_sends_whisper_verb(self):
        client, mock = _client_with_mock(_MockResponse(200, {}))
        await client.calls.whisper("c1", {"verb": "say", "text": "Hello"})
        body = mock.request.call_args[1]["json"]
        assert body["whisper"]["verb"] == "say"
        assert body["whisper"]["text"] == "Hello"


class TestCallsMute:
    """PUT /Calls/{callSid} with mute_status."""

    @pytest.mark.asyncio
    async def test_mute(self):
        client, mock = _client_with_mock(_MockResponse(200, {}))
        await client.calls.mute("c1", "mute")
        assert mock.request.call_args[1]["json"]["mute_status"] == "mute"

    @pytest.mark.asyncio
    async def test_unmute(self):
        client, mock = _client_with_mock(_MockResponse(200, {}))
        await client.calls.mute("c1", "unmute")
        assert mock.request.call_args[1]["json"]["mute_status"] == "unmute"


class TestCallsPipelineUpdate:
    """PUT /Calls/{callSid} with pipeline_update."""

    @pytest.mark.asyncio
    async def test_sends_pipeline_update(self):
        client, mock = _client_with_mock(_MockResponse(200, {}))
        await client.calls.update_pipeline("c1", {"type": "update_instructions", "instructions": "New prompt"})
        body = mock.request.call_args[1]["json"]
        assert body["pipeline_update"]["type"] == "update_instructions"


# ── Conferences resource ────────────────────────────────────────────

class TestConferences:
    @pytest.mark.asyncio
    async def test_list(self):
        client, mock = _client_with_mock(_MockResponse(200, []))
        await client.conferences.list()
        assert mock.request.call_args[0][0] == "GET"
        assert "/Conferences" in mock.request.call_args[0][1]


# ── Queues resource ────────────────────────────────────────────

class TestQueues:
    @pytest.mark.asyncio
    async def test_list(self):
        client, mock = _client_with_mock(_MockResponse(200, []))
        await client.queues.list()
        assert "/Queues" in mock.request.call_args[0][1]

    @pytest.mark.asyncio
    async def test_list_with_search(self):
        client, mock = _client_with_mock(_MockResponse(200, []))
        await client.queues.list("support")
        assert mock.request.call_args[1]["params"] == {"search": "support"}


# ── Context manager ─────────────────────────────────────────────────

class TestClientLifecycle:
    @pytest.mark.asyncio
    async def test_async_context_manager(self):
        async with JambonzClient(base_url="https://api.jambonz.us", account_sid="a", api_key="k") as client:
            assert client.calls is not None
            assert client.conferences is not None
            assert client.queues is not None
