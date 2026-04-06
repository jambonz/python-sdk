"""Hello World - Webhook (HTTP) example.

A minimal jambonz application using aiohttp as the web framework.
Speaks a greeting and hangs up.

Usage:
    python webhook_app.py
"""

from aiohttp import web

from jambonz_sdk.webhook import WebhookResponse


async def handle_incoming(request: web.Request) -> web.Response:
    """Handle incoming call."""
    jambonz = WebhookResponse()
    jambonz.say(text="Hello! Welcome to our service. Goodbye!").hangup()
    return web.json_response(jambonz.to_json())


async def handle_call_status(request: web.Request) -> web.Response:
    """Handle call status events."""
    body = await request.json()
    print(f"Call {body.get('call_sid')} status: {body.get('call_status')}")
    return web.Response(status=200)


app = web.Application()
app.router.add_post("/incoming", handle_incoming)
app.router.add_post("/call-status", handle_call_status)

if __name__ == "__main__":
    web.run_app(app, port=3000)
