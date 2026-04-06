"""WsRouter - path-based routing for multiple WebSocket services."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from jambonz_sdk.websocket.audio_stream import AudioStream
from jambonz_sdk.websocket.client import WsClient

logger = logging.getLogger("jambonz_sdk.websocket.router")


class _AudioService:
    """Manages audio WebSocket connections for a specific path."""

    def __init__(self, path: str) -> None:
        self.path = path
        self._handlers: dict[str, list] = {}

    def on(self, event: str, handler: object) -> _AudioService:
        if event not in self._handlers:
            self._handlers[event] = []
        self._handlers[event].append(handler)
        return self

    async def handle_connection(self, ws: Any) -> None:
        stream = AudioStream(ws)
        handlers = self._handlers.get("connection", [])
        for handler in handlers:
            result = handler(stream)
            if asyncio.iscoroutine(result):
                await result
        await stream._run()


class WsRouter:
    """Routes incoming WebSocket connections to the appropriate service by path.

    Supports both control (``ws.jambonz.org``) and audio (``audio.drachtio.org``)
    WebSocket subprotocols.
    """

    def __init__(self) -> None:
        self._services: dict[str, WsClient] = {}
        self._audio_services: dict[str, _AudioService] = {}

    def use(self, path: str, client: WsClient) -> None:
        """Register a control service for a path."""
        self._services[path] = client

    def use_audio(self, path: str) -> _AudioService:
        """Register an audio service for a path.

        Returns an _AudioService that emits ``'connection'`` events with
        an AudioStream instance.
        """
        svc = _AudioService(path)
        self._audio_services[path] = svc
        return svc

    async def route(self, ws: Any) -> None:
        """Route a WebSocket connection to the appropriate service.

        Called by the WebSocket server for each new connection.
        """
        path = ws.request.path if ws.request else "/"

        # Check subprotocol to determine if this is audio or control
        subprotocol = ws.subprotocol

        if subprotocol == "audio.drachtio.org":
            svc = self._audio_services.get(path)
            if svc:
                await svc.handle_connection(ws)
            else:
                logger.warning("No audio service for path: %s", path)
                await ws.close(4004, "No audio service for path")
        else:
            # Default to control protocol
            svc_ctrl = self._services.get(path)
            if svc_ctrl:
                await svc_ctrl.handle_connection(ws)
            else:
                logger.warning("No service for path: %s", path)
                await ws.close(4004, "No service for path")
