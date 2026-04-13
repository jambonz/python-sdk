"""Voice Agent - WebSocket example.

LLM-powered voice agent using the agent verb with tool calling.
Demonstrates agent configuration, eventHook handling, and toolHook handling.

Usage:
    python websocket_app.py
"""

import asyncio
import json

from jambonz_sdk.websocket import create_endpoint

# Application environment variables schema
env_vars = {
    "OPENAI_MODEL": {
        "type": "string",
        "description": "OpenAI model to use",
        "default": "gpt-4.1-mini",
    },
    "SYSTEM_PROMPT": {
        "type": "string",
        "description": "System prompt for the voice agent",
        "uiHint": "textarea",
        "default": "You are a helpful voice AI assistant for Acme Corp. Be concise and conversational. You can help with general questions, look up the weather, and transfer calls.",
    },
}


async def main():
    make_service, server = await create_endpoint(port=3000, env_vars=env_vars)
    svc = make_service(path="/")

    async def handle_session(session):
        # Read env vars from session data
        ev = session.data.get("env_vars", {})
        model = ev.get("OPENAI_MODEL", "gpt-4.1-mini")
        system_prompt = ev.get("SYSTEM_PROMPT", env_vars["SYSTEM_PROMPT"]["default"])

        print(f"New call: {session.call_sid} from {session.from_}")

        # Handle agent events
        async def on_event(evt):
            event_type = evt.get("type", "")
            if event_type == "turn_end":
                print(
                    f"Turn: user='{evt.get('transcript', '')}' "
                    f"agent='{evt.get('response', '')[:80]}' "
                    f"latency={evt.get('latency', {})}"
                )
            await session.reply()

        session.on("/agent-event", on_event)

        # Handle tool calls
        async def on_tool(evt):
            tool_name = evt.get("name", "")
            args = evt.get("arguments", {})
            print(f"Tool call: {tool_name}({json.dumps(args)})")

            if tool_name == "get_weather":
                result = {"temperature": 72, "condition": "sunny", "city": args.get("city", "unknown")}
            elif tool_name == "transfer_call":
                result = {"status": "transferring", "department": args.get("department", "general")}
            else:
                result = {"error": f"Unknown tool: {tool_name}"}

            await session.tool_output(evt.get("tool_call_id", ""), result)
            await session.reply()

        session.on("/tool-call", on_tool)

        # Handle agent completion
        async def on_complete(evt):
            print(f"Agent complete: {evt.get('completion_reason', 'unknown')}")
            session.hangup()
            await session.reply()

        session.on("/agent-complete", on_complete)

        # Start the agent
        session.agent(
            stt={
                "vendor": "deepgram",
                "language": "en-US",
                "deepgramOptions": {"model": "nova-3-general"},
            },
            tts={
                "vendor": "cartesia",
                "voice": "9626c31c-bec5-4cca-baa8-f8ba9e84c8bc",
            },
            llm={
                "vendor": "openai",
                "model": model,
                "llmOptions": {
                    "messages": [{"role": "system", "content": system_prompt}],
                    "tools": [
                        {
                            "type": "function",
                            "function": {
                                "name": "get_weather",
                                "description": "Get current weather for a city",
                                "parameters": {
                                    "type": "object",
                                    "properties": {
                                        "city": {"type": "string", "description": "City name"},
                                    },
                                    "required": ["city"],
                                },
                            },
                        },
                        {
                            "type": "function",
                            "function": {
                                "name": "transfer_call",
                                "description": "Transfer the caller to a department",
                                "parameters": {
                                    "type": "object",
                                    "properties": {
                                        "department": {
                                            "type": "string",
                                            "enum": ["sales", "support", "billing"],
                                        },
                                    },
                                    "required": ["department"],
                                },
                            },
                        },
                    ],
                },
            },
            turnDetection="krisp",
            earlyGeneration=True,
            bargeIn={"enable": True, "minSpeechDuration": 0.3},
            eventHook="/agent-event",
            toolHook="/tool-call",
            actionHook="/agent-complete",
        )
        await session.send()

    svc.on("session:new", handle_session)

    print("Voice agent WebSocket app listening on port 3000")
    await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
