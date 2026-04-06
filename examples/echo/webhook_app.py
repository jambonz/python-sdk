"""Speech Echo - Webhook (HTTP) example.

Listens for speech input and echoes it back to the caller.
Demonstrates the gather verb with speech recognition and actionHook handling.

Usage:
    python webhook_app.py
"""

from aiohttp import web

from jambonz_sdk.webhook import WebhookResponse


async def handle_incoming(request: web.Request) -> web.Response:
    """Handle incoming call - prompt for speech."""
    jambonz = WebhookResponse()
    jambonz.pause(length=1).gather(
        input=["speech"],
        actionHook="/echo",
        timeout=10,
        say={"text": "Please say something and I will echo it back to you."},
    )
    return web.json_response(jambonz.to_json())


async def handle_echo(request: web.Request) -> web.Response:
    """Handle gather result - echo speech back."""
    body = await request.json()
    jambonz = WebhookResponse()

    reason = body.get("reason", "")

    if reason == "speechDetected":
        transcript = (
            body.get("speech", {})
            .get("alternatives", [{}])[0]
            .get("transcript", "nothing")
        )
        jambonz.say(text=f"You said: {transcript}.").gather(
            input=["speech"],
            actionHook="/echo",
            timeout=10,
            say={"text": "Please say something else."},
        )
    elif reason == "timeout":
        jambonz.gather(
            input=["speech"],
            actionHook="/echo",
            timeout=10,
            say={"text": "Are you still there? I didn't hear anything."},
        )
    else:
        jambonz.say(text="Goodbye.").hangup()

    return web.json_response(jambonz.to_json())


async def handle_call_status(request: web.Request) -> web.Response:
    body = await request.json()
    print(f"Call {body.get('call_sid')} status: {body.get('call_status')}")
    return web.Response(status=200)


app = web.Application()
app.router.add_post("/incoming", handle_incoming)
app.router.add_post("/echo", handle_echo)
app.router.add_post("/call-status", handle_call_status)

if __name__ == "__main__":
    web.run_app(app, port=3000)
