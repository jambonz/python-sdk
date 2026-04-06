"""Shared component type definitions matching jambonz JSON schemas.

All TypedDict keys use the exact same names as the jambonz JSON schemas
(camelCase where applicable) to ensure serialization compatibility.
"""

from __future__ import annotations

from typing import Any, TypedDict, Union


class Auth(TypedDict, total=False):
    """Authentication credentials."""

    username: str
    password: str
    apiKey: str
    agent_id: str
    api_key: str


class ActionHookObject(TypedDict, total=False):
    """ActionHook as an object with URL and options."""

    url: str
    method: str  # "GET" | "POST"
    basicAuth: Auth


# ActionHook can be a simple URL string or an object
ActionHook = Union[str, ActionHookObject]


class Synthesizer(TypedDict, total=False):
    """Text-to-speech configuration."""

    vendor: str
    label: str
    language: str
    voice: str | dict[str, Any]
    fallbackVendor: str
    fallbackLabel: str
    fallbackLanguage: str
    fallbackVoice: str | dict[str, Any]
    engine: str  # "standard" | "neural" | "generative" | "long-form"
    gender: str  # "MALE" | "FEMALE" | "NEUTRAL"
    options: dict[str, Any]


class Vad(TypedDict, total=False):
    """Voice Activity Detection configuration."""

    enable: bool
    voiceMs: int
    silenceMs: int
    strategy: str
    mode: int  # 0-3
    vendor: str  # "webrtc" | "silero"
    threshold: float  # 0-1
    speechPadMs: int


class Recognizer(TypedDict, total=False):
    """Speech-to-text recognition configuration."""

    vendor: str
    label: str
    language: str
    fallbackVendor: str
    fallbackLabel: str
    fallbackLanguage: str
    vad: Vad
    autogeneratePrompt: bool
    hints: list[str]
    hintsBoost: float
    altLanguages: list[str]
    profanityFilter: bool
    interim: bool
    singleUtterance: bool
    dualChannel: bool
    separateRecognitionPerChannel: bool
    punctuation: bool
    enhancedModel: bool
    words: bool
    diarization: bool
    diarizationMinSpeakers: int
    diarizationMaxSpeakers: int
    interactionType: str
    naicsCode: int
    identifyChannels: bool
    vocabularyName: str
    vocabularyFilterName: str
    filterMethod: str  # "remove" | "mask" | "tag"
    model: str
    outputFormat: str  # "simple" | "detailed"
    profanityOption: str  # "masked" | "removed" | "raw"
    requestSnr: bool
    initialSpeechTimeoutMs: int
    azureServiceEndpoint: str
    azureSttEndpointId: str
    asrDtmfTerminationDigit: str
    asrTimeout: int
    fastRecognitionTimeout: int
    minConfidence: float
    deepgramOptions: dict[str, Any]
    googleOptions: dict[str, Any]
    awsOptions: dict[str, Any]
    azureOptions: dict[str, Any]
    nuanceOptions: dict[str, Any]
    ibmOptions: dict[str, Any]
    nvidiaOptions: dict[str, Any]
    sonioxOptions: dict[str, Any]
    cobaltOptions: dict[str, Any]
    assemblyAiOptions: dict[str, Any]
    speechmaticsOptions: dict[str, Any]
    openaiOptions: dict[str, Any]
    houndifyOptions: dict[str, Any]
    gladiaOptions: dict[str, Any]
    elevenlabsOptions: dict[str, Any]
    verbioOptions: dict[str, Any]
    customOptions: dict[str, Any]


class FromHeader(TypedDict, total=False):
    """SIP From header override."""

    user: str
    host: str


class Target(TypedDict, total=False):
    """Call target for the dial verb."""

    type: str  # "phone" | "sip" | "user" | "teams"
    number: str
    sipUri: str
    name: str
    tenant: str
    trunk: str
    confirmHook: ActionHook
    method: str  # "GET" | "POST"
    headers: dict[str, str]
    from_: FromHeader  # Note: 'from' is reserved in Python
    auth: Auth
    vmail: bool
    overrideTo: str
    proxy: str


class AmdTimers(TypedDict, total=False):
    """AMD timer configuration."""

    noSpeechTimeoutMs: int
    decisionTimeoutMs: int
    toneTimeoutMs: int
    greetingCompletionTimeoutMs: int


class Amd(TypedDict, total=False):
    """Answering machine detection configuration."""

    actionHook: ActionHook
    thresholdWordCount: int
    digitCount: int
    timers: AmdTimers
    recognizer: Recognizer


class BidirectionalAudio(TypedDict, total=False):
    """Bidirectional audio streaming configuration."""

    enabled: bool
    streaming: bool
    sampleRate: int


class FillerNoise(TypedDict, total=False):
    """Filler noise configuration."""

    enable: bool
    url: str
    startDelaySecs: int


class ActionHookDelayAction(TypedDict, total=False):
    """Configuration for handling slow webhook responses."""

    enabled: bool
    noResponseTimeout: int
    noResponseGiveUpTimeout: int
    retries: int
    actions: list[dict[str, Any]]


class McpServer(TypedDict, total=False):
    """MCP server configuration."""

    url: str
    auth: dict[str, Any]
    roots: list[dict[str, Any]]


class LlmBase(TypedDict, total=False):
    """Shared properties for LLM/S2S verbs."""

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


class BargeIn(TypedDict, total=False):
    """Barge-in configuration."""

    enable: bool
    sticky: bool
    actionHook: ActionHook
    input: list[str]
    minBargeinWordCount: int


class TtsStream(TypedDict, total=False):
    """TTS streaming configuration."""

    enable: bool
    synthesizer: Synthesizer


class NoiseIsolation(TypedDict, total=False):
    """Noise isolation configuration."""

    enable: bool
    vendor: str
    level: int
    model: str


class TurnTaking(TypedDict, total=False):
    """Turn-taking detection configuration."""

    enable: bool
    vendor: str
    threshold: float
    model: str
