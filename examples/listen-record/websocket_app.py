"""Listen/Record - WebSocket example.

Records call audio using the listen verb to stream audio to a WebSocket handler.
Demonstrates the audio WebSocket protocol with makeService.audio().

Usage:
    python websocket_app.py
"""

import asyncio

from jambonz_sdk.websocket import create_endpoint


async def main():
    make_service, server = await create_endpoint(port=3000)

    # Control service - handles call sessions
    svc = make_service(path="/")

    # Audio service - receives audio streams
    audio_svc = make_service.audio(path="/audio-stream")

    async def handle_session(session):
        print(f"Incoming call: {session.call_sid}")

        async def on_listen_done(evt):
            print(f"Listen ended: {evt.get('reason', 'unknown')}")
            session.say(text="Recording complete. Thank you. Goodbye.").hangup()
            await session.reply()

        session.on("/listen-done", on_listen_done)

        session.answer().say(
            text="This call will be recorded. I will record for up to 30 seconds. Press pound to stop early."
        ).listen(
            url="/audio-stream",
            actionHook="/listen-done",
            sampleRate=16000,
            mixType="mono",
            finishOnKey="#",
            maxLength=30,
            playBeep=True,
            metadata={"purpose": "recording", "call_sid": session.call_sid},
        ).say(text="Recording complete. Thank you. Goodbye.").hangup()
        await session.send()

    svc.on("session:new", handle_session)

    # Handle audio connections
    total_bytes = {}

    def on_audio_connection(stream):
        print(f"Audio stream connected: call={stream.call_sid}, rate={stream.sample_rate}")
        print(f"Metadata: {stream.metadata}")
        call_sid = stream.metadata.get("call_sid", "unknown")
        total_bytes[call_sid] = 0

        def on_audio(pcm: bytes):
            total_bytes[call_sid] = total_bytes.get(call_sid, 0) + len(pcm)

        def on_close(code, reason):
            total = total_bytes.pop(call_sid, 0)
            duration_secs = total / (16000 * 2)  # 16kHz, 16-bit (2 bytes per sample)
            print(f"Audio stream closed: {total} bytes ({duration_secs:.1f}s of audio)")

        stream.on("audio", on_audio)
        stream.on("close", on_close)

    audio_svc.on("connection", on_audio_connection)

    print("Listen/Record WebSocket app listening on port 3000")
    await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
