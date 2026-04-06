"""WsClient - manages a jambonz WebSocket service on a specific path."""

from __future__ import annotations

import json
import logging
from typing import Any, Callable

from jambonz_sdk.websocket.session import EventHandler, Session

logger = logging.getLogger("jambonz_sdk.websocket.client")


class WsClient:
    """Manages a jambonz WebSocket service on a specific path.

    Handles incoming WebSocket connections, creates Session objects for
    new calls, and routes messages to the appropriate session.

    Events:
        - ``session:new``: New call session. Handler receives ``(session: Session)``.
        - ``session:redirect``: Call redirected. Handler receives ``(session: Session)``.
        - ``error``: Error occurred. Handler receives ``(error: Exception)``.
    """

    def __init__(self, path: str) -> None:
        self.path = path
        self._handlers: dict[str, list[EventHandler]] = {}
        self._sessions: dict[str, Session] = {}

    def on(self, event: str, handler: EventHandler) -> WsClient:
        """Register an event handler.

        Args:
            event: Event name (``'session:new'``, ``'session:redirect'``, ``'error'``).
            handler: Callback function.

        Returns:
            self for chaining.
        """
        if event not in self._handlers:
            self._handlers[event] = []
        self._handlers[event].append(handler)
        return self

    def _emit(self, event: str, *args: Any) -> bool:
        """Emit an event to registered handlers."""
        handlers = self._handlers.get(event, [])
        for handler in handlers:
            handler(*args)
        return bool(handlers)

    async def _emit_async(self, event: str, *args: Any) -> bool:
        """Emit an event, awaiting async handlers."""
        import asyncio

        handlers = self._handlers.get(event, [])
        for handler in handlers:
            result = handler(*args)
            if asyncio.iscoroutine(result):
                await result
        return bool(handlers)

    async def handle_connection(self, ws: Any) -> None:
        """Handle a WebSocket connection for this service.

        Processes messages from jambonz and dispatches to the appropriate
        Session or emits service-level events.

        Args:
            ws: A WebSocket connection object supporting ``send()``,
                ``close()``, and async iteration for messages.
        """
        session: Session | None = None

        try:
            async for raw_message in ws:
                if isinstance(raw_message, bytes):
                    continue  # Binary frames handled by audio client

                try:
                    msg = json.loads(raw_message)
                except json.JSONDecodeError:
                    logger.warning("Received invalid JSON: %s", raw_message[:100])
                    continue

                msg_type = msg.get("type", "")
                msgid = msg.get("msgid", "")
                data = msg.get("data", {})

                if msg_type in ("session:new", "session:reconnect"):
                    session = Session(ws, data, msgid)
                    self._sessions[session.call_sid] = session
                    await self._emit_async("session:new", session)

                elif msg_type == "session:redirect":
                    if session:
                        session._update_msgid(msgid)
                        session.data = data
                        await self._emit_async("session:redirect", session)
                    else:
                        session = Session(ws, data, msgid)
                        self._sessions[session.call_sid] = session
                        await self._emit_async("session:redirect", session)

                elif msg_type == "session:adulting":
                    # Session is being transferred, just acknowledge
                    if session:
                        session._update_msgid(msgid)

                elif msg_type == "verb:hook":
                    if session:
                        session._update_msgid(msgid)
                        hook = msg.get("hook", "")
                        # Try specific handler first, then fallback
                        handled = await session._emit_async(hook, data)
                        if not handled:
                            handled = await session._emit_async("verb:hook", hook, data)
                        if not handled:
                            # Auto-reply with empty verb array
                            await session.reply()

                elif msg_type == "verb:status":
                    if session:
                        await session._emit_async("verb:status", data)

                elif msg_type == "call:status":
                    if session:
                        await session._emit_async("call:status", data)

                elif msg_type == "llm:tool-call":
                    if session:
                        session._update_msgid(msgid)
                        await session._emit_async("llm:tool-call", data)

                elif msg_type == "llm:event":
                    if session:
                        await session._emit_async("llm:event", data)

                elif msg_type == "tts:tokens-result":
                    if session:
                        await session._emit_async("tts:tokens-result", data)

                elif msg_type == "tts:streaming-event":
                    if session:
                        event_type = data.get("event_type", "")
                        # Emit specific event
                        if event_type:
                            await session._emit_async(f"tts:{event_type}", data)
                        # Emit catch-all
                        await session._emit_async("tts:streaming-event", data)

                else:
                    logger.debug("Unhandled message type: %s", msg_type)

        except StopAsyncIteration:
            if session:
                await session._emit_async("close", 1000, "")
        except Exception as exc:
            if session:
                await session._emit_async("error", exc)
            await self._emit_async("error", exc)
        finally:
            if session and session.call_sid in self._sessions:
                del self._sessions[session.call_sid]
