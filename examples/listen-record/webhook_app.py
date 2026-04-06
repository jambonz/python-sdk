"""Listen/Record - Webhook (HTTP) example.

Records call audio using the listen verb to stream audio to an external
WebSocket endpoint.

Note: The audio WebSocket handler must be run separately. For a fully
integrated solution, use the WebSocket example which handles both control
and audio on the same server.

Usage:
    python webhook_app.py
"""

from aiohttp import web

from jambonz_sdk.webhook import WebhookResponse


async def handle_incoming(request: web.Request) -> web.Response:
    """Handle incoming call - start recording."""
    jambonz = WebhookResponse()
    jambonz.answer().say(
        text="This call will be recorded. I will record for up to 30 seconds. Press pound to stop."
    ).listen(
        url="wss://your-server.example.com/audio-stream",
        actionHook="/listen-done",
        sampleRate=16000,
        mixType="mono",
        finishOnKey="#",
        maxLength=30,
        playBeep=True,
        metadata={"purpose": "recording"},
    ).say(text="Recording complete. Goodbye.").hangup()
    return web.json_response(jambonz.to_json())


async def handle_listen_done(request: web.Request) -> web.Response:
    """Handle listen completion."""
    body = await request.json()
    print(f"Listen done: {body.get('reason', 'unknown')}")
    jambonz = WebhookResponse()
    jambonz.say(text="Recording complete. Thank you. Goodbye.").hangup()
    return web.json_response(jambonz.to_json())


async def handle_call_status(request: web.Request) -> web.Response:
    body = await request.json()
    print(f"Call {body.get('call_sid')} status: {body.get('call_status')}")
    return web.Response(status=200)


app = web.Application()
app.router.add_post("/incoming", handle_incoming)
app.router.add_post("/listen-done", handle_listen_done)
app.router.add_post("/call-status", handle_call_status)

if __name__ == "__main__":
    web.run_app(app, port=3000)
