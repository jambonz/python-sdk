"""Verb type definitions matching jambonz JSON schemas.

Each verb is a TypedDict where keys match the exact JSON schema property names.
The 'verb' key is always required and set to a literal string.
"""

from __future__ import annotations

from typing import Any, TypedDict, Union

from jambonz_sdk.types.components import (
    ActionHook,
    ActionHookDelayAction,
    Amd,
    Auth,
    BidirectionalAudio,
    FillerNoise,
    McpServer,
    Recognizer,
    Synthesizer,
    Target,
    Vad,
)


class SayVerb(TypedDict, total=False):
    """Speak text using TTS."""

    verb: str  # "say"
    id: str
    text: str | list[str]
    instructions: str
    stream: bool
    loop: int | str
    synthesizer: Synthesizer
    earlyMedia: bool
    disableTtsCache: bool
    closeStreamOnEmpty: bool


class PlayVerb(TypedDict, total=False):
    """Play an audio file."""

    verb: str  # "play"
    id: str
    url: str | list[str]
    loop: int | str
    earlyMedia: bool
    seekOffset: int | str
    timeoutSecs: int | str
    actionHook: ActionHook


class GatherVerb(TypedDict, total=False):
    """Collect speech/DTMF input."""

    verb: str  # "gather"
    id: str
    actionHook: ActionHook
    input: list[str]  # ["speech", "digits"]
    finishOnKey: str
    numDigits: int
    minDigits: int
    maxDigits: int
    interDigitTimeout: int
    speechTimeout: int
    timeout: int
    partialResultHook: ActionHook
    listenDuringPrompt: bool
    dtmfBargein: bool
    bargein: bool
    minBargeinWordCount: int
    recognizer: Recognizer
    say: SayVerb
    play: PlayVerb
    fillerNoise: FillerNoise
    actionHookDelayAction: ActionHookDelayAction


class DialVerb(TypedDict, total=False):
    """Place outbound call and bridge."""

    verb: str  # "dial"
    id: str
    target: list[Target]
    actionHook: ActionHook
    onHoldHook: ActionHook
    answerOnBridge: bool
    callerId: str
    callerName: str
    confirmHook: ActionHook
    referHook: ActionHook
    dialMusic: str
    dtmfCapture: dict[str, Any]
    dtmfHook: ActionHook
    headers: dict[str, str]
    anchorMedia: bool
    exitMediaPath: bool
    boostAudioSignal: int | str
    listen: dict[str, Any]
    stream: dict[str, Any]
    transcribe: dict[str, Any]
    timeLimit: int
    timeout: int
    proxy: str
    amd: Amd
    dub: list[dict[str, Any]]
    tag: dict[str, Any]
    forwardPAI: bool


class ListenVerb(TypedDict, total=False):
    """Stream audio to external websocket."""

    verb: str  # "listen"
    id: str
    url: str
    actionHook: ActionHook
    wsAuth: Auth
    mixType: str  # "mono" | "stereo" | "mixed"
    metadata: dict[str, Any]
    sampleRate: int
    finishOnKey: str
    maxLength: int
    passDtmf: bool
    playBeep: bool
    disableBidirectionalAudio: bool
    bidirectionalAudio: BidirectionalAudio
    timeout: int
    transcribe: dict[str, Any]
    earlyMedia: bool
    channel: int


class StreamVerb(TypedDict, total=False):
    """Stream audio to external websocket (alias for listen)."""

    verb: str  # "stream"
    id: str
    url: str
    actionHook: ActionHook
    wsAuth: Auth
    mixType: str
    metadata: dict[str, Any]
    sampleRate: int
    finishOnKey: str
    maxLength: int
    passDtmf: bool
    playBeep: bool
    disableBidirectionalAudio: bool
    bidirectionalAudio: BidirectionalAudio
    timeout: int
    transcribe: dict[str, Any]
    earlyMedia: bool
    channel: int


class TranscribeVerb(TypedDict, total=False):
    """Real-time call transcription."""

    verb: str  # "transcribe"
    id: str
    enable: bool
    transcriptionHook: str
    translationHook: str
    recognizer: Recognizer
    earlyMedia: bool
    channel: int


class ConferenceVerb(TypedDict, total=False):
    """Multi-party conference room."""

    verb: str  # "conference"
    id: str
    name: str
    beep: bool
    memberTag: str
    speakOnlyTo: str
    startConferenceOnEnter: bool
    endConferenceOnExit: bool
    endConferenceDuration: int
    maxParticipants: int
    joinMuted: bool
    actionHook: ActionHook
    waitHook: ActionHook
    statusEvents: list[str]
    statusHook: ActionHook
    enterHook: ActionHook
    record: dict[str, Any]
    listen: dict[str, Any]
    distributeDtmf: bool


class EnqueueVerb(TypedDict, total=False):
    """Place caller in a queue."""

    verb: str  # "enqueue"
    id: str
    name: str
    actionHook: ActionHook
    waitHook: ActionHook
    priority: int


class DequeueVerb(TypedDict, total=False):
    """Remove caller from a queue."""

    verb: str  # "dequeue"
    id: str
    name: str
    actionHook: ActionHook
    timeout: int
    beep: bool
    callSid: str


class HangupVerb(TypedDict, total=False):
    """Terminate the call."""

    verb: str  # "hangup"
    id: str
    headers: dict[str, str]


class PauseVerb(TypedDict, total=False):
    """Pause execution."""

    verb: str  # "pause"
    id: str
    length: int


class RedirectVerb(TypedDict, total=False):
    """Transfer control to different webhook."""

    verb: str  # "redirect"
    id: str
    actionHook: ActionHook
    statusHook: ActionHook


class ConfigVerb(TypedDict, total=False):
    """Set session-level defaults."""

    verb: str  # "config"
    id: str
    synthesizer: Synthesizer
    recognizer: Recognizer
    bargeIn: dict[str, Any]
    ttsStream: dict[str, Any]
    record: dict[str, Any]
    listen: dict[str, Any]
    stream: dict[str, Any]
    transcribe: dict[str, Any]
    amd: Amd
    fillerNoise: FillerNoise
    vad: Vad
    notifyEvents: bool
    notifySttLatency: bool
    reset: str | list[str]
    onHoldMusic: str
    actionHookDelayAction: ActionHookDelayAction
    sipRequestWithinDialogHook: ActionHook
    boostAudioSignal: int | str
    referHook: ActionHook
    earlyMedia: bool
    autoStreamTts: bool
    disableTtsCache: bool
    trackTtsPlayout: bool
    noiseIsolation: dict[str, Any]
    turnTaking: dict[str, Any]


class TagVerb(TypedDict, total=False):
    """Attach metadata to the call."""

    verb: str  # "tag"
    id: str
    data: dict[str, Any]


class DtmfVerb(TypedDict, total=False):
    """Send DTMF tones."""

    verb: str  # "dtmf"
    id: str
    dtmf: str
    duration: int


class MessageVerb(TypedDict, total=False):
    """Send SMS/MMS message."""

    verb: str  # "message"
    id: str
    to: str
    from_: str  # 'from' is reserved in Python; serialized as 'from'
    text: str
    media: str | list[str]
    carrier: str
    account_sid: str
    message_sid: str
    actionHook: ActionHook


class DubVerb(TypedDict, total=False):
    """Manage audio dubbing tracks."""

    verb: str  # "dub"
    id: str
    action: str  # "addTrack" | "removeTrack" | "silenceTrack" | "playOnTrack" | "sayOnTrack"
    track: str
    play: str
    say: str | dict[str, Any]
    loop: bool
    gain: int | str


class AlertVerb(TypedDict, total=False):
    """Send SIP 180 with Alert-Info."""

    verb: str  # "alert"
    id: str
    message: str


class AnswerVerb(TypedDict, total=False):
    """Explicitly answer the call."""

    verb: str  # "answer"
    id: str


class LeaveVerb(TypedDict, total=False):
    """Leave conference or queue."""

    verb: str  # "leave"
    id: str


class SipDeclineVerb(TypedDict, total=False):
    """Reject incoming call with SIP error."""

    verb: str  # "sip:decline"
    id: str
    status: int
    reason: str
    headers: dict[str, str]


class SipRequestVerb(TypedDict, total=False):
    """Send SIP request within dialog."""

    verb: str  # "sip:request"
    id: str
    method: str
    body: str
    headers: dict[str, str]
    actionHook: ActionHook


class SipReferVerb(TypedDict, total=False):
    """Send SIP REFER for call transfer."""

    verb: str  # "sip:refer"
    id: str
    referTo: str
    referredBy: str
    referredByDisplayName: str
    headers: dict[str, str]
    actionHook: ActionHook
    eventHook: ActionHook


# LLM/S2S verbs share the LlmBase structure

class LlmVerb(TypedDict, total=False):
    """Legacy LLM verb (prefer s2s or vendor-specific shortcuts)."""

    verb: str  # "llm"
    id: str
    vendor: str
    model: str
    auth: Auth
    connectOptions: dict[str, Any]
    llmOptions: dict[str, Any]
    mcpServers: list[McpServer]
    actionHook: ActionHook
    eventHook: ActionHook
    toolHook: ActionHook
    events: list[str]


class S2sVerb(TypedDict, total=False):
    """Generic S2S verb (use when vendor is dynamic)."""

    verb: str  # "s2s"
    id: str
    vendor: str
    model: str
    auth: Auth
    connectOptions: dict[str, Any]
    llmOptions: dict[str, Any]
    mcpServers: list[McpServer]
    actionHook: ActionHook
    eventHook: ActionHook
    toolHook: ActionHook
    events: list[str]


class OpenaiS2sVerb(TypedDict, total=False):
    """OpenAI speech-to-speech."""

    verb: str  # "openai_s2s"
    id: str
    vendor: str
    model: str
    auth: Auth
    connectOptions: dict[str, Any]
    llmOptions: dict[str, Any]
    mcpServers: list[McpServer]
    actionHook: ActionHook
    eventHook: ActionHook
    toolHook: ActionHook
    events: list[str]


class GoogleS2sVerb(TypedDict, total=False):
    """Google speech-to-speech."""

    verb: str  # "google_s2s"
    id: str
    vendor: str
    model: str
    auth: Auth
    connectOptions: dict[str, Any]
    llmOptions: dict[str, Any]
    mcpServers: list[McpServer]
    actionHook: ActionHook
    eventHook: ActionHook
    toolHook: ActionHook
    events: list[str]


class DeepgramS2sVerb(TypedDict, total=False):
    """Deepgram speech-to-speech."""

    verb: str  # "deepgram_s2s"
    id: str
    vendor: str
    model: str
    auth: Auth
    connectOptions: dict[str, Any]
    llmOptions: dict[str, Any]
    mcpServers: list[McpServer]
    actionHook: ActionHook
    eventHook: ActionHook
    toolHook: ActionHook
    events: list[str]


class ElevenlabsS2sVerb(TypedDict, total=False):
    """ElevenLabs speech-to-speech."""

    verb: str  # "elevenlabs_s2s"
    id: str
    vendor: str
    model: str
    auth: Auth
    connectOptions: dict[str, Any]
    llmOptions: dict[str, Any]
    mcpServers: list[McpServer]
    actionHook: ActionHook
    eventHook: ActionHook
    toolHook: ActionHook
    events: list[str]


class UltravoxS2sVerb(TypedDict, total=False):
    """Ultravox speech-to-speech."""

    verb: str  # "ultravox_s2s"
    id: str
    vendor: str
    model: str
    auth: Auth
    connectOptions: dict[str, Any]
    llmOptions: dict[str, Any]
    mcpServers: list[McpServer]
    actionHook: ActionHook
    eventHook: ActionHook
    toolHook: ActionHook
    events: list[str]


class DialogflowVerb(TypedDict, total=False):
    """Google Dialogflow agent."""

    verb: str  # "dialogflow"
    id: str
    project: str
    lang: str
    event: str
    environment: str
    welcomeEvent: str
    welcomeEventParams: dict[str, Any]
    noInputTimeout: int
    noInputEvent: str
    passDtmfAsTextInput: bool
    thresholdWordCount: int
    actionHook: ActionHook
    eventHook: ActionHook
    tts: Synthesizer


class PipelineVerb(TypedDict, total=False):
    """Integrated STT -> LLM -> TTS voice AI pipeline."""

    verb: str  # "pipeline"
    id: str
    stt: Recognizer
    tts: Synthesizer
    turnDetection: str | dict[str, Any]
    bargeIn: dict[str, Any]
    noResponseTimeout: int
    llm: dict[str, Any]
    actionHook: ActionHook
    eventHook: ActionHook
    toolHook: ActionHook
    greeting: bool
    earlyGeneration: bool
    noiseIsolation: str | dict[str, Any]
    mcpServers: list[McpServer]


# Union of all verb types
AnyVerb = Union[
    SayVerb,
    PlayVerb,
    GatherVerb,
    DialVerb,
    ListenVerb,
    StreamVerb,
    TranscribeVerb,
    ConferenceVerb,
    EnqueueVerb,
    DequeueVerb,
    HangupVerb,
    PauseVerb,
    RedirectVerb,
    ConfigVerb,
    TagVerb,
    DtmfVerb,
    MessageVerb,
    DubVerb,
    AlertVerb,
    AnswerVerb,
    LeaveVerb,
    SipDeclineVerb,
    SipRequestVerb,
    SipReferVerb,
    LlmVerb,
    S2sVerb,
    OpenaiS2sVerb,
    GoogleS2sVerb,
    DeepgramS2sVerb,
    ElevenlabsS2sVerb,
    UltravoxS2sVerb,
    DialogflowVerb,
    PipelineVerb,
]
