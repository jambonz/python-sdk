"""jambonz Python SDK.

A Python SDK for the jambonz CPaaS platform, providing:

- **Webhook**: HTTP transport for building jambonz voice apps
- **WebSocket**: Persistent connection transport for real-time voice AI
- **Client**: REST API client for call control and management

Quick start (webhook)::

    from jambonz_sdk.webhook import WebhookResponse

    jambonz = WebhookResponse()
    jambonz.say(text="Hello!").hangup()
    response_body = jambonz.to_json()

Quick start (websocket)::

    from jambonz_sdk.websocket import create_endpoint

    make_service, server = await create_endpoint(port=3000)
    svc = make_service(path="/")

    def handle_session(session):
        session.say(text="Hello!").hangup()
        await session.send()

    svc.on("session:new", handle_session)

Quick start (REST client)::

    from jambonz_sdk.client import JambonzClient

    async with JambonzClient(base_url=url, account_sid=sid, api_key=key) as client:
        call_sid = await client.calls.create({...})
"""

__version__ = "0.1.0"

# Re-export main classes for convenience
from jambonz_sdk.client import JambonzClient
from jambonz_sdk.verb_builder import VerbBuilder
from jambonz_sdk.webhook import WebhookResponse

__all__ = [
    "JambonzClient",
    "VerbBuilder",
    "WebhookResponse",
    "__version__",
]
