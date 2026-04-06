"""AudioStream - per-call audio WebSocket handler.

Handles the ``audio.drachtio.org`` subprotocol for streaming raw audio
between jambonz and the application.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Callable

logger = logging.getLogger("jambonz_sdk.websocket.audio_stream")

AudioHandler = Callable[..., Any]


class AudioStream:
    """Represents a single audio stream WebSocket connection.

    Receives raw L16 PCM audio and JSON text events from jambonz.
    Can send audio back for bidirectional streaming.

    Events:
        - ``audio``: Binary L16 PCM frame. Handler receives ``(pcm: bytes)``.
        - ``dtmf``: DTMF event. Handler receives ``(data: dict)`` with digit and duration.
        - ``playDone``: Playback completed. Handler receives ``(data: dict)`` with id.
        - ``mark``: Synchronization marker. Handler receives ``(data: dict)`` with name and event.
        - ``close``: Connection closed. Handler receives ``(code: int, reason: str)``.
        - ``error``: Error occurred. Handler receives ``(err: Exception)``.

    Attributes:
        call_sid: Call identifier.
        sample_rate: Audio sample rate.
        metadata: Initial metadata from the connection.
    """

    def __init__(self, ws: Any) -> None:
        self._ws = ws
        self._handlers: dict[str, list[AudioHandler]] = {}
        self.call_sid: str = ""
        self.sample_rate: int = 8000
        self.metadata: dict[str, Any] = {}

    def on(self, event: str, handler: AudioHandler) -> AudioStream:
        """Register an event handler.

        Returns self for chaining.
        """
        if event not in self._handlers:
            self._handlers[event] = []
        self._handlers[event].append(handler)
        return self

    async def _emit(self, event: str, *args: Any) -> None:
        import asyncio

        for handler in self._handlers.get(event, []):
            result = handler(*args)
            if asyncio.iscoroutine(result):
                await result

    async def _run(self) -> None:
        """Main message loop for the audio stream."""
        try:
            async for message in self._ws:
                if isinstance(message, bytes):
                    await self._emit("audio", message)
                else:
                    try:
                        data = json.loads(message)
                    except json.JSONDecodeError:
                        continue

                    event_type = data.get("type", "")

                    if event_type == "setup":
                        self.call_sid = data.get("callSid", "")
                        self.sample_rate = data.get("sampleRate", 8000)
                        self.metadata = data.get("metadata", {})
                    elif event_type == "dtmf":
                        await self._emit("dtmf", data)
                    elif event_type == "playDone":
                        await self._emit("playDone", data)
                    elif event_type == "mark":
                        await self._emit("mark", data)
                    else:
                        logger.debug("Unhandled audio event: %s", event_type)

        except StopAsyncIteration:
            await self._emit("close", 1000, "")
        except Exception as exc:
            await self._emit("error", exc)

    # ── Sending Audio ───────────────────────────────────────────────

    async def send_audio(self, pcm: bytes) -> None:
        """Send raw L16 PCM audio back to jambonz (streaming mode)."""
        await self._ws.send(pcm)

    async def play_audio(
        self,
        audio_content: str,
        *,
        audio_content_type: str = "raw",
        sample_rate: int = 8000,
        id: str | None = None,
        queue_play: bool = False,
    ) -> None:
        """Send a complete audio clip as base64 (non-streaming mode).

        Args:
            audio_content: Base64-encoded audio content.
            audio_content_type: ``'raw'`` or ``'wav'``.
            sample_rate: Audio sample rate in Hz.
            id: Optional ID returned in the playDone event.
            queue_play: If True, queue after current playback; if False, interrupt.
        """
        msg: dict[str, Any] = {
            "type": "playAudio",
            "data": {
                "audioContent": audio_content,
                "audioContentType": audio_content_type,
                "sampleRate": sample_rate,
                "queuePlay": queue_play,
            },
        }
        if id is not None:
            msg["data"]["id"] = id
        await self._ws.send(json.dumps(msg))

    async def kill_audio(self) -> None:
        """Stop playback and flush the buffer."""
        await self._ws.send(json.dumps({"type": "killAudio"}))

    async def disconnect(self) -> None:
        """End the listen/stream verb."""
        await self._ws.send(json.dumps({"type": "disconnect"}))

    async def send_mark(self, name: str) -> None:
        """Insert a synchronization marker."""
        await self._ws.send(json.dumps({"type": "mark", "name": name}))

    async def clear_marks(self) -> None:
        """Clear all pending markers."""
        await self._ws.send(json.dumps({"type": "clearMarks"}))

    async def close(self) -> None:
        """Close the WebSocket connection."""
        await self._ws.close()
