"""WebSocket Session class representing a single call.

A Session is created for each incoming call over a persistent WebSocket
connection. It extends VerbBuilder with send/reply semantics and event
handling for actionHook callbacks.
"""

from __future__ import annotations

import json
import logging
from collections.abc import Callable
from typing import Any

from jambonz_sdk.verb_builder import VerbBuilder

logger = logging.getLogger("jambonz_sdk.websocket.session")

EventHandler = Callable[..., Any]


class Session(VerbBuilder):
    """Represents a single call session over WebSocket.

    Provides verb building (inherited from VerbBuilder), message sending,
    and event-based actionHook handling.

    Attributes:
        call_sid: Unique call identifier.
        account_sid: Account identifier.
        application_sid: Application identifier.
        direction: Call direction ("inbound" or "outbound").
        from_: Caller phone number or SIP URI.
        to: Called phone number or SIP URI.
        call_id: SIP Call-ID.
        data: Full session data from session:new message.
        locals: Application-local storage dict for the session.
    """

    def __init__(
        self,
        ws: Any,
        data: dict[str, Any],
        msgid: str,
    ) -> None:
        super().__init__()
        self._ws = ws
        self._msgid = msgid
        self._handlers: dict[str, list[EventHandler]] = {}

        # Extract call properties from session data
        self.data = data
        self.call_sid: str = data.get("call_sid", "")
        self.account_sid: str = data.get("account_sid", "")
        self.application_sid: str = data.get("application_sid", "")
        self.direction: str = data.get("direction", "")
        self.from_: str = data.get("from", "")
        self.to: str = data.get("to", "")
        self.call_id: str = data.get("call_id", "")
        self.b3: str = data.get("b3", "")
        self.locals: dict[str, Any] = {}

    def on(self, event: str, handler: EventHandler) -> Session:
        """Register an event handler for an actionHook or lifecycle event.

        Args:
            event: Event name (e.g., ``'/gather-result'``, ``'close'``, ``'error'``).
            handler: Callback function to invoke when the event fires.

        Returns:
            self for chaining.
        """
        if event not in self._handlers:
            self._handlers[event] = []
        self._handlers[event].append(handler)
        return self

    def _emit(self, event: str, *args: Any) -> bool:
        """Emit an event to registered handlers.

        Returns True if any handler was called.
        """
        handlers = self._handlers.get(event, [])
        for handler in handlers:
            handler(*args)
        return bool(handlers)

    async def _emit_async(self, event: str, *args: Any) -> bool:
        """Emit an event, awaiting async handlers.

        Returns True if any handler was called.
        """
        import asyncio

        handlers = self._handlers.get(event, [])
        for handler in handlers:
            result = handler(*args)
            if asyncio.iscoroutine(result):
                await result
        return bool(handlers)

    async def send(self, **opts: Any) -> None:
        """Send the initial verb array (response to session:new).

        This should be called exactly once per session, after building
        the initial verb chain. Use ``.reply()`` for all subsequent
        responses (actionHook events).
        """
        verbs = self.to_list()
        msg = {
            "type": "ack",
            "msgid": self._msgid,
            "data": verbs,
        }
        if opts:
            msg.update(opts)
        await self._ws.send(json.dumps(msg))

    async def reply(self, **opts: Any) -> None:
        """Reply to an actionHook event with the next verb array.

        Must be called after receiving a verb:hook event. Uses the
        most recently received message ID for correlation.
        """
        verbs = self.to_list()
        msg = {
            "type": "ack",
            "msgid": self._msgid,
            "data": verbs,
        }
        if opts:
            msg.update(opts)
        await self._ws.send(json.dumps(msg))

    def _update_msgid(self, msgid: str) -> None:
        """Update the current message ID for reply correlation."""
        self._msgid = msgid

    # ── Inject Commands ─────────────────────────────────────────────

    async def inject_command(self, command: str, data: dict[str, Any] | None = None) -> None:
        """Send an immediate command (bypasses verb queue)."""
        msg: dict[str, Any] = {"type": "command", "command": command}
        if data:
            msg["data"] = data
        await self._ws.send(json.dumps(msg))

    async def inject_record(self, action: str, data: dict[str, Any] | None = None) -> None:
        """Control call recording.

        Args:
            action: One of 'startCallRecording', 'stopCallRecording',
                'pauseCallRecording', 'resumeCallRecording'.
            data: Additional recording options (e.g., siprecServerURL).
        """
        cmd_data: dict[str, Any] = {"action": action}
        if data:
            cmd_data.update(data)
        await self.inject_command("record", cmd_data)

    async def inject_whisper(self, verb: dict[str, Any]) -> None:
        """Inject a whisper verb (say/play) to one party."""
        await self.inject_command("whisper", {"whisper": verb})

    async def inject_mute(self, status: str) -> None:
        """Mute or unmute the call.

        Args:
            status: ``'mute'`` or ``'unmute'``.
        """
        await self.inject_command("mute", {"mute_status": status})

    async def inject_listen_status(self, status: str) -> None:
        """Pause or resume audio streaming.

        Args:
            status: ``'pause'`` or ``'resume'``.
        """
        await self.inject_command("listen:status", {"listen_status": status})

    async def inject_noise_isolation(
        self, status: str, opts: dict[str, Any] | None = None
    ) -> None:
        """Enable or disable noise isolation.

        Args:
            status: ``'on'`` or ``'off'``.
            opts: Additional options (vendor, level, etc.).
        """
        data: dict[str, Any] = {"noiseIsolation_status": status}
        if opts:
            data.update(opts)
        await self.inject_command("noiseIsolation:status", data)

    async def inject_dtmf(self, dtmf: str) -> None:
        """Send DTMF digits."""
        await self.inject_command("dtmf", {"dtmf": dtmf})

    async def inject_tag(self, data: dict[str, Any]) -> None:
        """Attach metadata to the call."""
        await self.inject_command("tag", data)

    async def inject_redirect(self, hook: str) -> None:
        """Redirect the call to a new webhook."""
        await self.inject_command("redirect", {"call_hook": hook})

    # ── TTS Token Streaming ─────────────────────────────────────────

    async def send_tts_tokens(self, text: str, **opts: Any) -> None:
        """Stream TTS text tokens for incremental synthesis."""
        msg: dict[str, Any] = {"type": "tts:tokens", "data": {"tokens": text}}
        if opts:
            msg["data"].update(opts)
        await self._ws.send(json.dumps(msg))

    async def flush_tts_tokens(self, **opts: Any) -> None:
        """Signal end of a TTS token stream."""
        msg: dict[str, Any] = {"type": "tts:flush", "data": {}}
        if opts:
            msg["data"].update(opts)
        await self._ws.send(json.dumps(msg))

    async def clear_tts_tokens(self) -> None:
        """Clear pending TTS tokens."""
        await self._ws.send(json.dumps({"type": "tts:clear", "data": {}}))

    # ── LLM Tool Output ────────────────────────────────────────────

    async def tool_output(self, tool_call_id: str, result: Any) -> Session:
        """Return a tool call result to the pipeline LLM.

        Args:
            tool_call_id: The tool_call_id from the llm:tool-call event.
            result: The tool result (will be JSON-serialized).

        Returns:
            self for chaining with .reply().
        """
        msg = {
            "type": "llm:tool-output",
            "data": {
                "tool_call_id": tool_call_id,
                "output": result,
            },
        }
        await self._ws.send(json.dumps(msg))
        return self

    # ── Pipeline Updates ────────────────────────────────────────────

    async def update_pipeline(self, data: dict[str, Any]) -> None:
        """Send a mid-conversation pipeline update.

        Args:
            data: Update payload with ``type`` key (e.g., 'update_instructions',
                'inject_context', 'update_tools', 'generate_reply').
        """
        msg = {"type": "pipeline:update", "data": data}
        await self._ws.send(json.dumps(msg))
