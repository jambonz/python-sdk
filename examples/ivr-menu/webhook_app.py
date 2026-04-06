"""IVR Menu - Webhook (HTTP) example.

Interactive voice response menu with speech and DTMF input.
Demonstrates multi-route webhook application with gather and routing logic.

Usage:
    python webhook_app.py
"""

from aiohttp import web

from jambonz_sdk.webhook import WebhookResponse


async def handle_incoming(request: web.Request) -> web.Response:
    """Handle incoming call - present the menu."""
    jambonz = WebhookResponse()
    jambonz.say(text="Welcome to Acme Corporation.").gather(
        input=["speech", "digits"],
        actionHook="/menu-selection",
        numDigits=1,
        timeout=10,
        bargein=True,
        say={"text": "Press 1 or say sales for sales. Press 2 or say support for support. Press 3 or say billing for billing."},
    ).say(text="We did not receive any input. Goodbye.").hangup()
    return web.json_response(jambonz.to_json())


async def handle_menu_selection(request: web.Request) -> web.Response:
    """Route based on user input."""
    body = await request.json()
    jambonz = WebhookResponse()

    digits = body.get("digits", "")
    transcript = (
        body.get("speech", {})
        .get("alternatives", [{}])[0]
        .get("transcript", "")
        .lower()
    )

    if digits == "1" or "sales" in transcript:
        jambonz.say(text="Connecting you to our sales team. Please hold.").dial(
            target=[{"type": "phone", "number": "+15085551001"}],
            answerOnBridge=True,
            timeout=30,
            actionHook="/dial-result",
        ).say(text="Sorry, no one is available right now. Goodbye.").hangup()

    elif digits == "2" or "support" in transcript:
        jambonz.say(text="Connecting you to technical support. Please hold.").dial(
            target=[{"type": "phone", "number": "+15085551002"}],
            answerOnBridge=True,
            timeout=30,
            actionHook="/dial-result",
        ).say(text="Sorry, no one is available right now. Goodbye.").hangup()

    elif digits == "3" or "billing" in transcript:
        jambonz.say(text="Connecting you to our billing department. Please hold.").dial(
            target=[{"type": "phone", "number": "+15085551003"}],
            answerOnBridge=True,
            timeout=30,
            actionHook="/dial-result",
        ).say(text="Sorry, no one is available right now. Goodbye.").hangup()

    else:
        jambonz.say(text="I didn't understand your selection.").redirect(
            actionHook="/incoming"
        )

    return web.json_response(jambonz.to_json())


async def handle_dial_result(request: web.Request) -> web.Response:
    """Handle dial completion."""
    body = await request.json()
    jambonz = WebhookResponse()
    dial_status = body.get("dial_call_status", "")
    print(f"Dial result: {dial_status}")
    jambonz.say(text="Thank you for calling. Goodbye.").hangup()
    return web.json_response(jambonz.to_json())


async def handle_call_status(request: web.Request) -> web.Response:
    body = await request.json()
    print(f"Call {body.get('call_sid')} status: {body.get('call_status')}")
    return web.Response(status=200)


app = web.Application()
app.router.add_post("/incoming", handle_incoming)
app.router.add_post("/menu-selection", handle_menu_selection)
app.router.add_post("/dial-result", handle_dial_result)
app.router.add_post("/call-status", handle_call_status)

if __name__ == "__main__":
    web.run_app(app, port=3000)
