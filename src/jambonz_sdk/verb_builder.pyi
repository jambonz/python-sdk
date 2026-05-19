"""Auto-generated type stubs for VerbBuilder.

DO NOT EDIT — regenerate with: python scripts/generate_stubs.py

Each verb method accepts three interchangeable input forms:
  1. a positional generated model instance
  2. a positional dict payload
  3. keyword arguments matching the verb's JSON Schema
"""

from typing import Any, Self

from jambonz_sdk.types.verbs import AnyVerb

class VerbBuilder:
    _verbs: list[AnyVerb]

    def __init__(self) -> None: ...
    def to_list(self) -> list[AnyVerb]: ...

    def say(
        self, arg: Any = ..., /,
        id: str = ...,
        text: Any = ...,
        instructions: str = ...,
        stream: bool = ...,
        loop: Any = ...,
        synthesizer: Any = ...,
        earlyMedia: bool = ...,
        disableTtsCache: bool = ...,
        closeStreamOnEmpty: bool = ...,
        **kwargs: Any,
    ) -> Self:
        """Speak text using TTS.

        Args:
            arg: a typed model instance or a dict payload (alternative to kwargs).
            id: str
            text: Any
            instructions: str
            stream: bool
            loop: Any
            synthesizer: Any
            earlyMedia: bool
            disableTtsCache: bool
            closeStreamOnEmpty: bool

        Returns:
            self for chaining.
        """
        ...

    def play(
        self, arg: Any = ..., /,
        id: str = ...,
        url: Any = ...,
        loop: Any = ...,
        earlyMedia: bool = ...,
        seekOffset: Any = ...,
        timeoutSecs: Any = ...,
        actionHook: Any = ...,
        **kwargs: Any,
    ) -> Self:
        """Play an audio file from a URL.

        Required: url

        Args:
            arg: a typed model instance or a dict payload (alternative to kwargs).
            id: str
            url: Any (required)
            loop: Any
            earlyMedia: bool
            seekOffset: Any
            timeoutSecs: Any
            actionHook: Any

        Returns:
            self for chaining.
        """
        ...

    def gather(
        self, arg: Any = ..., /,
        id: str = ...,
        actionHook: Any = ...,
        input: list[Any] = ...,
        finishOnKey: str = ...,
        numDigits: int | float = ...,
        minDigits: int | float = ...,
        maxDigits: int | float = ...,
        interDigitTimeout: int | float = ...,
        speechTimeout: int | float = ...,
        timeout: int | float = ...,
        partialResultHook: Any = ...,
        listenDuringPrompt: bool = ...,
        dtmfBargein: bool = ...,
        bargein: bool = ...,
        minBargeinWordCount: int | float = ...,
        recognizer: Any = ...,
        say: dict[str, Any] = ...,
        play: dict[str, Any] = ...,
        fillerNoise: Any = ...,
        actionHookDelayAction: Any = ...,
        **kwargs: Any,
    ) -> Self:
        """Collect speech (STT) and/or DTMF input.

        Args:
            arg: a typed model instance or a dict payload (alternative to kwargs).
            id: str
            actionHook: Any
            input: list[Any]
            finishOnKey: str
            numDigits: int | float
            minDigits: int | float
            maxDigits: int | float
            interDigitTimeout: int | float
            speechTimeout: int | float
            timeout: int | float
            partialResultHook: Any
            listenDuringPrompt: bool
            dtmfBargein: bool
            bargein: bool
            minBargeinWordCount: int | float
            recognizer: Any
            say: dict[str, Any]
            play: dict[str, Any]
            fillerNoise: Any
            actionHookDelayAction: Any

        Returns:
            self for chaining.
        """
        ...

    def openai_s2s(
        self, arg: Any = ..., /,
        **kwargs: Any,
    ) -> Self:
        """Connect caller to OpenAI for real-time voice conversation.

        Required: llmOptions, vendor

        Args:
            arg: a typed model instance or a dict payload (alternative to kwargs).

        Returns:
            self for chaining.
        """
        ...

    def google_s2s(
        self, arg: Any = ..., /,
        **kwargs: Any,
    ) -> Self:
        """Connect caller to Google for real-time voice conversation.

        Required: llmOptions, vendor

        Args:
            arg: a typed model instance or a dict payload (alternative to kwargs).

        Returns:
            self for chaining.
        """
        ...

    def deepgram_s2s(
        self, arg: Any = ..., /,
        **kwargs: Any,
    ) -> Self:
        """Connect caller to Deepgram for real-time voice conversation.

        Required: llmOptions, vendor

        Args:
            arg: a typed model instance or a dict payload (alternative to kwargs).

        Returns:
            self for chaining.
        """
        ...

    def elevenlabs_s2s(
        self, arg: Any = ..., /,
        **kwargs: Any,
    ) -> Self:
        """Connect caller to ElevenLabs Conversational AI agent.

        Required: llmOptions, vendor

        Args:
            arg: a typed model instance or a dict payload (alternative to kwargs).

        Returns:
            self for chaining.
        """
        ...

    def ultravox_s2s(
        self, arg: Any = ..., /,
        **kwargs: Any,
    ) -> Self:
        """Connect caller to Ultravox for real-time voice conversation.

        Required: llmOptions, vendor

        Args:
            arg: a typed model instance or a dict payload (alternative to kwargs).

        Returns:
            self for chaining.
        """
        ...

    def s2s(
        self, arg: Any = ..., /,
        **kwargs: Any,
    ) -> Self:
        """Generic S2S verb (use when vendor is determined at runtime).

        Required: llmOptions, vendor

        Args:
            arg: a typed model instance or a dict payload (alternative to kwargs).

        Returns:
            self for chaining.
        """
        ...

    def llm(
        self, arg: Any = ..., /,
        **kwargs: Any,
    ) -> Self:
        """Legacy LLM verb (prefer s2s or vendor-specific shortcuts).

        Required: llmOptions, vendor

        Args:
            arg: a typed model instance or a dict payload (alternative to kwargs).

        Returns:
            self for chaining.
        """
        ...

    def dialogflow(
        self, arg: Any = ..., /,
        id: str = ...,
        credentials: Any = ...,
        project: str = ...,
        agent: str = ...,
        environment: str = ...,
        region: str = ...,
        model: str = ...,
        lang: str = ...,
        actionHook: Any = ...,
        eventHook: Any = ...,
        events: list[Any] = ...,
        welcomeEvent: str = ...,
        welcomeEventParams: dict[str, Any] = ...,
        noInputTimeout: int | float = ...,
        noInputEvent: str = ...,
        passDtmfAsTextInput: bool = ...,
        thinkingMusic: str = ...,
        tts: Any = ...,
        bargein: bool = ...,
        queryInput: dict[str, Any] = ...,
        **kwargs: Any,
    ) -> Self:
        """Connect caller to Google Dialogflow agent.

        Required: credentials, lang, project

        Args:
            arg: a typed model instance or a dict payload (alternative to kwargs).
            id: str
            credentials: Any (required)
            project: str (required)
            agent: str
            environment: str
            region: str
            model: str
            lang: str (required)
            actionHook: Any
            eventHook: Any
            events: list[Any]
            welcomeEvent: str
            welcomeEventParams: dict[str, Any]
            noInputTimeout: int | float
            noInputEvent: str
            passDtmfAsTextInput: bool
            thinkingMusic: str
            tts: Any
            bargein: bool
            queryInput: dict[str, Any]

        Returns:
            self for chaining.
        """
        ...

    def agent(
        self, arg: Any = ..., /,
        id: str = ...,
        stt: Any = ...,
        tts: Any = ...,
        turnDetection: Any = ...,
        bargeIn: dict[str, Any] = ...,
        noResponseTimeout: int | float = ...,
        llm: dict[str, Any] = ...,
        actionHook: Any = ...,
        eventHook: Any = ...,
        toolHook: Any = ...,
        greeting: bool = ...,
        earlyGeneration: bool = ...,
        noiseIsolation: Any = ...,
        mcpServers: list[Any] = ...,
        **kwargs: Any,
    ) -> Self:
        """Integrated STT → LLM → TTS voice AI agent.

        Required: llm

        Args:
            arg: a typed model instance or a dict payload (alternative to kwargs).
            id: str
            stt: Any
            tts: Any
            turnDetection: Any
            bargeIn: dict[str, Any]
            noResponseTimeout: int | float
            llm: dict[str, Any] (required)
            actionHook: Any
            eventHook: Any
            toolHook: Any
            greeting: bool
            earlyGeneration: bool
            noiseIsolation: Any
            mcpServers: list[Any]

        Returns:
            self for chaining.
        """
        ...

    def listen(
        self, arg: Any = ..., /,
        id: str = ...,
        url: str = ...,
        actionHook: Any = ...,
        wsAuth: Any = ...,
        mixType: str = ...,
        metadata: dict[str, Any] = ...,
        sampleRate: int | float = ...,
        finishOnKey: str = ...,
        maxLength: int | float = ...,
        passDtmf: bool = ...,
        playBeep: bool = ...,
        disableBidirectionalAudio: bool = ...,
        bidirectionalAudio: Any = ...,
        timeout: int | float = ...,
        transcribe: Any = ...,
        earlyMedia: bool = ...,
        channel: int | float = ...,
        **kwargs: Any,
    ) -> Self:
        """Stream real-time audio to a websocket endpoint.

        Required: url

        Args:
            arg: a typed model instance or a dict payload (alternative to kwargs).
            id: str
            url: str (required)
            actionHook: Any
            wsAuth: Any
            mixType: str
            metadata: dict[str, Any]
            sampleRate: int | float
            finishOnKey: str
            maxLength: int | float
            passDtmf: bool
            playBeep: bool
            disableBidirectionalAudio: bool
            bidirectionalAudio: Any
            timeout: int | float
            transcribe: Any
            earlyMedia: bool
            channel: int | float

        Returns:
            self for chaining.
        """
        ...

    def stream(
        self, arg: Any = ..., /,
        id: str = ...,
        url: str = ...,
        actionHook: Any = ...,
        wsAuth: Any = ...,
        mixType: str = ...,
        metadata: dict[str, Any] = ...,
        sampleRate: int | float = ...,
        finishOnKey: str = ...,
        maxLength: int | float = ...,
        passDtmf: bool = ...,
        playBeep: bool = ...,
        disableBidirectionalAudio: bool = ...,
        bidirectionalAudio: Any = ...,
        timeout: int | float = ...,
        transcribe: Any = ...,
        earlyMedia: bool = ...,
        channel: int | float = ...,
        **kwargs: Any,
    ) -> Self:
        """Stream real-time audio (preferred alias for listen).

        Required: url

        Args:
            arg: a typed model instance or a dict payload (alternative to kwargs).
            id: str
            url: str (required)
            actionHook: Any
            wsAuth: Any
            mixType: str
            metadata: dict[str, Any]
            sampleRate: int | float
            finishOnKey: str
            maxLength: int | float
            passDtmf: bool
            playBeep: bool
            disableBidirectionalAudio: bool
            bidirectionalAudio: Any
            timeout: int | float
            transcribe: Any
            earlyMedia: bool
            channel: int | float

        Returns:
            self for chaining.
        """
        ...

    def transcribe(
        self, arg: Any = ..., /,
        id: str = ...,
        enable: bool = ...,
        transcriptionHook: str = ...,
        translationHook: str = ...,
        recognizer: Any = ...,
        earlyMedia: bool = ...,
        channel: int | float = ...,
        **kwargs: Any,
    ) -> Self:
        """Enable real-time call transcription.

        Args:
            arg: a typed model instance or a dict payload (alternative to kwargs).
            id: str
            enable: bool
            transcriptionHook: str
            translationHook: str
            recognizer: Any
            earlyMedia: bool
            channel: int | float

        Returns:
            self for chaining.
        """
        ...

    def dial(
        self, arg: Any = ..., /,
        id: str = ...,
        target: list[Any] = ...,
        actionHook: Any = ...,
        onHoldHook: Any = ...,
        answerOnBridge: bool = ...,
        callerId: str = ...,
        callerName: str = ...,
        confirmHook: Any = ...,
        referHook: Any = ...,
        dialMusic: str = ...,
        dtmfCapture: Any = ...,
        dtmfHook: Any = ...,
        headers: dict[str, Any] = ...,
        anchorMedia: bool = ...,
        exitMediaPath: bool = ...,
        boostAudioSignal: Any = ...,
        listen: dict[str, Any] = ...,
        stream: dict[str, Any] = ...,
        transcribe: dict[str, Any] = ...,
        timeLimit: int | float = ...,
        timeout: int | float = ...,
        proxy: str = ...,
        amd: Any = ...,
        dub: list[Any] = ...,
        tag: dict[str, Any] = ...,
        forwardPAI: bool = ...,
        **kwargs: Any,
    ) -> Self:
        """Place outbound call and bridge to current caller.

        Required: target

        Args:
            arg: a typed model instance or a dict payload (alternative to kwargs).
            id: str
            target: list[Any] (required)
            actionHook: Any
            onHoldHook: Any
            answerOnBridge: bool
            callerId: str
            callerName: str
            confirmHook: Any
            referHook: Any
            dialMusic: str
            dtmfCapture: Any
            dtmfHook: Any
            headers: dict[str, Any]
            anchorMedia: bool
            exitMediaPath: bool
            boostAudioSignal: Any
            listen: dict[str, Any]
            stream: dict[str, Any]
            transcribe: dict[str, Any]
            timeLimit: int | float
            timeout: int | float
            proxy: str
            amd: Any
            dub: list[Any]
            tag: dict[str, Any]
            forwardPAI: bool

        Returns:
            self for chaining.
        """
        ...

    def conference(
        self, arg: Any = ..., /,
        id: str = ...,
        name: str = ...,
        beep: bool = ...,
        memberTag: str = ...,
        speakOnlyTo: str = ...,
        startConferenceOnEnter: bool = ...,
        endConferenceOnExit: bool = ...,
        endConferenceDuration: int | float = ...,
        maxParticipants: int | float = ...,
        joinMuted: bool = ...,
        actionHook: Any = ...,
        waitHook: Any = ...,
        statusEvents: list[Any] = ...,
        statusHook: Any = ...,
        enterHook: Any = ...,
        record: dict[str, Any] = ...,
        listen: dict[str, Any] = ...,
        distributeDtmf: bool = ...,
        **kwargs: Any,
    ) -> Self:
        """Place caller into a multi-party conference room.

        Required: name

        Args:
            arg: a typed model instance or a dict payload (alternative to kwargs).
            id: str
            name: str (required)
            beep: bool
            memberTag: str
            speakOnlyTo: str
            startConferenceOnEnter: bool
            endConferenceOnExit: bool
            endConferenceDuration: int | float
            maxParticipants: int | float
            joinMuted: bool
            actionHook: Any
            waitHook: Any
            statusEvents: list[Any]
            statusHook: Any
            enterHook: Any
            record: dict[str, Any]
            listen: dict[str, Any]
            distributeDtmf: bool

        Returns:
            self for chaining.
        """
        ...

    def enqueue(
        self, arg: Any = ..., /,
        id: str = ...,
        name: str = ...,
        actionHook: Any = ...,
        waitHook: Any = ...,
        priority: int | float = ...,
        **kwargs: Any,
    ) -> Self:
        """Place caller into a named call queue.

        Required: name

        Args:
            arg: a typed model instance or a dict payload (alternative to kwargs).
            id: str
            name: str (required)
            actionHook: Any
            waitHook: Any
            priority: int | float

        Returns:
            self for chaining.
        """
        ...

    def dequeue(
        self, arg: Any = ..., /,
        id: str = ...,
        name: str = ...,
        actionHook: Any = ...,
        timeout: int | float = ...,
        beep: bool = ...,
        callSid: str = ...,
        **kwargs: Any,
    ) -> Self:
        """Remove caller from a queue and bridge.

        Required: name

        Args:
            arg: a typed model instance or a dict payload (alternative to kwargs).
            id: str
            name: str (required)
            actionHook: Any
            timeout: int | float
            beep: bool
            callSid: str

        Returns:
            self for chaining.
        """
        ...

    def hangup(
        self, arg: Any = ..., /,
        id: str = ...,
        headers: dict[str, Any] = ...,
        **kwargs: Any,
    ) -> Self:
        """Terminate the call.

        Args:
            arg: a typed model instance or a dict payload (alternative to kwargs).
            id: str
            headers: dict[str, Any]

        Returns:
            self for chaining.
        """
        ...

    def redirect(
        self, arg: Any = ..., /,
        id: str = ...,
        actionHook: Any = ...,
        statusHook: Any = ...,
        **kwargs: Any,
    ) -> Self:
        """Transfer control to a different webhook URL.

        Required: actionHook

        Args:
            arg: a typed model instance or a dict payload (alternative to kwargs).
            id: str
            actionHook: Any (required)
            statusHook: Any

        Returns:
            self for chaining.
        """
        ...

    def pause(
        self, arg: Any = ..., /,
        id: str = ...,
        length: int | float = ...,
        **kwargs: Any,
    ) -> Self:
        """Pause execution for a specified duration.

        Required: length

        Args:
            arg: a typed model instance or a dict payload (alternative to kwargs).
            id: str
            length: int | float (required)

        Returns:
            self for chaining.
        """
        ...

    def sip_decline(
        self, arg: Any = ..., /,
        id: str = ...,
        status: int | float = ...,
        reason: str = ...,
        headers: dict[str, Any] = ...,
        **kwargs: Any,
    ) -> Self:
        """Reject incoming call with a SIP error response.

        Required: status

        Args:
            arg: a typed model instance or a dict payload (alternative to kwargs).
            id: str
            status: int | float (required)
            reason: str
            headers: dict[str, Any]

        Returns:
            self for chaining.
        """
        ...

    def sip_request(
        self, arg: Any = ..., /,
        id: str = ...,
        method: str = ...,
        body: str = ...,
        headers: dict[str, Any] = ...,
        actionHook: Any = ...,
        **kwargs: Any,
    ) -> Self:
        """Send a SIP request within the current dialog.

        Required: method

        Args:
            arg: a typed model instance or a dict payload (alternative to kwargs).
            id: str
            method: str (required)
            body: str
            headers: dict[str, Any]
            actionHook: Any

        Returns:
            self for chaining.
        """
        ...

    def sip_refer(
        self, arg: Any = ..., /,
        id: str = ...,
        referTo: str = ...,
        referredBy: str = ...,
        referredByDisplayName: str = ...,
        headers: dict[str, Any] = ...,
        actionHook: Any = ...,
        eventHook: Any = ...,
        **kwargs: Any,
    ) -> Self:
        """Send a SIP REFER for call transfer.

        Required: referTo

        Args:
            arg: a typed model instance or a dict payload (alternative to kwargs).
            id: str
            referTo: str (required)
            referredBy: str
            referredByDisplayName: str
            headers: dict[str, Any]
            actionHook: Any
            eventHook: Any

        Returns:
            self for chaining.
        """
        ...

    def config(
        self, arg: Any = ..., /,
        id: str = ...,
        synthesizer: Any = ...,
        recognizer: Any = ...,
        bargeIn: dict[str, Any] = ...,
        ttsStream: dict[str, Any] = ...,
        record: dict[str, Any] = ...,
        listen: dict[str, Any] = ...,
        stream: dict[str, Any] = ...,
        transcribe: dict[str, Any] = ...,
        amd: Any = ...,
        fillerNoise: Any = ...,
        vad: Any = ...,
        notifyEvents: bool = ...,
        notifySttLatency: bool = ...,
        reset: Any = ...,
        onHoldMusic: str = ...,
        actionHookDelayAction: Any = ...,
        sipRequestWithinDialogHook: Any = ...,
        boostAudioSignal: Any = ...,
        referHook: Any = ...,
        earlyMedia: bool = ...,
        autoStreamTts: bool = ...,
        disableTtsCache: bool = ...,
        trackTtsPlayout: bool = ...,
        noiseIsolation: dict[str, Any] = ...,
        turnTaking: dict[str, Any] = ...,
        **kwargs: Any,
    ) -> Self:
        """Set session-level defaults.

        Args:
            arg: a typed model instance or a dict payload (alternative to kwargs).
            id: str
            synthesizer: Any
            recognizer: Any
            bargeIn: dict[str, Any]
            ttsStream: dict[str, Any]
            record: dict[str, Any]
            listen: dict[str, Any]
            stream: dict[str, Any]
            transcribe: dict[str, Any]
            amd: Any
            fillerNoise: Any
            vad: Any
            notifyEvents: bool
            notifySttLatency: bool
            reset: Any
            onHoldMusic: str
            actionHookDelayAction: Any
            sipRequestWithinDialogHook: Any
            boostAudioSignal: Any
            referHook: Any
            earlyMedia: bool
            autoStreamTts: bool
            disableTtsCache: bool
            trackTtsPlayout: bool
            noiseIsolation: dict[str, Any]
            turnTaking: dict[str, Any]

        Returns:
            self for chaining.
        """
        ...

    def tag(
        self, arg: Any = ..., /,
        id: str = ...,
        data: dict[str, Any] = ...,
        **kwargs: Any,
    ) -> Self:
        """Attach metadata to the call.

        Required: data

        Args:
            arg: a typed model instance or a dict payload (alternative to kwargs).
            id: str
            data: dict[str, Any] (required)

        Returns:
            self for chaining.
        """
        ...

    def dtmf(
        self, arg: Any = ..., /,
        id: str = ...,
        dtmf: str = ...,
        duration: int | float = ...,
        **kwargs: Any,
    ) -> Self:
        """Send DTMF tones.

        Required: dtmf

        Args:
            arg: a typed model instance or a dict payload (alternative to kwargs).
            id: str
            dtmf: str (required)
            duration: int | float

        Returns:
            self for chaining.
        """
        ...

    def dub(
        self, arg: Any = ..., /,
        id: str = ...,
        action: str = ...,
        track: str = ...,
        play: str = ...,
        say: Any = ...,
        loop: bool = ...,
        gain: Any = ...,
        **kwargs: Any,
    ) -> Self:
        """Manage audio dubbing tracks.

        Required: action, track

        Args:
            arg: a typed model instance or a dict payload (alternative to kwargs).
            id: str
            action: str (required)
            track: str (required)
            play: str
            say: Any
            loop: bool
            gain: Any

        Returns:
            self for chaining.
        """
        ...

    def message(
        self, arg: Any = ..., /,
        id: str = ...,
        to: str = ...,
        from_: str = ...,
        text: str = ...,
        media: Any = ...,
        carrier: str = ...,
        account_sid: str = ...,
        message_sid: str = ...,
        actionHook: Any = ...,
        **kwargs: Any,
    ) -> Self:
        """Send SMS/MMS message.

        Required: from, to

        Args:
            arg: a typed model instance or a dict payload (alternative to kwargs).
            id: str
            to: str (required)
            from_: str (required)
            text: str
            media: Any
            carrier: str
            account_sid: str
            message_sid: str
            actionHook: Any

        Returns:
            self for chaining.
        """
        ...

    def alert(
        self, arg: Any = ..., /,
        id: str = ...,
        message: str = ...,
        **kwargs: Any,
    ) -> Self:
        """Send SIP 180 with Alert-Info header.

        Required: message

        Args:
            arg: a typed model instance or a dict payload (alternative to kwargs).
            id: str
            message: str (required)

        Returns:
            self for chaining.
        """
        ...

    def answer(
        self, arg: Any = ..., /,
        id: str = ...,
        **kwargs: Any,
    ) -> Self:
        """Explicitly answer the call.

        Args:
            arg: a typed model instance or a dict payload (alternative to kwargs).
            id: str

        Returns:
            self for chaining.
        """
        ...

    def leave(
        self, arg: Any = ..., /,
        id: str = ...,
        **kwargs: Any,
    ) -> Self:
        """Leave a conference or queue.

        Args:
            arg: a typed model instance or a dict payload (alternative to kwargs).
            id: str

        Returns:
            self for chaining.
        """
        ...
