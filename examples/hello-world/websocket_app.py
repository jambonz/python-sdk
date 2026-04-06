"""Hello World - WebSocket example.

A minimal jambonz application using persistent WebSocket connection.
Speaks a greeting and hangs up.

Usage:
    python websocket_app.py
"""

import asyncio

from jambonz_sdk.websocket import create_endpoint


async def main():
    make_service, server = await create_endpoint(port=3000)
    svc = make_service(path="/")

    async def handle_session(session):
        print(f"Incoming call: {session.call_sid} from {session.from_} to {session.to}")
        session.say(text="Hello! Welcome to our service. Goodbye!").hangup()
        await session.send()

    svc.on("session:new", handle_session)

    print("jambonz WebSocket app listening on port 3000")
    await asyncio.Future()  # Run forever


if __name__ == "__main__":
    asyncio.run(main())
