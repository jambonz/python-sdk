"""Dial - Webhook (HTTP) example.

Simple outbound dial to a phone number with fallback messaging.
Demonstrates the dial verb with answerOnBridge and actionHook.

Usage:
    python webhook_app.py
"""

from aiohttp import web

from jambonz_sdk.webhook import WebhookResponse


async def handle_incoming(request: web.Request) -> web.Response:
    """Handle incoming call - dial out to an agent."""
    jambonz = WebhookResponse()
    jambonz.say(text="Please hold while I connect you to an agent.").dial(
        target=[{"type": "phone", "number": "+15085551212"}],
        answerOnBridge=True,
        timeout=30,
        actionHook="/dial-result",
    ).say(text="Sorry, the agent is not available right now. Please try again later. Goodbye.").hangup()
    return web.json_response(jambonz.to_json())


async def handle_dial_result(request: web.Request) -> web.Response:
    """Handle dial completion."""
    body = await request.json()
    jambonz = WebhookResponse()

    dial_status = body.get("dial_call_status", "")
    duration = body.get("duration", 0)
    print(f"Dial result: status={dial_status}, duration={duration}s")

    jambonz.say(text="The call has ended. Thank you. Goodbye.").hangup()
    return web.json_response(jambonz.to_json())


async def handle_call_status(request: web.Request) -> web.Response:
    body = await request.json()
    print(f"Call {body.get('call_sid')} status: {body.get('call_status')}")
    return web.Response(status=200)


app = web.Application()
app.router.add_post("/incoming", handle_incoming)
app.router.add_post("/dial-result", handle_dial_result)
app.router.add_post("/call-status", handle_call_status)

if __name__ == "__main__":
    web.run_app(app, port=3000)
