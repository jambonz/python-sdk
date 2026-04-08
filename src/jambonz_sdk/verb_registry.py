"""Verb registry — the single source of truth for mapping spec entries to SDK methods.

This module defines which entries in the JSON Schema files are top-level verbs
(as opposed to nested component types), their Python method names, docstrings,
and any synonym/alias transforms.

When the spec adds a new verb, add one entry here — the VerbBuilder will
automatically gain a typed method for it.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class VerbDef:
    """Definition of a single verb method on VerbBuilder.

    Attributes:
        spec_name: The schema identifier (e.g., ``"say"``, ``"sip:decline"``).
        method_name: The Python method name (e.g., ``"say"``, ``"sip_decline"``).
        json_verb: The ``verb`` value in the output JSON. Defaults to ``spec_name``.
        doc: One-line docstring for the generated method.
        inject: Properties to inject into the verb data (for synonyms like
            ``openai_s2s`` → ``llm`` with ``vendor: "openai"``).
    """

    spec_name: str
    method_name: str
    json_verb: str = ""
    doc: str = ""
    inject: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.json_verb:
            object.__setattr__(self, "json_verb", self.spec_name)


# ── Verb definitions ────────────────────────────────────────────────
# Each entry here creates a method on VerbBuilder.
# Order matches the categories in the jambonz documentation.

VERB_DEFS: list[VerbDef] = [
    # Audio & Speech
    VerbDef("say", "say", doc="Speak text using TTS."),
    VerbDef("play", "play", doc="Play an audio file from a URL."),
    VerbDef("gather", "gather", doc="Collect speech (STT) and/or DTMF input."),

    # AI & Real-time
    VerbDef("llm", "openai_s2s", json_verb="openai_s2s",
            doc="Connect caller to OpenAI for real-time voice conversation.",
            inject={"vendor": "openai"}),
    VerbDef("llm", "google_s2s", json_verb="google_s2s",
            doc="Connect caller to Google for real-time voice conversation.",
            inject={"vendor": "google"}),
    VerbDef("llm", "deepgram_s2s", json_verb="deepgram_s2s",
            doc="Connect caller to Deepgram for real-time voice conversation.",
            inject={"vendor": "deepgram"}),
    VerbDef("llm", "elevenlabs_s2s", json_verb="elevenlabs_s2s",
            doc="Connect caller to ElevenLabs Conversational AI agent.",
            inject={"vendor": "elevenlabs"}),
    VerbDef("llm", "ultravox_s2s", json_verb="ultravox_s2s",
            doc="Connect caller to Ultravox for real-time voice conversation.",
            inject={"vendor": "ultravox"}),
    VerbDef("llm", "s2s", json_verb="s2s",
            doc="Generic S2S verb (use when vendor is determined at runtime)."),
    VerbDef("llm", "llm", doc="Legacy LLM verb (prefer s2s or vendor-specific shortcuts)."),
    VerbDef("dialogflow", "dialogflow", doc="Connect caller to Google Dialogflow agent."),
    VerbDef("pipeline", "pipeline", doc="Integrated STT → LLM → TTS voice AI pipeline."),

    # Audio Streaming
    VerbDef("listen", "listen", doc="Stream real-time audio to a websocket endpoint."),
    VerbDef("listen", "stream", json_verb="stream",
            doc="Stream real-time audio (preferred alias for listen)."),
    VerbDef("transcribe", "transcribe", doc="Enable real-time call transcription."),

    # Call Control
    VerbDef("dial", "dial", doc="Place outbound call and bridge to current caller."),
    VerbDef("conference", "conference", doc="Place caller into a multi-party conference room."),
    VerbDef("enqueue", "enqueue", doc="Place caller into a named call queue."),
    VerbDef("dequeue", "dequeue", doc="Remove caller from a queue and bridge."),
    VerbDef("hangup", "hangup", doc="Terminate the call."),
    VerbDef("redirect", "redirect", doc="Transfer control to a different webhook URL."),
    VerbDef("pause", "pause", doc="Pause execution for a specified duration."),

    # SIP
    VerbDef("sip:decline", "sip_decline", doc="Reject incoming call with a SIP error response."),
    VerbDef("sip:request", "sip_request", doc="Send a SIP request within the current dialog."),
    VerbDef("sip:refer", "sip_refer", doc="Send a SIP REFER for call transfer."),

    # Utility
    VerbDef("config", "config", doc="Set session-level defaults."),
    VerbDef("tag", "tag", doc="Attach metadata to the call."),
    VerbDef("dtmf", "dtmf", doc="Send DTMF tones."),
    VerbDef("dub", "dub", doc="Manage audio dubbing tracks."),
    VerbDef("message", "message", doc="Send SMS/MMS message."),
    VerbDef("alert", "alert", doc="Send SIP 180 with Alert-Info header."),
    VerbDef("answer", "answer", doc="Explicitly answer the call."),
    VerbDef("leave", "leave", doc="Leave a conference or queue."),
]
