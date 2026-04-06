"""Spec-driven tests for AudioStream.

Tests validate the audio.drachtio.org WebSocket protocol:
- sendAudio: sends raw binary PCM frames
- playAudio: sends JSON {"type": "playAudio", "data": {audioContent, ...}}
- killAudio: sends {"type": "killAudio"}
- disconnect: sends {"type": "disconnect"}
- sendMark: sends {"type": "mark", "name": <name>}
- clearMarks: sends {"type": "clearMarks"}
"""

import json
from unittest.mock import AsyncMock

import pytest

from jambonz_sdk.websocket.audio_stream import AudioStream


def _make_stream() -> tuple[AudioStream, AsyncMock]:
    ws = AsyncMock()
    ws.send = AsyncMock()
    ws.close = AsyncMock()
    return AudioStream(ws), ws


# ── Binary audio sending ────────────────────────────────────────────

class TestSendAudio:
    """sendAudio must send raw binary PCM — not JSON-wrapped."""

    @pytest.mark.asyncio
    async def test_sends_raw_bytes(self):
        stream, ws = _make_stream()
        pcm = b"\x00\x01\x02\x03" * 100
        await stream.send_audio(pcm)
        ws.send.assert_called_once_with(pcm)

    @pytest.mark.asyncio
    async def test_sends_exact_bytes(self):
        stream, ws = _make_stream()
        pcm = bytes(range(256))
        await stream.send_audio(pcm)
        assert ws.send.call_args[0][0] == pcm


# ── playAudio (non-streaming mode) ─────────────────────────────────

class TestPlayAudio:
    """playAudio sends base64-encoded audio clips per the jambonz protocol."""

    @pytest.mark.asyncio
    async def test_message_format(self):
        stream, ws = _make_stream()
        await stream.play_audio("base64data", audio_content_type="raw", sample_rate=16000)
        msg = json.loads(ws.send.call_args[0][0])
        assert msg["type"] == "playAudio"
        assert msg["data"]["audioContent"] == "base64data"
        assert msg["data"]["audioContentType"] == "raw"
        assert msg["data"]["sampleRate"] == 16000

    @pytest.mark.asyncio
    async def test_with_id_for_play_done_tracking(self):
        stream, ws = _make_stream()
        await stream.play_audio("data", id="greeting-1")
        msg = json.loads(ws.send.call_args[0][0])
        assert msg["data"]["id"] == "greeting-1"

    @pytest.mark.asyncio
    async def test_queue_play_flag(self):
        stream, ws = _make_stream()
        await stream.play_audio("data", queue_play=True)
        msg = json.loads(ws.send.call_args[0][0])
        assert msg["data"]["queuePlay"] is True

    @pytest.mark.asyncio
    async def test_defaults(self):
        stream, ws = _make_stream()
        await stream.play_audio("data")
        msg = json.loads(ws.send.call_args[0][0])
        assert msg["data"]["audioContentType"] == "raw"
        assert msg["data"]["sampleRate"] == 8000
        assert msg["data"]["queuePlay"] is False
        assert "id" not in msg["data"]


# ── Control commands ────────────────────────────────────────────────

class TestAudioControlCommands:
    @pytest.mark.asyncio
    async def test_kill_audio(self):
        stream, ws = _make_stream()
        await stream.kill_audio()
        msg = json.loads(ws.send.call_args[0][0])
        assert msg["type"] == "killAudio"

    @pytest.mark.asyncio
    async def test_disconnect(self):
        stream, ws = _make_stream()
        await stream.disconnect()
        msg = json.loads(ws.send.call_args[0][0])
        assert msg["type"] == "disconnect"

    @pytest.mark.asyncio
    async def test_close(self):
        stream, ws = _make_stream()
        await stream.close()
        ws.close.assert_called_once()


# ── Marks (synchronization markers) ────────────────────────────────

class TestMarks:
    """Marks track audio playout. Only work with bidirectional streaming mode."""

    @pytest.mark.asyncio
    async def test_send_mark(self):
        stream, ws = _make_stream()
        await stream.send_mark("chunk-1")
        msg = json.loads(ws.send.call_args[0][0])
        assert msg["type"] == "mark"
        assert msg["name"] == "chunk-1"

    @pytest.mark.asyncio
    async def test_clear_marks(self):
        stream, ws = _make_stream()
        await stream.clear_marks()
        msg = json.loads(ws.send.call_args[0][0])
        assert msg["type"] == "clearMarks"


# ── Event registration ─────────────────────────────────────────────

class TestAudioStreamEvents:
    def test_on_returns_self(self):
        stream, _ = _make_stream()
        assert stream.on("audio", lambda d: None) is stream

    def test_default_properties(self):
        stream, _ = _make_stream()
        assert stream.call_sid == ""
        assert stream.sample_rate == 8000
        assert stream.metadata == {}
