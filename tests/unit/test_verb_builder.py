"""Spec-driven tests for VerbBuilder.

These tests validate that:
1. Every verb in the registry has a corresponding method on VerbBuilder
2. Every method produces JSON output matching the JSON Schema contract
3. Verb synonyms and injected properties work correctly
4. The builder's chaining and reset behavior is correct
5. Property names in output match JSON Schema exactly (camelCase preserved)
6. The 'from' → 'from_' Python mapping works for the message verb

Tests are driven by JSON Schema — if a new property is added to a verb schema,
these tests verify the SDK can pass it through correctly.
"""

import json

import pytest

from jambonz_sdk.verb_builder import _SPECS, VerbBuilder
from jambonz_sdk.verb_registry import VERB_DEFS

# ── Spec-driven: every registered verb must exist as a method ───────

class TestAllVerbsRegistered:
    """Every VerbDef in the registry must produce a working method."""

    @pytest.mark.parametrize(
        "verb_def",
        VERB_DEFS,
        ids=[d.method_name for d in VERB_DEFS],
    )
    def test_method_exists(self, verb_def):
        assert hasattr(VerbBuilder, verb_def.method_name), (
            f"VerbBuilder missing method '{verb_def.method_name}' "
            f"for spec '{verb_def.spec_name}'"
        )

    @pytest.mark.parametrize(
        "verb_def",
        VERB_DEFS,
        ids=[d.method_name for d in VERB_DEFS],
    )
    def test_method_is_callable(self, verb_def):
        method = getattr(VerbBuilder, verb_def.method_name)
        assert callable(method)

    @pytest.mark.parametrize(
        "verb_def",
        VERB_DEFS,
        ids=[d.method_name for d in VERB_DEFS],
    )
    def test_method_produces_correct_verb_name(self, verb_def):
        """Calling the method must produce a dict with the correct 'verb' key."""
        builder = VerbBuilder()
        method = getattr(builder, verb_def.method_name)
        method()  # Call with no args — all are optional at Python level
        verbs = builder.to_list()
        assert len(verbs) == 1
        assert verbs[0]["verb"] == verb_def.json_verb


# ── Spec-driven: output properties must match JSON Schema ─────────

class TestVerbOutputMatchesSpec:
    """For each verb, passing a property defined in the JSON Schema must
    appear in the output JSON with the exact same key name."""

    @pytest.mark.parametrize(
        "verb_def",
        VERB_DEFS,
        ids=[d.method_name for d in VERB_DEFS],
    )
    def test_all_spec_properties_pass_through(self, verb_def):
        """Every property in the spec can be passed and appears in output."""
        spec = _SPECS[verb_def.spec_name]
        properties = spec.get("properties", {})

        # Build kwargs with dummy values matching expected types
        kwargs = {}
        for prop_name, prop_type in properties.items():
            py_name = "from_" if prop_name == "from" else prop_name
            kwargs[py_name] = _dummy_value(prop_type)

        builder = VerbBuilder()
        method = getattr(builder, verb_def.method_name)
        method(**kwargs)
        verbs = builder.to_list()
        output = verbs[0]

        # Verify every spec property appears in output (with exact key name)
        for prop_name in properties:
            assert prop_name in output, (
                f"Verb '{verb_def.method_name}': spec property '{prop_name}' "
                f"missing from output. Got keys: {list(output.keys())}"
            )


class TestVerbSynonyms:
    """Synonym verbs must produce the correct json_verb and inject defaults."""

    def test_stream_produces_stream_verb(self):
        builder = VerbBuilder()
        builder.stream(url="wss://example.com/audio")
        assert builder.to_list()[0]["verb"] == "stream"

    def test_listen_produces_listen_verb(self):
        builder = VerbBuilder()
        builder.listen(url="wss://example.com/audio")
        assert builder.to_list()[0]["verb"] == "listen"

    def test_stream_and_listen_accept_same_properties(self):
        """Both synonyms accept the same spec properties."""
        b1 = VerbBuilder()
        b1.stream(url="wss://a.com", sampleRate=16000, mixType="stereo")
        b2 = VerbBuilder()
        b2.listen(url="wss://a.com", sampleRate=16000, mixType="stereo")
        v1, v2 = b1.to_list()[0], b2.to_list()[0]
        assert v1["url"] == v2["url"]
        assert v1["sampleRate"] == v2["sampleRate"]
        assert v1["verb"] != v2["verb"]

    def test_openai_s2s_injects_vendor(self):
        builder = VerbBuilder()
        builder.openai_s2s(llmOptions={})
        assert builder.to_list()[0]["vendor"] == "openai"

    def test_google_s2s_injects_vendor(self):
        builder = VerbBuilder()
        builder.google_s2s(llmOptions={})
        assert builder.to_list()[0]["vendor"] == "google"

    def test_deepgram_s2s_injects_vendor(self):
        builder = VerbBuilder()
        builder.deepgram_s2s(llmOptions={})
        assert builder.to_list()[0]["vendor"] == "deepgram"

    def test_elevenlabs_s2s_injects_vendor(self):
        builder = VerbBuilder()
        builder.elevenlabs_s2s(llmOptions={})
        assert builder.to_list()[0]["vendor"] == "elevenlabs"

    def test_ultravox_s2s_injects_vendor(self):
        builder = VerbBuilder()
        builder.ultravox_s2s(llmOptions={})
        assert builder.to_list()[0]["vendor"] == "ultravox"

    def test_s2s_does_not_inject_vendor(self):
        """Generic s2s should NOT inject a vendor — user provides it."""
        builder = VerbBuilder()
        builder.s2s(vendor="custom", llmOptions={})
        assert builder.to_list()[0]["vendor"] == "custom"

    def test_user_can_override_injected_vendor(self):
        """Explicit vendor kwarg should override the injected default."""
        builder = VerbBuilder()
        builder.openai_s2s(vendor="custom-openai", llmOptions={})
        assert builder.to_list()[0]["vendor"] == "custom-openai"


class TestPythonReservedWordMapping:
    """'from' is reserved in Python; we accept 'from_' and serialize as 'from'."""

    def test_message_from_mapping(self):
        builder = VerbBuilder()
        builder.message(to="+1234", from_="+5678", text="Hello")
        verbs = builder.to_list()
        assert "from" in verbs[0]
        assert "from_" not in verbs[0]
        assert verbs[0]["from"] == "+5678"


class TestBuilderChaining:
    def test_chaining_returns_self(self):
        builder = VerbBuilder()
        result = builder.say(text="a").pause(length=1).hangup()
        assert result is builder

    def test_to_list_returns_all_verbs_in_order(self):
        builder = VerbBuilder()
        builder.say(text="Hello").pause(length=1).hangup()
        verbs = builder.to_list()
        assert [v["verb"] for v in verbs] == ["say", "pause", "hangup"]

    def test_to_list_resets_builder(self):
        builder = VerbBuilder()
        builder.say(text="first")
        builder.to_list()
        builder.say(text="second")
        verbs = builder.to_list()
        assert len(verbs) == 1
        assert verbs[0]["text"] == "second"

    def test_empty_builder_returns_empty_list(self):
        assert VerbBuilder().to_list() == []

    def test_none_values_are_stripped(self):
        builder = VerbBuilder()
        builder.say(text="Hello", loop=None, synthesizer=None)
        verbs = builder.to_list()
        assert "loop" not in verbs[0]
        assert "synthesizer" not in verbs[0]


class TestJsonSerialization:
    def test_output_is_json_serializable(self):
        builder = VerbBuilder()
        builder.config(
            synthesizer={"vendor": "google", "voice": "en-US-Wavenet-D"},
            recognizer={"vendor": "deepgram", "language": "en-US"},
        ).gather(
            input=["speech", "digits"],
            actionHook="/result",
            say={"text": "Say something."},
        ).hangup()
        serialized = json.dumps(builder.to_list())
        assert len(json.loads(serialized)) == 3

    def test_nested_objects_preserved(self):
        builder = VerbBuilder()
        builder.gather(
            recognizer={"vendor": "deepgram", "deepgramOptions": {"model": "nova-3"}},
            say={"text": "Speak.", "synthesizer": {"vendor": "elevenlabs"}},
        )
        verbs = builder.to_list()
        assert verbs[0]["recognizer"]["deepgramOptions"]["model"] == "nova-3"
        assert verbs[0]["say"]["synthesizer"]["vendor"] == "elevenlabs"


class TestSipVerbNaming:
    """SIP verbs use colon in JSON (sip:decline) but underscore in Python."""

    def test_sip_decline_json_verb(self):
        builder = VerbBuilder()
        builder.sip_decline(status=486, reason="Busy Here")
        assert builder.to_list()[0]["verb"] == "sip:decline"

    def test_sip_request_json_verb(self):
        builder = VerbBuilder()
        builder.sip_request(method="INFO")
        assert builder.to_list()[0]["verb"] == "sip:request"

    def test_sip_refer_json_verb(self):
        builder = VerbBuilder()
        builder.sip_refer(referTo="sip:alice@example.com")
        assert builder.to_list()[0]["verb"] == "sip:refer"


# ── Realistic jambonz application flows ─────────────────────────────

class TestRealisticFlows:
    def test_ivr_menu_flow(self):
        builder = VerbBuilder()
        builder.say(text="Welcome.").gather(
            input=["speech", "digits"],
            actionHook="/menu",
            numDigits=1,
            timeout=10,
            say={"text": "Press 1 for sales."},
        ).say(text="No input. Goodbye.").hangup()
        verbs = builder.to_list()
        assert len(verbs) == 4
        assert [v["verb"] for v in verbs] == ["say", "gather", "say", "hangup"]
        assert verbs[1]["actionHook"] == "/menu"
        assert verbs[1]["numDigits"] == 1

    def test_dial_with_answer_on_bridge(self):
        builder = VerbBuilder()
        builder.dial(
            target=[{"type": "phone", "number": "+15085551212"}],
            answerOnBridge=True,
            timeout=30,
            actionHook="/dial-result",
        )
        verbs = builder.to_list()
        assert verbs[0]["target"][0]["type"] == "phone"
        assert verbs[0]["answerOnBridge"] is True

    def test_voice_agent_pipeline(self):
        builder = VerbBuilder()
        builder.pipeline(
            stt={"vendor": "deepgram", "language": "en-US"},
            tts={"vendor": "cartesia", "voice": "sonic"},
            llm={"vendor": "openai", "model": "gpt-4o", "llmOptions": {
                "messages": [{"role": "system", "content": "You are helpful."}]
            }},
            turnDetection="krisp",
            bargeIn={"enable": True, "minSpeechDuration": 0.3},
            actionHook="/done",
            eventHook="/events",
            toolHook="/tools",
        )
        v = builder.to_list()[0]
        assert v["verb"] == "pipeline"
        assert v["stt"]["vendor"] == "deepgram"
        assert v["llm"]["vendor"] == "openai"
        assert v["turnDetection"] == "krisp"

    def test_listen_with_bidirectional_audio(self):
        builder = VerbBuilder()
        builder.listen(
            url="/audio",
            sampleRate=16000,
            bidirectionalAudio={"enabled": True, "streaming": True, "sampleRate": 24000},
            metadata={"purpose": "recording"},
            actionHook="/done",
        )
        v = builder.to_list()[0]
        assert v["bidirectionalAudio"]["streaming"] is True
        assert v["metadata"]["purpose"] == "recording"


# ── Helpers ─────────────────────────────────────────────────────────

def _dummy_value(spec_type):
    """Generate a dummy value matching a JSON Schema type descriptor."""
    if isinstance(spec_type, str):
        if spec_type.startswith("#"):
            return {}
        if "|" in spec_type:
            first = spec_type.split("|")[0].strip()
            return _dummy_value(first)
        return {"string": "test", "number": 1, "boolean": True, "object": {}, "array": []}.get(spec_type, "test")
    if isinstance(spec_type, list):
        return [{}]
    if isinstance(spec_type, dict):
        enum = spec_type.get("enum")
        if enum:
            return enum[0]
        return _dummy_value(spec_type.get("type", "string"))
    return "test"
