# jambonz Python SDK

## Project Overview

This is the Python SDK for the [jambonz](https://jambonz.org) CPaaS platform, a direct port of the Node.js SDK (`@jambonz/sdk`) at `/Users/xhoaluu/jambonz/node-sdk`.

jambonz is an open-source Communications Platform as a Service for building voice and messaging applications. The SDK provides three main modules:

1. **Webhook** - HTTP transport for building jambonz apps with any ASGI/WSGI framework
2. **WebSocket** - Persistent connection transport for real-time voice AI apps
3. **Client** - REST API client for call control, conferences, and queues

## Architecture

### Package Layout

```
src/jambonz_sdk/
├── __init__.py          # Public API re-exports
├── verbs/               # Public re-exports of generated verb models (Gather, Say, …)
├── components/          # Public re-exports of generated component models (Recognizer, …)
├── _models/             # Pydantic v2 models
│   ├── base.py          # JambonzModel base class (alias/serialization config)
│   ├── _registry.py     # JSON verb name → generated model class lookup
│   ├── _generated/      # Auto-generated from JSON Schemas — do not edit
│   │   ├── verbs/
│   │   ├── components/
│   │   └── callbacks/
│   └── _patches/        # Hand-written supplements (currently empty stub)
├── types/
│   ├── __init__.py
│   ├── components.py    # Legacy TypedDicts (still used internally)
│   ├── verbs.py         # Legacy verb TypedDicts
│   ├── rest.py          # REST API request/response types
│   └── session.py       # Call session & WebSocket message types
├── verb_builder.py      # VerbBuilder — verb methods route through the generated models
├── verb_registry.py     # Verb definitions: maps spec entries → Python methods
├── webhook/
│   ├── __init__.py
│   ├── response.py      # WebhookResponse class
│   └── middleware.py     # Signature verification & env vars middleware
├── websocket/
│   ├── __init__.py
│   ├── endpoint.py      # create_endpoint factory & HTTP upgrade handler
│   ├── session.py       # Session class (extends VerbBuilder)
│   ├── client.py        # WsClient - manages services on a path
│   ├── router.py        # WsRouter - path-based routing
│   ├── audio_client.py  # AudioClient - audio protocol handler
│   └── audio_stream.py  # AudioStream - per-call audio handler
├── client/
│   ├── __init__.py
│   └── api.py           # JambonzClient, CallsResource, ConferencesResource, QueuesResource
└── _signature.py        # HMAC-SHA256 webhook signature verification
```

### Key Design Patterns

- **Transport-agnostic verb building**: Same verb methods on both `WebhookResponse` and `Session`
- **Fluent/chainable API**: All verb methods return `self` for method chaining
- **Typed pydantic models**: Every verb and component has a generated pydantic v2 model. Verb methods accept a typed model, a raw dict, or kwargs interchangeably — all three are validated through the model and serialized via `model_dump(mode="json", by_alias=True, exclude_none=True)`. Typos and missing required fields fail at construction time rather than at the jambonz server. Dict and kwargs styles remain for backwards compatibility.
- **Auto-generated verb methods**: VerbBuilder methods are generated at import time from JSON Schema files (`@jambonz/schema`) + `verb_registry.py`. When the schema changes, the SDK picks up new parameters automatically.
- **aiohttp for both HTTP and WebSocket**: Single dependency for REST client and WS transport

## Verb System

The SDK supports all 26+ jambonz verbs. Verb methods on VerbBuilder are **auto-generated** from JSON Schema files bundled from [`@jambonz/schema`](https://github.com/jambonz/schema).

### How verb generation works

1. `verb_registry.py` defines which spec entries are verbs, their Python method names, JSON verb names, and any synonym transforms
2. `verb_builder.py` loads JSON Schema files from `schema/verbs/` at import time and generates a method for each registry entry
3. Each generated method has typed parameters, docstrings, and required-field documentation — all derived from the schema
4. To add a new verb: add one `VerbDef` entry in `verb_registry.py` — no other changes needed

### Verb List

Audio/Speech: `say`, `play`, `gather`
AI/S2S: `openai_s2s`, `google_s2s`, `deepgram_s2s`, `elevenlabs_s2s`, `ultravox_s2s`, `s2s`, `llm`, `dialogflow`, `agent`
Call Control: `dial`, `conference`, `enqueue`, `dequeue`, `hangup`, `redirect`, `pause`
Audio Streaming: `listen`, `stream`, `transcribe`
SIP: `sip_decline`, `sip_request`, `sip_refer`
Utility: `config`, `tag`, `dtmf`, `dub`, `message`, `alert`, `answer`, `leave`

### Verb Synonyms

- `stream` and `listen` are synonyms (prefer `stream`)
- `s2s` and `llm` are synonyms (prefer `s2s`; use vendor-specific shortcuts when vendor is known)

### Python Method Naming

SIP verbs use underscores: `sip_decline()`, `sip_request()`, `sip_refer()` (maps to `sip:decline`, `sip:request`, `sip:refer` in JSON).

## JSON Schema Management

The SDK bundles JSON Schema files from `@jambonz/schema` (npm package / GitHub repo).
Schema files live at `src/jambonz_sdk/schema/` and are included in the wheel.

To update when the upstream schema changes:
```bash
# Download the pinned version
python scripts/sync_schema.py

# Download a specific version
python scripts/sync_schema.py v0.1.1

# Copy from a local directory
python scripts/sync_schema.py --local /path/to/schema

# After any schema sync, regenerate the pydantic models and the .pyi stubs:
python scripts/regen_models.py
python scripts/generate_stubs.py
```

Source: https://github.com/jambonz/schema

### Pydantic model regeneration

`scripts/regen_models.py` mirrors the bundled schemas, runs
`datamodel-code-generator`, applies post-gen patches (declared as tables
at the top of the script), then writes:

- `src/jambonz_sdk/_models/_generated/` — generated classes, committed
  as a build artifact so end users don't need codegen tools installed
- `src/jambonz_sdk/verbs/__init__.py` and
  `src/jambonz_sdk/components/__init__.py` — user-facing re-exports

Post-processing performs: (1) `BaseModel` → `JambonzModel`, (2) `AnyUrl` → `str`
(the schemas use `format: uri` even for relative paths like `/menu`),
(3) nested `dict[str, Any]` → real model classes on fields like `Gather.say`,
`Gather.play`, and `Agent.llm`, (4) appending cross-field validators to
specific classes (`Gather` digit-bounds rules). All these live as tables
in the script — extend them there, never edit generated files directly.

## AI Agent Support

### AGENTS.md

`AGENTS.md` is the comprehensive developer guide for AI agents working with this SDK.
It covers: verb system, webhook/WebSocket patterns, REST API, env vars, mid-call control,
TTS streaming, agent updates, audio streaming, and common application patterns.
AI coding agents should read AGENTS.md before generating jambonz Python application code.

### MCP Server

The `mcp.json` configures the jambonz MCP server at `https://mcp-server.jambonz.app/mcp`.
This provides two tools for AI agents:

1. **`jambonz_developer_toolkit`** — Returns the full developer guide and schema index. Call this FIRST before writing any jambonz code.
2. **`get_jambonz_schema`** — Fetch JSON Schema for any verb or component (e.g., `verb:say`, `component:synthesizer`, `callback:gather`, `guide:session-commands`).

## Node SDK Reference

The Node.js SDK source is at `/Users/xhoaluu/jambonz/node-sdk/typescript/src/`. Key files:
- `verb-builder.ts` - Base VerbBuilder class
- `webhook/response.ts` - WebhookResponse
- `websocket/session.ts` - WebSocket Session
- `websocket/endpoint.ts` - createEndpoint factory
- `client/api.ts` - REST API client
- `types/verbs.ts` - All verb type definitions
- `types/components.ts` - Shared component types

## Development

```bash
# Install dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=jambonz_sdk --cov-report=term-missing

# Type check
mypy src/

# Lint
ruff check src/ tests/
ruff format src/ tests/
```

## Conventions

- Python 3.10+ (use `|` union syntax, match statements where appropriate)
- Use `TypedDict` for verb/component schemas (mirrors JSON structure)
- Use `dataclass` for stateful objects (Session, JambonzClient)
- Async-first for WebSocket and REST client
- All public methods have type annotations
- Tests use pytest + pytest-asyncio
- Follow the exact same JSON field names as the Node SDK schemas (snake_case in Python maps to camelCase in JSON where needed — but jambonz schemas already use camelCase in JSON, so we keep camelCase as dict keys)
- Verb dict keys match the JSON schema exactly (e.g., `actionHook`, `earlyMedia`, `numDigits`)

## Testing Strategy

Tests are **spec-driven** — they validate behavior against the jambonz specification, not against the implementation.

```bash
pytest tests/unit/          # Fast, mocked — 253 tests
pytest tests/integration/   # Real servers — 26 tests
pytest                      # All 279 tests
```

### Unit tests (`tests/unit/`)
- `test_verb_builder.py` — Parametrized across all 31 verb defs: method existence, correct verb name, all spec properties pass through
- `test_webhook.py` — Webhook contract, HMAC-SHA256 signature protocol, env vars OPTIONS format
- `test_session.py` — WebSocket protocol messages: ack, command, tts:tokens, llm:tool-output, agent:update
- `test_ws_client.py` — Message routing: session:new, verb:hook dispatch, auto-reply, binary/JSON robustness
- `test_rest_client.py` — REST API contract: URL construction, HTTP methods, request bodies
- `test_audio_stream.py` — Audio protocol: raw PCM, playAudio JSON, marks, control commands

### Integration tests (`tests/integration/`)
- `test_webhook.py` — Real aiohttp server with IVR menu, actionHook routing, env vars discovery
- `test_websocket.py` — Real WebSocket connections: full protocol compliance, multi-step conversations, inject commands, TTS streaming, agent updates
