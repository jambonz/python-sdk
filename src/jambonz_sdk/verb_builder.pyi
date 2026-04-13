"""Auto-generated type stubs for VerbBuilder.

DO NOT EDIT — regenerate with: python scripts/generate_stubs.py
"""

from typing import Any, Self

from jambonz_sdk.types.verbs import AnyVerb

class VerbBuilder:
    _verbs: list[AnyVerb]

    def __init__(self) -> None: ...
    def to_list(self) -> list[AnyVerb]: ...

    def say(
        self,
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
        self,
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
        self,
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
        self,
        **kwargs: Any,
    ) -> Self:
        """Connect caller to OpenAI for real-time voice conversation.

        Required: llmOptions, vendor

        Args:

        Returns:
            self for chaining.
        """
        ...

    def google_s2s(
        self,
        **kwargs: Any,
    ) -> Self:
        """Connect caller to Google for real-time voice conversation.

        Required: llmOptions, vendor

        Args:

        Returns:
            self for chaining.
        """
        ...

    def deepgram_s2s(
        self,
        **kwargs: Any,
    ) -> Self:
        """Connect caller to Deepgram for real-time voice conversation.

        Required: llmOptions, vendor

        Args:

        Returns:
            self for chaining.
        """
        ...

    def elevenlabs_s2s(
        self,
        **kwargs: Any,
    ) -> Self:
        """Connect caller to ElevenLabs Conversational AI agent.

        Required: llmOptions, vendor

        Args:

        Returns:
            self for chaining.
        """
        ...

    def ultravox_s2s(
        self,
        **kwargs: Any,
    ) -> Self:
        """Connect caller to Ultravox for real-time voice conversation.

        Required: llmOptions, vendor

        Args:

        Returns:
            self for chaining.
        """
        ...

    def s2s(
        self,
        **kwargs: Any,
    ) -> Self:
        """Generic S2S verb (use when vendor is determined at runtime).

        Required: llmOptions, vendor

        Args:

        Returns:
            self for chaining.
        """
        ...

    def llm(
        self,
        **kwargs: Any,
    ) -> Self:
        """Legacy LLM verb (prefer s2s or vendor-specific shortcuts).

        Required: llmOptions, vendor

        Args:

        Returns:
            self for chaining.
        """
        ...

    def dialogflow(
        self,
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
        self,
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
        self,
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
        self,
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
        self,
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
        self,
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
        self,
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
        self,
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
        self,
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
        self,
        id: str = ...,
        headers: dict[str, Any] = ...,
        **kwargs: Any,
    ) -> Self:
        """Terminate the call.

        Args:
            id: str
            headers: dict[str, Any]

        Returns:
            self for chaining.
        """
        ...

    def redirect(
        self,
        id: str = ...,
        actionHook: Any = ...,
        statusHook: Any = ...,
        **kwargs: Any,
    ) -> Self:
        """Transfer control to a different webhook URL.

        Required: actionHook

        Args:
            id: str
            actionHook: Any (required)
            statusHook: Any

        Returns:
            self for chaining.
        """
        ...

    def pause(
        self,
        id: str = ...,
        length: int | float = ...,
        **kwargs: Any,
    ) -> Self:
        """Pause execution for a specified duration.

        Required: length

        Args:
            id: str
            length: int | float (required)

        Returns:
            self for chaining.
        """
        ...

    def sip_decline(
        self,
        id: str = ...,
        status: int | float = ...,
        reason: str = ...,
        headers: dict[str, Any] = ...,
        **kwargs: Any,
    ) -> Self:
        """Reject incoming call with a SIP error response.

        Required: status

        Args:
            id: str
            status: int | float (required)
            reason: str
            headers: dict[str, Any]

        Returns:
            self for chaining.
        """
        ...

    def sip_request(
        self,
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
        self,
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
        self,
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
        self,
        id: str = ...,
        data: dict[str, Any] = ...,
        **kwargs: Any,
    ) -> Self:
        """Attach metadata to the call.

        Required: data

        Args:
            id: str
            data: dict[str, Any] (required)

        Returns:
            self for chaining.
        """
        ...

    def dtmf(
        self,
        id: str = ...,
        dtmf: str = ...,
        duration: int | float = ...,
        **kwargs: Any,
    ) -> Self:
        """Send DTMF tones.

        Required: dtmf

        Args:
            id: str
            dtmf: str (required)
            duration: int | float

        Returns:
            self for chaining.
        """
        ...

    def dub(
        self,
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
        self,
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
        self,
        id: str = ...,
        message: str = ...,
        **kwargs: Any,
    ) -> Self:
        """Send SIP 180 with Alert-Info header.

        Required: message

        Args:
            id: str
            message: str (required)

        Returns:
            self for chaining.
        """
        ...

    def answer(
        self,
        id: str = ...,
        **kwargs: Any,
    ) -> Self:
        """Explicitly answer the call.

        Args:
            id: str

        Returns:
            self for chaining.
        """
        ...

    def leave(
        self,
        id: str = ...,
        **kwargs: Any,
    ) -> Self:
        """Leave a conference or queue.

        Args:
            id: str

        Returns:
            self for chaining.
        """
        ...
