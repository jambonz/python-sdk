"""create_endpoint factory for WebSocket-based jambonz applications.

Sets up a WebSocket server that handles both control (ws.jambonz.org)
and audio (audio.drachtio.org) subprotocols.

For env vars discovery (OPTIONS), a lightweight HTTP server runs alongside
the WebSocket server on the same port using aiohttp, which hands off
WebSocket upgrade requests to the websockets library.
"""

from __future__ import annotations

import logging
from typing import Any

from aiohttp import web

from jambonz_sdk.websocket.client import WsClient
from jambonz_sdk.websocket.router import WsRouter, _AudioService

logger = logging.getLogger("jambonz_sdk.websocket.endpoint")


class MakeService:
    """Factory returned by ``create_endpoint`` for registering services.

    Call this as a function to register control services, or use
    ``.audio()`` to register audio services.
    """

    def __init__(self, router: WsRouter) -> None:
        self._router = router

    def __call__(self, *, path: str = "/") -> WsClient:
        """Register a control WebSocket service at the given path.

        Args:
            path: URL path to listen on.

        Returns:
            A WsClient that emits ``'session:new'`` events.
        """
        client = WsClient(path)
        self._router.use(path, client)
        return client

    def audio(self, *, path: str) -> _AudioService:
        """Register an audio WebSocket service at the given path.

        Args:
            path: URL path for the audio WebSocket.

        Returns:
            An audio service that emits ``'connection'`` events with AudioStream.
        """
        return self._router.use_audio(path)


async def create_endpoint(
    *,
    host: str = "0.0.0.0",
    port: int = 3000,
    env_vars: dict[str, dict[str, Any]] | None = None,
    logger_: logging.Logger | None = None,
    compress: bool = True,
) -> tuple[MakeService, web.AppRunner]:
    """Create a WebSocket endpoint for jambonz applications.

    Starts an HTTP + WebSocket server that handles:
    - OPTIONS requests for env vars discovery
    - WebSocket upgrades for jambonz control (ws.jambonz.org) and audio
      (audio.drachtio.org) subprotocols

    Args:
        host: Bind address (default ``"0.0.0.0"``).
        port: Bind port (default ``3000``).
        env_vars: Application environment variable schema for portal discovery.
        logger_: Optional logger instance.
        compress: Enable WebSocket permessage-deflate compression (default ``True``).

    Returns:
        A tuple of ``(make_service, runner)`` where ``make_service`` is used
        to register services and ``runner`` is the aiohttp AppRunner.

    Example::

        make_service, runner = await create_endpoint(port=3000)
        svc = make_service(path="/")

        svc.on("session:new", handle_session)

        # Server is running; to stop:
        await runner.cleanup()
    """
    log = logger_ or logger
    router = WsRouter()
    make_service = MakeService(router)

    app = web.Application()

    async def handle_options(request: web.Request) -> web.Response:
        """Respond to OPTIONS with env_vars schema for portal discovery."""
        if env_vars is not None:
            return web.json_response({"env": env_vars})
        return web.Response(status=200)

    async def handle_websocket(request: web.Request) -> web.WebSocketResponse:
        """Handle WebSocket upgrade and route to the appropriate service."""
        # Determine subprotocol from the Sec-WebSocket-Protocol header
        requested_protocols = request.headers.get("Sec-WebSocket-Protocol", "")
        protocols = [p.strip() for p in requested_protocols.split(",") if p.strip()]

        # Pick the best matching subprotocol
        selected_protocol = None
        for proto in ["audio.drachtio.org", "ws.jambonz.org"]:
            if proto in protocols:
                selected_protocol = proto
                break

        ws = web.WebSocketResponse(
            protocols=[selected_protocol] if selected_protocol else [],
            compress=compress,
        )
        await ws.prepare(request)

        # Wrap aiohttp WS into an adapter that the router can use
        adapter = _AiohttpWsAdapter(ws, request.path, selected_protocol)
        await router.route(adapter)

        return ws

    # Register routes: OPTIONS on all paths, and WebSocket GET on all paths
    app.router.add_route("OPTIONS", "/{path:.*}", handle_options)
    app.router.add_route("GET", "/{path:.*}", handle_websocket)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host, port)
    await site.start()

    log.info("jambonz WebSocket endpoint listening on %s:%d", host, port)

    return make_service, runner


class _AiohttpWsAdapter:
    """Adapts an aiohttp WebSocketResponse to the interface expected by WsClient/WsRouter.

    The router and session code call ``ws.send()``, ``async for msg in ws:``,
    ``ws.close()``, and access ``ws.request.path`` and ``ws.subprotocol``.
    """

    def __init__(self, ws: web.WebSocketResponse, path: str, subprotocol: str | None) -> None:
        self._ws = ws
        self._path = path
        self._subprotocol = subprotocol

    @property
    def subprotocol(self) -> str | None:
        return self._subprotocol

    @property
    def request(self) -> Any:
        """Mimic websockets ServerConnection.request with a .path attribute."""
        return _FakeRequest(self._path)

    async def send(self, data: str | bytes) -> None:
        if isinstance(data, bytes):
            await self._ws.send_bytes(data)
        else:
            await self._ws.send_str(data)

    async def close(self, code: int = 1000, reason: str = "") -> None:
        await self._ws.close(code=code, message=reason.encode() if reason else b"")

    def __aiter__(self):
        return self

    async def __anext__(self) -> str | bytes:
        from aiohttp import WSMsgType

        msg = await self._ws.receive()
        if msg.type == WSMsgType.TEXT:
            return msg.data
        elif msg.type == WSMsgType.BINARY:
            return msg.data
        elif msg.type in (WSMsgType.CLOSE, WSMsgType.CLOSING, WSMsgType.CLOSED):
            raise StopAsyncIteration
        elif msg.type == WSMsgType.ERROR:
            raise self._ws.exception() or ConnectionError("WebSocket error")
        raise StopAsyncIteration


class _FakeRequest:
    """Minimal object with a .path attribute to satisfy router.route()."""

    def __init__(self, path: str) -> None:
        self.path = path
