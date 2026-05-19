"""Spec-driven tests for VerbBuilder.

Validates the contract VerbBuilder offers to users:

- every verb in the registry is reachable as a method and produces a dict
  with the correct ``verb`` key
- method input styles (pydantic model, dict, kwargs) are interchangeable
- property names on the wire match the JSON Schema exactly (camelCase)
- Python reserved word mapping (``from_`` → ``from``) works
- chaining and reset behavior match the documented API
- strict validation catches typos / missing required fields at construction
  time rather than at the jambonz server

Since verbs have heterogeneous required-field sets, per-verb minimal valid
payloads are hand-maintained in ``MINIMAL_VALID_KWARGS`` below. They are
chosen to be the smallest input that round-trips through the model.
"""

import json

import pytest
from pydantic import ValidationError

from jambonz_sdk._models._registry import verb_model
from jambonz_sdk.verb_builder import VerbBuilder
from jambonz_sdk.verb_registry import VERB_DEFS

# ── Per-verb minimal payloads that satisfy required-field validation ─
# Values here are intentionally the smallest valid input for each verb;
# changes to a verb schema's ``required`` list will surface here.

MINIMAL_VALID_KWARGS: dict[str, dict] = {
    "say": {"text": "hi"},
    "play": {"url": "https://example.com/audio.mp3"},
    "gather": {},
    "openai_s2s": {"llmOptions": {}},
    "google_s2s": {"llmOptions": {}},
    "deepgram_s2s": {"llmOptions": {}},
    "elevenlabs_s2s": {"auth": {"agent_id": "agent-123"}},
    "ultravox_s2s": {"llmOptions": {}},
    "s2s": {"vendor": "openai", "llmOptions": {}},
    "llm": {"vendor": "openai", "llmOptions": {}},
    "dialogflow": {"project": "p", "lang": "en-US", "credentials": "{}"},
    "agent": {"llm": {"vendor": "openai", "llmOptions": {}}},
    "listen": {"url": "wss://example.com/a"},
    "stream": {"url": "wss://example.com/a"},
    "transcribe": {},
    "dial": {"target": [{"type": "phone", "number": "+15085551212"}]},
    "conference": {"name": "room"},
    "enqueue": {"name": "q"},
    "dequeue": {"name": "q"},
    "hangup": {},
    "redirect": {"actionHook": "/next"},
    "pause": {"length": 1},
    "sip_decline": {"status": 486},
    "sip_request": {"method": "INFO"},
    "sip_refer": {"referTo": "sip:alice@example.com"},
    "config": {},
    "tag": {"data": {"foo": "bar"}},
    "dtmf": {"dtmf": "1234"},
    "dub": {"action": "addTrack", "track": "1"},
    "message": {"to": "+1", "from_": "+2", "text": "hi"},
    "alert": {"message": "info=alert-internal"},
    "answer": {},
    "leave": {},
}


# ── Method existence and verb-name mapping ──────────────────────────

class TestAllVerbsRegistered:
    """Every VerbDef in the registry must produce a working method."""

    @pytest.mark.parametrize(
        "verb_def",
        VERB_DEFS,
        ids=[d.method_name for d in VERB_DEFS],
    )
    def test_method_exists(self, verb_def):
        assert hasattr(VerbBuilder, verb_def.method_name)

    @pytest.mark.parametrize(
        "verb_def",
        VERB_DEFS,
        ids=[d.method_name for d in VERB_DEFS],
    )
    def test_method_is_callable(self, verb_def):
        assert callable(getattr(VerbBuilder, verb_def.method_name))

    @pytest.mark.parametrize(
        "verb_def",
        VERB_DEFS,
        ids=[d.method_name for d in VERB_DEFS],
    )
    def test_minimal_payload_produces_correct_verb_name(self, verb_def):
        """A minimal valid payload round-trips and carries the verb name."""
        kwargs = MINIMAL_VALID_KWARGS.get(verb_def.method_name)
        assert kwargs is not None, (
            f"no minimal payload defined for {verb_def.method_name}; "
            "add an entry to MINIMAL_VALID_KWARGS"
        )
        builder = VerbBuilder()
        getattr(builder, verb_def.method_name)(**kwargs)
        verbs = builder.to_list()
        assert len(verbs) == 1
        assert verbs[0]["verb"] == verb_def.json_verb


# ── Every schema property round-trips through the builder ───────────

class TestVerbOutputMatchesSpec:
    """Properties declared on a verb's schema must pass through to the output."""

    @pytest.mark.parametrize(
        "verb_def",
        VERB_DEFS,
        ids=[d.method_name for d in VERB_DEFS],
    )
    def test_required_properties_pass_through(self, verb_def):
        """Every required field on the generated model appears in output."""
        model = verb_model(verb_def.json_verb)
        if model is None:
            pytest.skip(f"no generated model for {verb_def.json_verb}")

        required_aliases: set[str] = set()
        for name, info in model.model_fields.items():
            if name == "verb" or not info.is_required():
                continue
            required_aliases.add(info.alias or name)

        kwargs = dict(MINIMAL_VALID_KWARGS.get(verb_def.method_name, {}))
        builder = VerbBuilder()
        getattr(builder, verb_def.method_name)(**kwargs)
        output = builder.to_list()[0]

        for alias in required_aliases:
            if alias == "from":
                continue  # covered by TestPythonReservedWordMapping
            assert alias in output, (
                f"{verb_def.method_name}: required field '{alias}' "
                f"missing from output {list(output.keys())}"
            )


# ── Verb synonyms and vendor-shortcut behavior ──────────────────────

class TestVerbSynonyms:
    """Synonym verbs produce the correct json_verb and honor schema defaults."""

    def test_stream_produces_stream_verb(self):
        builder = VerbBuilder()
        builder.stream(url="wss://example.com/audio")
        assert builder.to_list()[0]["verb"] == "stream"

    def test_listen_produces_listen_verb(self):
        builder = VerbBuilder()
        builder.listen(url="wss://example.com/audio")
        assert builder.to_list()[0]["verb"] == "listen"

    def test_stream_and_listen_accept_same_properties(self):
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
        builder.elevenlabs_s2s(auth={"agent_id": "agent-123"})
        assert builder.to_list()[0]["vendor"] == "elevenlabs"

    def test_ultravox_s2s_injects_vendor(self):
        builder = VerbBuilder()
        builder.ultravox_s2s(llmOptions={})
        assert builder.to_list()[0]["vendor"] == "ultravox"

    def test_s2s_does_not_inject_vendor(self):
        """Generic s2s should not default a vendor — user provides it."""
        builder = VerbBuilder()
        builder.s2s(vendor="custom", llmOptions={})
        assert builder.to_list()[0]["vendor"] == "custom"

    def test_vendor_shortcut_rejects_mismatched_vendor(self):
        """Vendor-specific shortcut enforces its Literal vendor constraint."""
        builder = VerbBuilder()
        with pytest.raises(ValidationError):
            builder.openai_s2s(vendor="anthropic", llmOptions={})


# ── 'from' Python reserved word mapping ─────────────────────────────

class TestPythonReservedWordMapping:
    def test_message_from_mapping(self):
        builder = VerbBuilder()
        builder.message(to="+1234", from_="+5678", text="Hello")
        verbs = builder.to_list()
        assert "from" in verbs[0]
        assert "from_" not in verbs[0]
        assert verbs[0]["from"] == "+5678"


# ── Chaining and builder lifecycle ─────────────────────────────────

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


# ── JSON serialization of the full verb queue ─────────────────────

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


# ── SIP verb naming (colon in JSON, underscore in Python) ──────────

class TestSipVerbNaming:
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


# ── Realistic end-to-end flows ─────────────────────────────────────

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

    def test_voice_agent(self):
        builder = VerbBuilder()
        builder.agent(
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
        assert v["verb"] == "agent"
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


# ── New: the three input styles (model, dict, kwargs) are equivalent

class TestInputStylesEquivalent:
    """Passing a model, dict, or kwargs must produce the same wire output."""

    def test_gather_three_styles_match(self):
        Gather = verb_model("gather")
        assert Gather is not None

        payload = {
            "input": ["speech", "digits"],
            "actionHook": "/menu",
            "timeout": 15,
            "numDigits": 1,
            "say": {"text": "Press 1 for sales"},
            "recognizer": {"vendor": "deepgram", "language": "en-US"},
        }

        # 1) model
        b1 = VerbBuilder()
        b1.gather(Gather.model_validate(payload))

        # 2) dict
        b2 = VerbBuilder()
        b2.gather(dict(payload))

        # 3) kwargs
        b3 = VerbBuilder()
        b3.gather(**payload)

        assert b1.to_list() == b2.to_list() == b3.to_list()

    def test_say_three_styles_match(self):
        Say = verb_model("say")
        payload = {"text": "hello", "loop": 2}
        b1 = VerbBuilder()
        b1.say(Say.model_validate(payload))
        b2 = VerbBuilder()
        b2.say(dict(payload))
        b3 = VerbBuilder()
        b3.say(**payload)
        assert b1.to_list() == b2.to_list() == b3.to_list()


# ── New: validation catches typos and wrong types at construction ──

class TestStrictValidation:
    def test_typo_in_nested_field_rejected(self):
        """Unknown fields on inner types raise at construction."""
        builder = VerbBuilder()
        with pytest.raises(ValidationError):
            builder.gather(say={"txet": "typo — extra field"})

    def test_missing_required_field_rejected(self):
        """Play requires url — constructing without it fails fast."""
        builder = VerbBuilder()
        with pytest.raises(ValidationError):
            builder.play()

    def test_wrong_type_rejected(self):
        """Passing a wrong-typed value for a field fails pydantic validation."""
        builder = VerbBuilder()
        with pytest.raises(ValidationError):
            builder.say(text=12345, synthesizer="not-a-dict")

    def test_model_and_kwargs_both_raises(self):
        """Passing both a model/dict and kwargs is a user error."""
        Say = verb_model("say")
        builder = VerbBuilder()
        with pytest.raises(TypeError):
            builder.say(Say(text="hi"), text="also hi")


# ── Public re-export modules provide typed model access ────────────

class TestPublicImports:
    def test_verbs_package_exports_typed_models(self):
        from jambonz_sdk.verbs import Agent, Gather, OpenaiS2S, Say, SipDecline

        assert Gather.__name__ == "Gather"
        assert Say.__name__ == "Say"
        assert Agent.__name__ == "Agent"
        assert OpenaiS2S.__name__ == "OpenaiS2S"
        assert SipDecline.__name__ == "SipDecline"

    def test_components_package_exports_typed_models(self):
        from jambonz_sdk.components import (
            ActionHook,
            Recognizer,
            Synthesizer,
            Target,
        )

        assert Recognizer.__name__ == "Recognizer"
        assert Synthesizer.__name__ == "Synthesizer"
        assert Target.__name__ == "Target"
        assert ActionHook is not None

    def test_end_to_end_typed_construction(self):
        """The full typed API from the handover's 'goal' example works."""
        from jambonz_sdk._models._generated.components.recognizer_deepgramOptions import (
            DeepgramRecognizerOptions,
        )
        from jambonz_sdk.components import Recognizer
        from jambonz_sdk.verbs import Gather, Say

        builder = VerbBuilder()
        builder.gather(Gather(
            input=["speech", "digits"],
            action_hook="/menu",
            timeout=15,
            num_digits=1,
            say=Say(text="Press 1 for sales, 2 for support"),
            recognizer=Recognizer(
                vendor="deepgram",
                language="en-US",
                hints=["jambonz", "drachtio"],
                deepgram_options=DeepgramRecognizerOptions(
                    model="nova-3", smart_formatting=True
                ),
            ),
        ))
        [output] = builder.to_list()
        assert output["verb"] == "gather"
        assert output["actionHook"] == "/menu"
        assert output["numDigits"] == 1
        assert output["recognizer"]["deepgramOptions"]["smartFormatting"] is True
