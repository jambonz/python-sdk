# jambonz Python SDK — Agent Toolkit

jambonz is an open-source CPaaS (Communications Platform as a Service) for building voice and messaging applications. It handles telephony infrastructure — SIP, carriers, phone numbers, media processing — so you can focus on application logic.

This is the **Python SDK** (`jambonz-sdk`). It provides the same functionality as the Node.js `@jambonz/sdk` package, following Python idioms and conventions.

## How jambonz Applications Work

A jambonz application controls phone calls by returning **arrays of verbs** — JSON instructions that execute sequentially. The runtime processes each verb in order: speak text, play audio, collect input, dial a number, connect to an AI model, etc.

### The Webhook Lifecycle

1. An incoming call arrives. jambonz invokes your application's URL with call details.
2. Your application returns a JSON array of verbs.
3. jambonz executes the verbs in order.
4. When a verb with an `actionHook` completes (e.g. `gather` collects speech), jambonz invokes the actionHook URL with the result.
5. The actionHook response (a new verb array) replaces the remaining verb stack.
6. This continues until the call ends or a `hangup` verb is executed.

### Transport Modes

- **Webhook (HTTP)**: Your server receives POST requests and returns JSON verb arrays. Stateless and simple.
- **WebSocket**: Persistent bidirectional connection. Required for real-time LLM agents, audio streaming, and TTS token streaming.

**IMPORTANT**: Any application that uses a speech-to-speech verb (`openai_s2s`, `google_s2s`, `deepgram_s2s`, `ultravox_s2s`, `elevenlabs_s2s`, `s2s`, or `pipeline`) MUST use WebSocket transport.

## Core Verbs

### Audio & Speech
- **say** — Speak text using TTS. Supports SSML, streaming, multiple voices.
- **play** — Play an audio file from a URL.
- **gather** — Collect speech (STT) and/or DTMF input.

### AI & Real-time
- **openai_s2s** / **google_s2s** / **deepgram_s2s** / **ultravox_s2s** / **elevenlabs_s2s** — Vendor-specific LLM voice conversation.
- **s2s** — Generic LLM voice conversation (use when vendor is determined at runtime).
- **pipeline** — Higher-level voice AI pipeline with integrated turn detection.
- **dialogflow** — Google Dialogflow agent.
- **stream** — Stream raw audio to a websocket endpoint.
- **transcribe** — Real-time call transcription.

### Call Control
- **dial** — Place an outbound call and bridge.
- **conference** — Multi-party conference room.
- **enqueue** / **dequeue** — Call queuing.
- **hangup** — End the call.
- **redirect** — Transfer control to a different webhook.
- **pause** — Wait for a specified duration.

### SIP
- **sip_decline** — Reject with a SIP error (`sip:decline` in JSON).
- **sip_request** — Send a SIP request within the dialog (`sip:request` in JSON).
- **sip_refer** — Transfer via SIP REFER (`sip:refer` in JSON).

### Utility
- **config** — Set session-level defaults (TTS, STT, VAD, etc.).
- **tag** — Attach metadata to the call.
- **dtmf** — Send DTMF tones.
- **dub** — Mix auxiliary audio tracks.
- **message** — Send SMS/MMS.
- **alert** — Send SIP 180 with Alert-Info.
- **answer** — Explicitly answer the call.
- **leave** — Leave a conference or queue.

### Verb Synonyms and Rules

1. **Always use `stream`, never `listen`** — they are synonyms; `stream` is preferred.
2. **Use vendor-specific shortcut when the vendor is known** — `openai_s2s`, `google_s2s`, etc.
3. **Use `s2s` when vendor is dynamic** — e.g., vendor comes from env var.
4. **Never use `llm` in generated code** — it is a legacy name.

## Using the SDK

Install: `pip install jambonz-sdk`

### Webhook Application (HTTP)

Use `WebhookResponse` from `jambonz_sdk.webhook`. Works with any ASGI/WSGI framework. Examples use aiohttp:

```python
from aiohttp import web
from jambonz_sdk.webhook import WebhookResponse

async def handle_incoming(request: web.Request) -> web.Response:
    body = await request.json()
    jambonz = WebhookResponse()
    jambonz.say(text="Hello! Welcome to our service.").gather(
        input=["speech", "digits"],
        actionHook="/handle-input",
        numDigits=1,
        timeout=10,
        say={"text": "Press 1 for sales or 2 for support."},
    ).say(text="No input received. Goodbye.").hangup()
    return web.json_response(jambonz.to_json())

async def handle_input(request: web.Request) -> web.Response:
    body = await request.json()
    digits = body.get("digits", "")
    jambonz = WebhookResponse()
    jambonz.say(text=f"You pressed {digits}. Goodbye.").hangup()
    return web.json_response(jambonz.to_json())

async def handle_call_status(request: web.Request) -> web.Response:
    body = await request.json()
    print(f"Call {body.get('call_sid')} status: {body.get('call_status')}")
    return web.Response(status=200)

app = web.Application()
app.router.add_post("/incoming", handle_incoming)
app.router.add_post("/handle-input", handle_input)
app.router.add_post("/call-status", handle_call_status)

if __name__ == "__main__":
    web.run_app(app, port=3000)
```

### WebSocket Application

Use `create_endpoint` from `jambonz_sdk.websocket`. Handles both control and audio WebSocket protocols:

```python
import asyncio
from jambonz_sdk.websocket import create_endpoint

async def main():
    make_service, runner = await create_endpoint(port=3000)
    svc = make_service(path="/")

    async def handle_session(session):
        print(f"Incoming call: {session.call_sid}")
        session.say(text="Hello from jambonz over WebSocket!").hangup()
        await session.send()

    svc.on("session:new", handle_session)
    print("Listening on port 3000")
    await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())
```

### WebSocket actionHook Events

In WebSocket mode, `actionHook` values become event names. Register handlers with `session.on()` and respond with `session.reply()`:

```python
async def handle_session(session):
    async def on_echo(evt):
        reason = evt.get("reason", "")
        if reason == "speechDetected":
            transcript = evt.get("speech", {}).get("alternatives", [{}])[0].get("transcript", "")
            session.say(text=f"You said: {transcript}.")
            session.gather(input=["speech"], actionHook="/echo", timeout=10,
                           say={"text": "Say something else."})
        else:
            session.say(text="Goodbye.").hangup()
        await session.reply()  # reply(), NOT send()

    session.on("/echo", on_echo)
    session.gather(input=["speech"], actionHook="/echo", timeout=10,
                   say={"text": "Say something and I will echo it."})
    await session.send()  # send() for initial response only

svc.on("session:new", handle_session)
```

**`.send()` vs `.reply()`:**
- `.send()` — Use ONCE for the initial verb array (response to `session:new`).
- `.reply()` — Use for ALL subsequent responses (actionHook events).

### REST API Client

```python
from jambonz_sdk.client import JambonzClient

async with JambonzClient(
    base_url="https://api.jambonz.us",
    account_sid="your-account-sid",
    api_key="your-api-key",
) as client:
    # Create outbound call
    call_sid = await client.calls.create({
        "from": "+15085551212",
        "to": {"type": "phone", "number": "+15085551213"},
        "call_hook": "/incoming",
    })

    # Mid-call control
    await client.calls.whisper(call_sid, {"verb": "say", "text": "Supervisor listening."})
    await client.calls.mute(call_sid, "mute")
    await client.calls.redirect(call_sid, "https://example.com/new-flow")
    await client.calls.update(call_sid, {"call_status": "completed"})
```

## Application Environment Variables

jambonz applications use **env vars** (NOT `os.environ`) for per-application configuration. Two required steps:

### Step 1: Declare (for portal discovery)

**WebSocket** — pass `env_vars` to `create_endpoint`:
```python
env_vars = {
    "GREETING": {"type": "string", "description": "Greeting message", "default": "Hello!"},
    "LANGUAGE": {"type": "string", "description": "TTS language", "default": "en-US"},
}
make_service, runner = await create_endpoint(port=3000, env_vars=env_vars)
```

**Webhook** — use `env_vars_middleware` for OPTIONS responses:
```python
from jambonz_sdk.webhook import env_vars_middleware

async def handle_options(request):
    return web.json_response(env_vars_middleware(env_vars))

app.router.add_route("OPTIONS", "/incoming", handle_options)
```

### Step 2: Read at runtime

**WebSocket**: `session.data.get("env_vars", {}).get("GREETING", "Hello!")`

**Webhook**: `body.get("env_vars", {}).get("GREETING", "Hello!")`

Env var schema properties:

| Property | Description |
|----------|-------------|
| `type` | `"string"` \| `"number"` \| `"boolean"` |
| `description` | Human-readable label |
| `required` | Whether user must provide a value |
| `default` | Pre-filled default |
| `enum` | Allowed values (renders as dropdown) |
| `obscure` | Mask in portal UI (for secrets) |
| `uiHint` | `"input"`, `"textarea"`, or `"filepicker"` |
| `jambonzResource` | Populate from jambonz account data (e.g., `"carriers"`) |

## Mid-Call Control

### WebSocket (inject commands)

```python
await session.inject_mute("mute")
await session.inject_whisper({"verb": "say", "text": "5 minutes remaining."})
await session.inject_record("startCallRecording", {"siprecServerURL": "sip:rec@example.com"})
await session.inject_record("stopCallRecording")
await session.inject_dtmf("1234#")
await session.inject_tag({"supervisor": "jane"})
await session.inject_redirect("/new-flow")
await session.inject_listen_status("pause")
```

### REST API (webhook apps)

```python
await client.calls.whisper(call_sid, {"verb": "say", "text": "Hello"})
await client.calls.mute(call_sid, "mute")
await client.calls.redirect(call_sid, "https://example.com/new")
await client.calls.update(call_sid, {"call_status": "completed"})
await client.calls.update_pipeline(call_sid, {"type": "update_instructions", "instructions": "New prompt"})
```

## TTS Token Streaming

Stream LLM tokens to jambonz for incremental TTS (lowest-latency playback):

```python
await session.send_tts_tokens("Hello, ")
await session.send_tts_tokens("how can I help you today?")
await session.flush_tts_tokens()
# To cancel:
await session.clear_tts_tokens()
```

## Pipeline Updates

Update a running pipeline mid-conversation:

```python
await session.update_pipeline({"type": "update_instructions", "instructions": "Now help with billing."})
await session.update_pipeline({"type": "inject_context", "messages": [{"role": "system", "content": "Customer is Gold tier."}]})
await session.update_pipeline({"type": "update_tools", "tools": [...]})
await session.update_pipeline({"type": "generate_reply", "user_input": "Override", "interrupt": True})
```

## Tool Output (Pipeline)

When the LLM requests a tool call, return the result:

```python
session.on("llm:tool-call", async def on_tool(evt):
    result = await my_tool(evt["name"], evt["arguments"])
    await session.tool_output(evt["tool_call_id"], result)
    await session.reply()
)
```

## Audio Streaming (Listen/Stream)

Stream raw audio between jambonz and your app via a separate WebSocket:

```python
make_service, runner = await create_endpoint(port=3000)
svc = make_service(path="/")
audio_svc = make_service.audio(path="/audio")

async def handle_session(session):
    session.stream(url="/audio", sampleRate=16000, mixType="mono",
                   metadata={"purpose": "recording"}, actionHook="/done")
    await session.send()

svc.on("session:new", handle_session)

def on_audio_connection(stream):
    print(f"Audio from call {stream.call_sid}, rate={stream.sample_rate}")
    stream.on("audio", lambda pcm: process_audio(pcm))
    # Send audio back (streaming mode):
    # await stream.send_audio(pcm_bytes)
    # Send complete clip (non-streaming):
    # await stream.play_audio(base64_content, audio_content_type="raw", sample_rate=16000)

audio_svc.on("connection", on_audio_connection)
```

## WebSocket Protocol Reference

### Messages: jambonz → app

| Type | Description |
|------|-------------|
| `session:new` | New call session |
| `session:redirect` | Call redirected to this app |
| `verb:hook` | actionHook fired (gather completed, etc.) — respond with `.reply()` |
| `verb:status` | Informational (no reply needed) |
| `call:status` | Call state changed |
| `llm:tool-call` | LLM requested a tool call |
| `llm:event` | LLM lifecycle event |
| `tts:tokens-result` | Ack for TTS token message |
| `tts:streaming-event` | TTS streaming lifecycle event |

### Messages: app → jambonz

| Type | Description |
|------|-------------|
| `ack` | Acknowledge with verbs (`send()` / `reply()`) |
| `command` | Inject command (`inject_mute()`, etc.) |
| `llm:tool-output` | Tool call result (`tool_output()`) |
| `tts:tokens` | Stream TTS text (`send_tts_tokens()`) |
| `tts:flush` | End TTS stream (`flush_tts_tokens()`) |
| `pipeline:update` | Pipeline update (`update_pipeline()`) |

## Common Patterns

### IVR Menu
```python
jambonz = WebhookResponse()
jambonz.say(text="Welcome.").gather(
    input=["speech", "digits"], actionHook="/menu", numDigits=1, timeout=10,
    say={"text": "Press 1 for sales, 2 for support."},
).say(text="No input. Goodbye.").hangup()
```

### Voice Agent (Pipeline)
```python
session.pipeline(
    stt={"vendor": "deepgram", "language": "en-US"},
    tts={"vendor": "cartesia", "voice": "sonic-english"},
    llm={"vendor": "openai", "model": "gpt-4o", "llmOptions": {
        "messages": [{"role": "system", "content": "You are a helpful assistant."}]
    }},
    turnDetection="krisp",
    bargeIn={"enable": True},
    actionHook="/pipeline-done",
    eventHook="/events",
    toolHook="/tools",
)
await session.send()
```

### ElevenLabs S2S
```python
session.elevenlabs_s2s(
    auth={"agent_id": "your-agent-id", "api_key": "your-api-key"},
    llmOptions={},
    actionHook="/s2s-complete",
    eventHook="/event",
    events=["all"],
)
await session.send()
```

### Dial with Fallback
```python
jambonz.say(text="Connecting you now.").dial(
    target=[{"type": "phone", "number": "+15085551212"}],
    answerOnBridge=True, timeout=30, actionHook="/dial-result",
).say(text="Agent unavailable. Goodbye.").hangup()
```

## Key Concepts

- **Verb**: A JSON object with a `verb` property that tells jambonz what to do.
- **ActionHook**: URL (webhook) or event name (WebSocket) invoked when a verb completes.
- **Synthesizer**: TTS config (vendor, voice, language).
- **Recognizer**: STT config (vendor, language, model).
- **Target**: A call destination (phone, SIP, user, Teams).
- **Session**: A single phone call over WebSocket.
- **Inject Command**: Async mid-call modification (immediate, doesn't replace verb stack).

## SDK Architecture

The SDK auto-generates verb methods from `specs.json` (from `@jambonz/verb-specifications`). When the spec changes, the SDK automatically picks up new parameters:

1. `specs.json` — bundled verb/component specifications (synced from upstream)
2. `verb_registry.py` — maps spec entries to Python methods + synonyms
3. `verb_builder.py` — generates methods at import time from specs + registry
4. `WebhookResponse` and `Session` both extend `VerbBuilder`

To add a new verb: add one `VerbDef` entry in `verb_registry.py`.
