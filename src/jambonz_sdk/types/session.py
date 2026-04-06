"""Call session and WebSocket message types."""

from __future__ import annotations

from enum import Enum
from typing import Any, TypedDict


class CallDirection(str, Enum):
    """Call direction."""

    INBOUND = "inbound"
    OUTBOUND = "outbound"


class CallSession(TypedDict, total=False):
    """Call session data received on session:new."""

    call_sid: str
    account_sid: str
    application_sid: str
    direction: str  # "inbound" | "outbound"
    from_: str  # Serialized as 'from'
    to: str
    call_id: str
    sip_status: int
    sip: dict[str, Any]
    env_vars: dict[str, str]
    defaults: dict[str, Any]
    customerData: dict[str, Any]


class WsMessageType(str, Enum):
    """WebSocket message types from jambonz."""

    SESSION_NEW = "session:new"
    SESSION_REDIRECT = "session:redirect"
    SESSION_RECONNECT = "session:reconnect"
    SESSION_ADULTING = "session:adulting"
    VERB_HOOK = "verb:hook"
    VERB_STATUS = "verb:status"
    CALL_STATUS = "call:status"
    LLM_TOOL_CALL = "llm:tool-call"
    LLM_EVENT = "llm:event"
    TTS_TOKENS_RESULT = "tts:tokens-result"
    TTS_STREAMING_EVENT = "tts:streaming-event"


class WsMessage(TypedDict, total=False):
    """WebSocket message structure."""

    type: str
    msgid: str
    hook: str
    data: dict[str, Any]
