"""REST API request/response types."""

from __future__ import annotations

from typing import Any, TypedDict


class CreateCallRequest(TypedDict, total=False):
    """Request body for creating an outbound call."""

    from_: str  # Serialized as 'from'
    to: dict[str, Any]  # Target object
    call_hook: str
    call_status_hook: str
    timeout: int
    tag: dict[str, Any]
    headers: dict[str, str]
    caller_name: str


class ListCallsFilter(TypedDict, total=False):
    """Filter parameters for listing calls."""

    direction: str  # "inbound" | "outbound"
    from_: str
    to: str
    callStatus: str


class CallStatus(TypedDict, total=False):
    """Call status information."""

    call_sid: str
    account_sid: str
    application_sid: str
    direction: str
    from_: str
    to: str
    call_id: str
    sip_status: int
    call_status: str
    duration: int


class CallInfo(TypedDict, total=False):
    """Full call information returned by the API."""

    call_sid: str
    account_sid: str
    application_sid: str
    direction: str
    from_: str
    to: str
    call_id: str
    sip_status: int
    call_status: str
    caller_name: str
    duration: int
    trace_id: str
