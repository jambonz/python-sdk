"""Voice Agent - Webhook (HTTP) example.

LLM-powered voice agent using the openai_s2s verb.
Demonstrates config + s2s verb pattern for webhook applications.

Note: S2S verbs are best suited for WebSocket transport. This webhook
example uses openai_s2s which requires the jambonz platform to maintain
the LLM connection. For full control, use the WebSocket version.

Usage:
    python webhook_app.py
"""

from aiohttp import web

from jambonz_sdk.webhook import WebhookResponse


async def handle_incoming(request: web.Request) -> web.Response:
    """Handle incoming call - start the voice agent."""
    jambonz = WebhookResponse()
    jambonz.config(
        synthesizer={"vendor": "elevenlabs", "voice": "Rachel", "language": "en-US"},
        recognizer={"vendor": "deepgram", "language": "en-US"},
    ).openai_s2s(
        model="gpt-4o-realtime",
        llmOptions={
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful voice assistant for Acme Corp. Be concise.",
                }
            ],
        },
        actionHook="/s2s-complete",
    )
    return web.json_response(jambonz.to_json())


async def handle_s2s_complete(request: web.Request) -> web.Response:
    """Handle S2S session completion."""
    body = await request.json()
    print(f"S2S complete: {body.get('completion_reason', 'unknown')}")
    jambonz = WebhookResponse()
    jambonz.say(text="Thank you for calling. Goodbye.").hangup()
    return web.json_response(jambonz.to_json())


async def handle_call_status(request: web.Request) -> web.Response:
    body = await request.json()
    print(f"Call {body.get('call_sid')} status: {body.get('call_status')}")
    return web.Response(status=200)


app = web.Application()
app.router.add_post("/incoming", handle_incoming)
app.router.add_post("/s2s-complete", handle_s2s_complete)
app.router.add_post("/call-status", handle_call_status)

if __name__ == "__main__":
    web.run_app(app, port=3000)
