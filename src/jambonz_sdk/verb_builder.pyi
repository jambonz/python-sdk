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
        text: str | list[Any] = ...,
        instructions: str = ...,
        stream: bool = ...,
        loop: int | float | str = ...,
        synthesizer: dict[str, Any] = ...,
        earlyMedia: bool = ...,
        disableTtsCache: bool = ...,
        closeStreamOnEmpty: bool = ...,
        **kwargs: Any,
    ) -> Self:
        """Speak text using TTS.

        Args:
            id: str
            text: str | list[Any]
            instructions: str
            stream: bool
            loop: int | float | str
            synthesizer: dict[str, Any]
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
        url: str | list[Any] = ...,
        loop: int | float | str = ...,
        earlyMedia: bool = ...,
        seekOffset: int | float | str = ...,
        timeoutSecs: int | float | str = ...,
        actionHook: dict[str, Any] | str = ...,
        **kwargs: Any,
    ) -> Self:
        """Play an audio file from a URL.

        Required: url

        Args:
            id: str
            url: str | list[Any] (required)
            loop: int | float | str
            earlyMedia: bool
            seekOffset: int | float | str
            timeoutSecs: int | float | str
            actionHook: dict[str, Any] | str

        Returns:
            self for chaining.
        """
        ...

    def gather(
        self,
        id: str = ...,
        actionHook: dict[str, Any] | str = ...,
        finishOnKey: str = ...,
        input: list[Any] = ...,
        numDigits: int | float = ...,
        minDigits: int | float = ...,
        maxDigits: int | float = ...,
        interDigitTimeout: int | float = ...,
        partialResultHook: dict[str, Any] | str = ...,
        speechTimeout: int | float = ...,
        listenDuringPrompt: bool = ...,
        dtmfBargein: bool = ...,
        bargein: bool = ...,
        minBargeinWordCount: int | float = ...,
        timeout: int | float = ...,
        recognizer: dict[str, Any] = ...,
        play: dict[str, Any] = ...,
        say: dict[str, Any] = ...,
        fillerNoise: dict[str, Any] = ...,
        actionHookDelayAction: dict[str, Any] = ...,
        **kwargs: Any,
    ) -> Self:
        """Collect speech (STT) and/or DTMF input.

        Args:
            id: str
            actionHook: dict[str, Any] | str
            finishOnKey: str
            input: list[Any]
            numDigits: int | float
            minDigits: int | float
            maxDigits: int | float
            interDigitTimeout: int | float
            partialResultHook: dict[str, Any] | str
            speechTimeout: int | float
            listenDuringPrompt: bool
            dtmfBargein: bool
            bargein: bool
            minBargeinWordCount: int | float
            timeout: int | float
            recognizer: dict[str, Any]
            play: dict[str, Any]
            say: dict[str, Any]
            fillerNoise: dict[str, Any]
            actionHookDelayAction: dict[str, Any]

        Returns:
            self for chaining.
        """
        ...

    def openai_s2s(
        self,
        id: str = ...,
        vendor: str = ...,
        model: str = ...,
        auth: dict[str, Any] = ...,
        connectOptions: dict[str, Any] = ...,
        mcpServers: list[Any] = ...,
        actionHook: dict[str, Any] | str = ...,
        eventHook: dict[str, Any] | str = ...,
        toolHook: dict[str, Any] | str = ...,
        events: list[Any] = ...,
        llmOptions: dict[str, Any] = ...,
        **kwargs: Any,
    ) -> Self:
        """Connect caller to OpenAI for real-time voice conversation.

        Required: llmOptions, vendor

        Args:
            id: str
            vendor: str (required)
            model: str
            auth: dict[str, Any]
            connectOptions: dict[str, Any]
            mcpServers: list[Any]
            actionHook: dict[str, Any] | str
            eventHook: dict[str, Any] | str
            toolHook: dict[str, Any] | str
            events: list[Any]
            llmOptions: dict[str, Any] (required)

        Returns:
            self for chaining.
        """
        ...

    def google_s2s(
        self,
        id: str = ...,
        vendor: str = ...,
        model: str = ...,
        auth: dict[str, Any] = ...,
        connectOptions: dict[str, Any] = ...,
        mcpServers: list[Any] = ...,
        actionHook: dict[str, Any] | str = ...,
        eventHook: dict[str, Any] | str = ...,
        toolHook: dict[str, Any] | str = ...,
        events: list[Any] = ...,
        llmOptions: dict[str, Any] = ...,
        **kwargs: Any,
    ) -> Self:
        """Connect caller to Google for real-time voice conversation.

        Required: llmOptions, vendor

        Args:
            id: str
            vendor: str (required)
            model: str
            auth: dict[str, Any]
            connectOptions: dict[str, Any]
            mcpServers: list[Any]
            actionHook: dict[str, Any] | str
            eventHook: dict[str, Any] | str
            toolHook: dict[str, Any] | str
            events: list[Any]
            llmOptions: dict[str, Any] (required)

        Returns:
            self for chaining.
        """
        ...

    def deepgram_s2s(
        self,
        id: str = ...,
        vendor: str = ...,
        model: str = ...,
        auth: dict[str, Any] = ...,
        connectOptions: dict[str, Any] = ...,
        mcpServers: list[Any] = ...,
        actionHook: dict[str, Any] | str = ...,
        eventHook: dict[str, Any] | str = ...,
        toolHook: dict[str, Any] | str = ...,
        events: list[Any] = ...,
        llmOptions: dict[str, Any] = ...,
        **kwargs: Any,
    ) -> Self:
        """Connect caller to Deepgram for real-time voice conversation.

        Required: llmOptions, vendor

        Args:
            id: str
            vendor: str (required)
            model: str
            auth: dict[str, Any]
            connectOptions: dict[str, Any]
            mcpServers: list[Any]
            actionHook: dict[str, Any] | str
            eventHook: dict[str, Any] | str
            toolHook: dict[str, Any] | str
            events: list[Any]
            llmOptions: dict[str, Any] (required)

        Returns:
            self for chaining.
        """
        ...

    def elevenlabs_s2s(
        self,
        id: str = ...,
        vendor: str = ...,
        model: str = ...,
        auth: dict[str, Any] = ...,
        connectOptions: dict[str, Any] = ...,
        mcpServers: list[Any] = ...,
        actionHook: dict[str, Any] | str = ...,
        eventHook: dict[str, Any] | str = ...,
        toolHook: dict[str, Any] | str = ...,
        events: list[Any] = ...,
        llmOptions: dict[str, Any] = ...,
        **kwargs: Any,
    ) -> Self:
        """Connect caller to ElevenLabs Conversational AI agent.

        Required: llmOptions, vendor

        Args:
            id: str
            vendor: str (required)
            model: str
            auth: dict[str, Any]
            connectOptions: dict[str, Any]
            mcpServers: list[Any]
            actionHook: dict[str, Any] | str
            eventHook: dict[str, Any] | str
            toolHook: dict[str, Any] | str
            events: list[Any]
            llmOptions: dict[str, Any] (required)

        Returns:
            self for chaining.
        """
        ...

    def ultravox_s2s(
        self,
        id: str = ...,
        vendor: str = ...,
        model: str = ...,
        auth: dict[str, Any] = ...,
        connectOptions: dict[str, Any] = ...,
        mcpServers: list[Any] = ...,
        actionHook: dict[str, Any] | str = ...,
        eventHook: dict[str, Any] | str = ...,
        toolHook: dict[str, Any] | str = ...,
        events: list[Any] = ...,
        llmOptions: dict[str, Any] = ...,
        **kwargs: Any,
    ) -> Self:
        """Connect caller to Ultravox for real-time voice conversation.

        Required: llmOptions, vendor

        Args:
            id: str
            vendor: str (required)
            model: str
            auth: dict[str, Any]
            connectOptions: dict[str, Any]
            mcpServers: list[Any]
            actionHook: dict[str, Any] | str
            eventHook: dict[str, Any] | str
            toolHook: dict[str, Any] | str
            events: list[Any]
            llmOptions: dict[str, Any] (required)

        Returns:
            self for chaining.
        """
        ...

    def s2s(
        self,
        id: str = ...,
        vendor: str = ...,
        model: str = ...,
        auth: dict[str, Any] = ...,
        connectOptions: dict[str, Any] = ...,
        mcpServers: list[Any] = ...,
        actionHook: dict[str, Any] | str = ...,
        eventHook: dict[str, Any] | str = ...,
        toolHook: dict[str, Any] | str = ...,
        events: list[Any] = ...,
        llmOptions: dict[str, Any] = ...,
        **kwargs: Any,
    ) -> Self:
        """Generic S2S verb (use when vendor is determined at runtime).

        Required: llmOptions, vendor

        Args:
            id: str
            vendor: str (required)
            model: str
            auth: dict[str, Any]
            connectOptions: dict[str, Any]
            mcpServers: list[Any]
            actionHook: dict[str, Any] | str
            eventHook: dict[str, Any] | str
            toolHook: dict[str, Any] | str
            events: list[Any]
            llmOptions: dict[str, Any] (required)

        Returns:
            self for chaining.
        """
        ...

    def llm(
        self,
        id: str = ...,
        vendor: str = ...,
        model: str = ...,
        auth: dict[str, Any] = ...,
        connectOptions: dict[str, Any] = ...,
        mcpServers: list[Any] = ...,
        actionHook: dict[str, Any] | str = ...,
        eventHook: dict[str, Any] | str = ...,
        toolHook: dict[str, Any] | str = ...,
        events: list[Any] = ...,
        llmOptions: dict[str, Any] = ...,
        **kwargs: Any,
    ) -> Self:
        """Legacy LLM verb (prefer s2s or vendor-specific shortcuts).

        Required: llmOptions, vendor

        Args:
            id: str
            vendor: str (required)
            model: str
            auth: dict[str, Any]
            connectOptions: dict[str, Any]
            mcpServers: list[Any]
            actionHook: dict[str, Any] | str
            eventHook: dict[str, Any] | str
            toolHook: dict[str, Any] | str
            events: list[Any]
            llmOptions: dict[str, Any] (required)

        Returns:
            self for chaining.
        """
        ...

    def dialogflow(
        self,
        id: str = ...,
        credentials: dict[str, Any] | str = ...,
        project: str = ...,
        agent: str = ...,
        environment: str = ...,
        region: str = ...,
        model: str = ...,
        lang: str = ...,
        actionHook: dict[str, Any] | str = ...,
        eventHook: dict[str, Any] | str = ...,
        events: list[Any] = ...,
        welcomeEvent: str = ...,
        welcomeEventParams: dict[str, Any] = ...,
        noInputTimeout: int | float = ...,
        noInputEvent: str = ...,
        passDtmfAsTextInput: bool = ...,
        thinkingMusic: str = ...,
        tts: dict[str, Any] = ...,
        bargein: bool = ...,
        queryInput: dict[str, Any] = ...,
        **kwargs: Any,
    ) -> Self:
        """Connect caller to Google Dialogflow agent.

        Required: credentials, lang, project

        Args:
            id: str
            credentials: dict[str, Any] | str (required)
            project: str (required)
            agent: str
            environment: str
            region: str
            model: str
            lang: str (required)
            actionHook: dict[str, Any] | str
            eventHook: dict[str, Any] | str
            events: list[Any]
            welcomeEvent: str
            welcomeEventParams: dict[str, Any]
            noInputTimeout: int | float
            noInputEvent: str
            passDtmfAsTextInput: bool
            thinkingMusic: str
            tts: dict[str, Any]
            bargein: bool
            queryInput: dict[str, Any]

        Returns:
            self for chaining.
        """
        ...

    def pipeline(
        self,
        id: str = ...,
        stt: dict[str, Any] = ...,
        tts: dict[str, Any] = ...,
        llm: dict[str, Any] = ...,
        turnDetection: str | dict[str, Any] = ...,
        bargeIn: dict[str, Any] = ...,
        actionHook: dict[str, Any] | str = ...,
        eventHook: dict[str, Any] | str = ...,
        toolHook: dict[str, Any] | str = ...,
        greeting: bool = ...,
        earlyGeneration: bool = ...,
        noiseIsolation: str | dict[str, Any] = ...,
        mcpServers: list[Any] = ...,
        noResponseTimeout: int | float = ...,
        **kwargs: Any,
    ) -> Self:
        """Integrated STT → LLM → TTS voice AI pipeline.

        Required: llm

        Args:
            id: str
            stt: dict[str, Any]
            tts: dict[str, Any]
            llm: dict[str, Any] (required)
            turnDetection: str | dict[str, Any]
            bargeIn: dict[str, Any]
            actionHook: dict[str, Any] | str
            eventHook: dict[str, Any] | str
            toolHook: dict[str, Any] | str
            greeting: bool
            earlyGeneration: bool
            noiseIsolation: str | dict[str, Any]
            mcpServers: list[Any]
            noResponseTimeout: int | float

        Returns:
            self for chaining.
        """
        ...

    def listen(
        self,
        id: str = ...,
        actionHook: dict[str, Any] | str = ...,
        auth: dict[str, Any] = ...,
        finishOnKey: str = ...,
        maxLength: int | float = ...,
        metadata: dict[str, Any] = ...,
        mixType: str = ...,
        passDtmf: bool = ...,
        playBeep: bool = ...,
        disableBidirectionalAudio: bool = ...,
        bidirectionalAudio: dict[str, Any] = ...,
        sampleRate: int | float = ...,
        timeout: int | float = ...,
        transcribe: dict[str, Any] = ...,
        url: str = ...,
        wsAuth: dict[str, Any] = ...,
        earlyMedia: bool = ...,
        channel: int | float = ...,
        **kwargs: Any,
    ) -> Self:
        """Stream real-time audio to a websocket endpoint.

        Required: url

        Args:
            id: str
            actionHook: dict[str, Any] | str
            auth: dict[str, Any]
            finishOnKey: str
            maxLength: int | float
            metadata: dict[str, Any]
            mixType: str
            passDtmf: bool
            playBeep: bool
            disableBidirectionalAudio: bool
            bidirectionalAudio: dict[str, Any]
            sampleRate: int | float
            timeout: int | float
            transcribe: dict[str, Any]
            url: str (required)
            wsAuth: dict[str, Any]
            earlyMedia: bool
            channel: int | float

        Returns:
            self for chaining.
        """
        ...

    def stream(
        self,
        id: str = ...,
        actionHook: dict[str, Any] | str = ...,
        auth: dict[str, Any] = ...,
        finishOnKey: str = ...,
        maxLength: int | float = ...,
        metadata: dict[str, Any] = ...,
        mixType: str = ...,
        passDtmf: bool = ...,
        playBeep: bool = ...,
        disableBidirectionalAudio: bool = ...,
        bidirectionalAudio: dict[str, Any] = ...,
        sampleRate: int | float = ...,
        timeout: int | float = ...,
        transcribe: dict[str, Any] = ...,
        url: str = ...,
        wsAuth: dict[str, Any] = ...,
        earlyMedia: bool = ...,
        channel: int | float = ...,
        **kwargs: Any,
    ) -> Self:
        """Stream real-time audio (preferred alias for listen).

        Required: url

        Args:
            id: str
            actionHook: dict[str, Any] | str
            auth: dict[str, Any]
            finishOnKey: str
            maxLength: int | float
            metadata: dict[str, Any]
            mixType: str
            passDtmf: bool
            playBeep: bool
            disableBidirectionalAudio: bool
            bidirectionalAudio: dict[str, Any]
            sampleRate: int | float
            timeout: int | float
            transcribe: dict[str, Any]
            url: str (required)
            wsAuth: dict[str, Any]
            earlyMedia: bool
            channel: int | float

        Returns:
            self for chaining.
        """
        ...

    def transcribe(
        self,
        id: str = ...,
        transcriptionHook: str = ...,
        translationHook: str = ...,
        recognizer: dict[str, Any] = ...,
        earlyMedia: bool = ...,
        channel: int | float = ...,
        **kwargs: Any,
    ) -> Self:
        """Enable real-time call transcription.

        Args:
            id: str
            transcriptionHook: str
            translationHook: str
            recognizer: dict[str, Any]
            earlyMedia: bool
            channel: int | float

        Returns:
            self for chaining.
        """
        ...

    def dial(
        self,
        id: str = ...,
        actionHook: dict[str, Any] | str = ...,
        onHoldHook: dict[str, Any] | str = ...,
        answerOnBridge: bool = ...,
        callerId: str = ...,
        callerName: str = ...,
        confirmHook: dict[str, Any] | str = ...,
        referHook: dict[str, Any] | str = ...,
        dialMusic: str = ...,
        dtmfCapture: dict[str, Any] = ...,
        dtmfHook: dict[str, Any] | str = ...,
        headers: dict[str, Any] = ...,
        anchorMedia: bool = ...,
        exitMediaPath: bool = ...,
        boostAudioSignal: int | float | str = ...,
        listen: dict[str, Any] = ...,
        stream: dict[str, Any] = ...,
        target: list[Any] = ...,
        timeLimit: int | float = ...,
        timeout: int | float = ...,
        proxy: str = ...,
        transcribe: dict[str, Any] = ...,
        amd: dict[str, Any] = ...,
        dub: list[Any] = ...,
        tag: dict[str, Any] = ...,
        forwardPAI: bool = ...,
        **kwargs: Any,
    ) -> Self:
        """Place outbound call and bridge to current caller.

        Required: target

        Args:
            id: str
            actionHook: dict[str, Any] | str
            onHoldHook: dict[str, Any] | str
            answerOnBridge: bool
            callerId: str
            callerName: str
            confirmHook: dict[str, Any] | str
            referHook: dict[str, Any] | str
            dialMusic: str
            dtmfCapture: dict[str, Any]
            dtmfHook: dict[str, Any] | str
            headers: dict[str, Any]
            anchorMedia: bool
            exitMediaPath: bool
            boostAudioSignal: int | float | str
            listen: dict[str, Any]
            stream: dict[str, Any]
            target: list[Any] (required)
            timeLimit: int | float
            timeout: int | float
            proxy: str
            transcribe: dict[str, Any]
            amd: dict[str, Any]
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
        actionHook: dict[str, Any] | str = ...,
        waitHook: dict[str, Any] | str = ...,
        statusEvents: list[Any] = ...,
        statusHook: dict[str, Any] | str = ...,
        enterHook: dict[str, Any] | str = ...,
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
            actionHook: dict[str, Any] | str
            waitHook: dict[str, Any] | str
            statusEvents: list[Any]
            statusHook: dict[str, Any] | str
            enterHook: dict[str, Any] | str
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
        actionHook: dict[str, Any] | str = ...,
        waitHook: dict[str, Any] | str = ...,
        priority: int | float = ...,
        _: dict[str, Any] = ...,
        **kwargs: Any,
    ) -> Self:
        """Place caller into a named call queue.

        Required: name

        Args:
            id: str
            name: str (required)
            actionHook: dict[str, Any] | str
            waitHook: dict[str, Any] | str
            priority: int | float
            _: dict[str, Any]

        Returns:
            self for chaining.
        """
        ...

    def dequeue(
        self,
        id: str = ...,
        name: str = ...,
        actionHook: dict[str, Any] | str = ...,
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
            actionHook: dict[str, Any] | str
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
        actionHook: dict[str, Any] | str = ...,
        statusHook: dict[str, Any] | str = ...,
        **kwargs: Any,
    ) -> Self:
        """Transfer control to a different webhook URL.

        Required: actionHook

        Args:
            id: str
            actionHook: dict[str, Any] | str (required)
            statusHook: dict[str, Any] | str

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
        actionHook: dict[str, Any] | str = ...,
        **kwargs: Any,
    ) -> Self:
        """Send a SIP request within the current dialog.

        Required: method

        Args:
            id: str
            method: str (required)
            body: str
            headers: dict[str, Any]
            actionHook: dict[str, Any] | str

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
        actionHook: dict[str, Any] | str = ...,
        eventHook: dict[str, Any] | str = ...,
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
            actionHook: dict[str, Any] | str
            eventHook: dict[str, Any] | str

        Returns:
            self for chaining.
        """
        ...

    def config(
        self,
        id: str = ...,
        synthesizer: dict[str, Any] = ...,
        recognizer: dict[str, Any] = ...,
        bargeIn: dict[str, Any] = ...,
        ttsStream: dict[str, Any] = ...,
        record: dict[str, Any] = ...,
        listen: dict[str, Any] = ...,
        stream: dict[str, Any] = ...,
        transcribe: dict[str, Any] = ...,
        amd: dict[str, Any] = ...,
        fillerNoise: dict[str, Any] = ...,
        notifyEvents: bool = ...,
        notifySttLatency: bool = ...,
        reset: str | list[Any] = ...,
        onHoldMusic: str = ...,
        actionHookDelayAction: dict[str, Any] = ...,
        sipRequestWithinDialogHook: dict[str, Any] | str = ...,
        boostAudioSignal: int | float | str = ...,
        vad: dict[str, Any] = ...,
        referHook: dict[str, Any] | str = ...,
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
            synthesizer: dict[str, Any]
            recognizer: dict[str, Any]
            bargeIn: dict[str, Any]
            ttsStream: dict[str, Any]
            record: dict[str, Any]
            listen: dict[str, Any]
            stream: dict[str, Any]
            transcribe: dict[str, Any]
            amd: dict[str, Any]
            fillerNoise: dict[str, Any]
            notifyEvents: bool
            notifySttLatency: bool
            reset: str | list[Any]
            onHoldMusic: str
            actionHookDelayAction: dict[str, Any]
            sipRequestWithinDialogHook: dict[str, Any] | str
            boostAudioSignal: int | float | str
            vad: dict[str, Any]
            referHook: dict[str, Any] | str
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
        say: str | dict[str, Any] = ...,
        loop: bool = ...,
        gain: int | float | str = ...,
        **kwargs: Any,
    ) -> Self:
        """Manage audio dubbing tracks.

        Required: action, track

        Args:
            id: str
            action: str (required)
            track: str (required)
            play: str
            say: str | dict[str, Any]
            loop: bool
            gain: int | float | str

        Returns:
            self for chaining.
        """
        ...

    def message(
        self,
        id: str = ...,
        carrier: str = ...,
        account_sid: str = ...,
        message_sid: str = ...,
        to: str = ...,
        from_: str = ...,
        text: str = ...,
        media: str | list[Any] = ...,
        actionHook: dict[str, Any] | str = ...,
        **kwargs: Any,
    ) -> Self:
        """Send SMS/MMS message.

        Required: from, to

        Args:
            id: str
            carrier: str
            account_sid: str
            message_sid: str
            to: str (required)
            from_: str (required)
            text: str
            media: str | list[Any]
            actionHook: dict[str, Any] | str

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
