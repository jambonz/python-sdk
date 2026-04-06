"""Speech Echo - WebSocket example.

Listens for speech input and echoes it back to the caller.
Demonstrates actionHook event handling with session.on() and session.reply().

Usage:
    python websocket_app.py
"""

import asyncio

from jambonz_sdk.websocket import create_endpoint


async def main():
    make_service, server = await create_endpoint(port=3000)
    svc = make_service(path="/")

    async def handle_session(session):
        print(f"Incoming call: {session.call_sid}")

        # Register event handlers BEFORE sending verbs
        session.on("close", lambda code, reason: print(f"Session closed: {code}"))
        session.on("error", lambda err: print(f"Session error: {err}"))

        async def handle_echo(evt):
            reason = evt.get("reason", "")

            if reason == "speechDetected":
                transcript = (
                    evt.get("speech", {})
                    .get("alternatives", [{}])[0]
                    .get("transcript", "nothing")
                )
                session.say(text=f"You said: {transcript}.").gather(
                    input=["speech"],
                    actionHook="/echo",
                    timeout=10,
                    say={"text": "Please say something else."},
                )
                await session.reply()

            elif reason == "timeout":
                session.gather(
                    input=["speech"],
                    actionHook="/echo",
                    timeout=10,
                    say={"text": "Are you still there? I didn't hear anything."},
                )
                await session.reply()

            else:
                await session.reply()

        session.on("/echo", handle_echo)

        # Send initial verbs
        session.pause(length=1).gather(
            input=["speech"],
            actionHook="/echo",
            timeout=10,
            say={"text": "Please say something and I will echo it back to you."},
        )
        await session.send()

    svc.on("session:new", handle_session)

    print("Speech echo WebSocket app listening on port 3000")
    await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
