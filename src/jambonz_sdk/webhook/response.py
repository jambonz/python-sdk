"""WebhookResponse class for HTTP-based jambonz applications.

Usage with any framework that accepts JSON-serializable responses::

    from jambonz_sdk.webhook import WebhookResponse

    # In your request handler:
    jambonz = WebhookResponse()
    jambonz.say(text="Hello!").gather(
        input=["speech"],
        actionHook="/handle-input",
        timeout=10,
        say={"text": "Please say something."},
    )
    # Return jambonz.to_json() as the HTTP response body
"""

from __future__ import annotations

import json
from typing import Any

from jambonz_sdk.verb_builder import VerbBuilder


class WebhookResponse(VerbBuilder):
    """Builds a jambonz verb array for HTTP webhook responses.

    Extends VerbBuilder with JSON serialization. The response can be
    converted to a JSON-serializable list or a JSON string.
    """

    def to_json(self) -> list[dict[str, Any]]:
        """Return the verb array as a JSON-serializable list and reset."""
        return self.to_list()  # type: ignore[return-value]

    def to_json_string(self) -> str:
        """Return the verb array as a JSON string and reset."""
        return json.dumps(self.to_list())

    def __json__(self) -> list[dict[str, Any]]:
        """Support for frameworks that call __json__ for serialization."""
        return self.to_json()
