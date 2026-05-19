# jambonz Python SDK

Python SDK for the [jambonz](https://jambonz.org) CPaaS platform.

## Installation

```bash
pip install jambonz-python-sdk
```

## Quick Start

### Webhook (HTTP)

```python
from aiohttp import web
from jambonz_sdk.webhook import WebhookResponse

async def handle_incoming(request: web.Request) -> web.Response:
    jambonz = WebhookResponse()
    jambonz.say(text="Hello!").gather(
        input=["speech"],
        actionHook="/handle-input",
        timeout=10,
        say={"text": "Please say something."},
    ).hangup()
    return web.json_response(jambonz.to_json())

app = web.Application()
app.router.add_post("/incoming", handle_incoming)
web.run_app(app, port=3000)
```

### Typed input (recommended)

Every verb method also accepts a pydantic model for full IDE autocomplete and
typo-proof nested fields:

```python
from jambonz_sdk.webhook import WebhookResponse
from jambonz_sdk.verbs import Gather, Say
from jambonz_sdk.components import Recognizer

jambonz = WebhookResponse()
jambonz.gather(Gather(
    input=["speech", "digits"],
    action_hook="/menu",
    timeout=15,
    num_digits=1,
    say=Say(text="Press 1 for sales, 2 for support"),
    recognizer=Recognizer(vendor="deepgram", language="en-US"),
)).hangup()
```

Dict and kwargs styles both still work and coerce automatically, so existing
apps keep running unchanged. Mix and match as you like:

```python
jambonz.gather(
    input=["speech"],
    say=Say(text="Hello"),              # model
    recognizer={"vendor": "google"},    # dict
)
```

Unknown fields, missing required fields, wrong types, and violated cross-field
rules (e.g. `numDigits` combined with `minDigits`/`maxDigits`) raise
`pydantic.ValidationError` at construction time — no more hunting silent
failures after a round-trip to the jambonz server.

### WebSocket

```python
import asyncio
from jambonz_sdk.websocket import create_endpoint

async def main():
    make_service, runner = await create_endpoint(port=3000)
    svc = make_service(path="/")

    async def handle_session(session):
        session.say(text="Hello!").hangup()
        await session.send()

    svc.on("session:new", handle_session)
    await asyncio.Future()

asyncio.run(main())
```

### REST Client

```python
from jambonz_sdk.client import JambonzClient

async with JambonzClient(
    base_url="https://api.jambonz.us",
    account_sid="your-account-sid",
    api_key="your-api-key",
) as client:
    call_sid = await client.calls.create({
        "from": "+15085551212",
        "to": {"type": "phone", "number": "+15085551213"},
        "call_hook": "/incoming",
    })
```

## How It Works

### Spec-driven verb generation

The SDK does **not** hardcode verb method signatures. Instead, verb methods (`.say()`, `.gather()`, `.dial()`, `.agent()`, etc.) are **auto-generated at import time** from [JSON Schema](https://github.com/jambonz/schema) files — the same schemas used by the Node.js SDK and the jambonz server.

**What this means:**

- When the schema adds a new property to a verb, the SDK picks it up automatically — no code change needed
- Every method has **real typed parameters** (not `**kwargs: Any`) so IDEs show autocomplete and type hints
- Verb synonyms (`stream` ↔ `listen`, `openai_s2s` → `llm` with `vendor: "openai"`) are handled by the registry

### Typed pydantic models

Alongside the schema-driven method signatures, the SDK ships pydantic v2 models
generated from the same JSON Schemas. They live under `jambonz_sdk.verbs` and
`jambonz_sdk.components` and can be passed directly to any verb method.

These models are a build artifact — produced by `scripts/regen_models.py`
from the bundled schemas — and get checked into the repo so end users don't
need codegen tools to install the SDK.

### Updating the schema

```bash
# Download the pinned version from @jambonz/schema:
python scripts/sync_schema.py

# Regenerate the typed pydantic models so they match:
python scripts/regen_models.py

# Regenerate the .pyi stubs so IDE autocomplete stays in sync:
python scripts/generate_stubs.py
```

If a **new verb** was added (not just new properties), add one line to `verb_registry.py`:

```python
VerbDef("new_verb", "new_verb", doc="Description.")
```

## Features

- **All 31 jambonz verbs**: say, play, gather, dial, conference, enqueue/dequeue, hangup, pause, redirect, config, tag, dtmf, dub, message, alert, answer, leave, listen/stream, transcribe, openai_s2s, google_s2s, deepgram_s2s, elevenlabs_s2s, ultravox_s2s, s2s, llm, dialogflow, agent, sip_decline, sip_request, sip_refer
- **Fluent chainable API**: `.say(...).gather(...).hangup()`
- **Webhook transport**: `WebhookResponse` for HTTP apps (works with aiohttp, FastAPI, Flask, etc.)
- **WebSocket transport**: `create_endpoint` with `Session`, event handling, `send()`/`reply()`
- **REST client**: `JambonzClient` with calls, conferences, queues, mid-call control
- **Audio streaming**: Bidirectional audio via `AudioStream`
- **Mid-call control**: inject commands (mute, whisper, record, DTMF, tag)
- **TTS token streaming**: `send_tts_tokens()` / `flush_tts_tokens()`
- **Agent updates**: `update_agent()` for mid-conversation LLM changes
- **Signature verification**: HMAC-SHA256 webhook signature validation
- **Env vars**: Portal discovery via OPTIONS + runtime reading

## Examples

See the [`examples/`](examples/) directory:

| Example | Webhook | WebSocket | Description |
|---------|---------|-----------|-------------|
| hello-world | [webhook](examples/hello-world/webhook_app.py) | [websocket](examples/hello-world/websocket_app.py) | Minimal greeting |
| echo | [webhook](examples/echo/webhook_app.py) | [websocket](examples/echo/websocket_app.py) | Speech echo with gather |
| ivr-menu | [webhook](examples/ivr-menu/webhook_app.py) | — | IVR menu with speech + DTMF |
| voice-agent | [webhook](examples/voice-agent/webhook_app.py) | [websocket](examples/voice-agent/websocket_app.py) | LLM agent with tool calls |
| dial | [webhook](examples/dial/webhook_app.py) | — | Outbound dial with fallback |
| listen-record | [webhook](examples/listen-record/webhook_app.py) | [websocket](examples/listen-record/websocket_app.py) | Audio recording |

## Development

```bash
# Create venv and install
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# Run tests
pytest tests/unit/          # Fast unit tests
pytest tests/integration/   # Real server tests
pytest                      # All tests

# Sync schema from upstream and regenerate pydantic models + stubs
python scripts/sync_schema.py
python scripts/regen_models.py
python scripts/generate_stubs.py
```

## License

MIT
