"""JambonzClient - REST API client for jambonz platform management and call control.

Provides typed methods for creating calls, querying active calls,
and mid-call control (redirect, whisper, mute, etc.).
"""

from __future__ import annotations

from typing import Any

import aiohttp


class _Resource:
    """Base class for API resources."""

    def __init__(self, client: JambonzClient, path: str) -> None:
        self._client = client
        self._path = path

    async def _request(
        self,
        method: str,
        path: str = "",
        *,
        json: Any = None,
        params: dict[str, str] | None = None,
    ) -> Any:
        return await self._client._request(
            method, f"{self._path}{path}", json=json, params=params
        )


class CallsResource(_Resource):
    """REST API operations for active calls."""

    def __init__(self, client: JambonzClient) -> None:
        super().__init__(client, "/Calls")

    async def create(self, opts: dict[str, Any]) -> str:
        """Create an outbound call.

        Args:
            opts: Call options including ``from``, ``to``, ``call_hook``, etc.

        Returns:
            The call_sid of the created call.
        """
        result = await self._request("POST", json=opts)
        return result.get("sid", result.get("call_sid", ""))

    async def list(self, filter: dict[str, str] | None = None) -> list[dict[str, Any]]:
        """List active calls.

        Args:
            filter: Optional filter by direction, from, to, callStatus.
        """
        return await self._request("GET", params=filter)

    async def get(self, call_sid: str) -> dict[str, Any]:
        """Get information about a specific call."""
        return await self._request("GET", f"/{call_sid}")

    async def count(self) -> dict[str, int]:
        """Get count of inbound/outbound calls."""
        return await self._request("GET", "/count")

    async def update(self, call_sid: str, opts: dict[str, Any]) -> dict[str, Any]:
        """Update an active call (generic)."""
        return await self._request("PUT", f"/{call_sid}", json=opts)

    async def delete(self, call_sid: str) -> None:
        """Terminate a call."""
        await self._request("DELETE", f"/{call_sid}")

    async def redirect(self, call_sid: str, hook: str) -> dict[str, Any]:
        """Redirect a call to a new webhook.

        Args:
            call_sid: The call to redirect.
            hook: URL of the new webhook.
        """
        return await self.update(call_sid, {"call_hook": hook})

    async def whisper(self, call_sid: str, verb: dict[str, Any]) -> dict[str, Any]:
        """Inject a whisper verb (say/play) into the call.

        Args:
            call_sid: The call to whisper to.
            verb: A verb dict (e.g., ``{"verb": "say", "text": "Hello"}``).
        """
        return await self.update(call_sid, {"whisper": verb})

    async def mute(self, call_sid: str, status: str) -> dict[str, Any]:
        """Mute or unmute a call.

        Args:
            call_sid: The call to mute.
            status: ``'mute'`` or ``'unmute'``.
        """
        return await self.update(call_sid, {"mute_status": status})

    async def update_agent(
        self, call_sid: str, data: dict[str, Any]
    ) -> dict[str, Any]:
        """Send a mid-conversation agent update.

        Args:
            call_sid: The call to update.
            data: Agent update payload.
        """
        return await self.update(call_sid, {"agent_update": data})

    async def noise_isolation(
        self, call_sid: str, status: str, opts: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Enable or disable noise isolation.

        Args:
            call_sid: The call.
            status: ``'on'`` or ``'off'``.
            opts: Additional noise isolation options.
        """
        data: dict[str, Any] = {"noiseIsolation_status": status}
        if opts:
            data.update(opts)
        return await self.update(call_sid, data)


class ConferencesResource(_Resource):
    """REST API operations for conferences."""

    def __init__(self, client: JambonzClient) -> None:
        super().__init__(client, "/Conferences")

    async def list(self) -> list[dict[str, Any]]:
        """List active conferences."""
        return await self._request("GET")


class QueuesResource(_Resource):
    """REST API operations for call queues."""

    def __init__(self, client: JambonzClient) -> None:
        super().__init__(client, "/Queues")

    async def list(self, search: str | None = None) -> list[dict[str, Any]]:
        """List active queues.

        Args:
            search: Optional search string to filter queues.
        """
        params = {"search": search} if search else None
        return await self._request("GET", params=params)


class JambonzClient:
    """REST API client for jambonz platform.

    Provides access to call control, conferences, and queues.

    Example::

        client = JambonzClient(
            base_url="https://api.jambonz.us",
            account_sid="your-account-sid",
            api_key="your-api-key",
        )

        # Create an outbound call
        call_sid = await client.calls.create({
            "from": "+15085551212",
            "to": {"type": "phone", "number": "+15085551213"},
            "call_hook": "/incoming",
        })

        # Mid-call control
        await client.calls.mute(call_sid, "mute")
        await client.calls.whisper(call_sid, {"verb": "say", "text": "Hello"})
    """

    def __init__(
        self,
        *,
        base_url: str,
        account_sid: str,
        api_key: str,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._account_sid = account_sid
        self._api_key = api_key
        self._session: aiohttp.ClientSession | None = None

        # Resource accessors
        self.calls = CallsResource(self)
        self.conferences = ConferencesResource(self)
        self.queues = QueuesResource(self)

    @property
    def _api_base(self) -> str:
        return f"{self._base_url}/v1/Accounts/{self._account_sid}"

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                headers={
                    "Authorization": f"Bearer {self._api_key}",
                    "Content-Type": "application/json",
                }
            )
        return self._session

    async def _request(
        self,
        method: str,
        path: str,
        *,
        json: Any = None,
        params: dict[str, str] | None = None,
    ) -> Any:
        session = await self._get_session()
        url = f"{self._api_base}{path}"

        async with session.request(method, url, json=json, params=params) as resp:
            if resp.status == 204:
                return None
            resp.raise_for_status()
            if resp.content_type == "application/json":
                return await resp.json()
            return await resp.text()

    async def close(self) -> None:
        """Close the underlying HTTP session."""
        if self._session and not self._session.closed:
            await self._session.close()

    async def __aenter__(self) -> JambonzClient:
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()
