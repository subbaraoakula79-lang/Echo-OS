"""
ECHO OS — AI Agent Core
Agentic loop with tool calling, streaming, and memory-aware conversations.
"""

import json
import logging
from typing import List, Dict, Any, Optional, AsyncGenerator, Callable, Awaitable

from openai import AsyncOpenAI

from core.config import settings

logger = logging.getLogger(__name__)

# Initialize client (deferred key check to runtime)
_client: Optional[AsyncOpenAI] = None


def _get_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        if not settings.OPENAI_API_KEY:
            raise RuntimeError("OPENAI_API_KEY is not set")
        _client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    return _client


class EchoAgent:
    """
    The ECHO Agent orchestrates:
    1. Intent detection via the LLM
    2. Tool selection and execution
    3. Multi-turn tool calling loops
    4. Streaming responses
    5. Memory-aware context injection
    """

    def __init__(self):
        self.model = settings.OPENAI_MODEL
        self.system_prompt = settings.SYSTEM_PROMPT
        self.tools: List[Dict[str, Any]] = []
        self.tool_map: Dict[str, Callable[..., Awaitable[Dict[str, Any]]]] = {}

    def register_tool(self, tool_def: Dict[str, Any], func: Callable[..., Awaitable[Dict[str, Any]]]):
        """Register a tool with its OpenAI function definition and async handler."""
        self.tools.append({"type": "function", "function": tool_def})
        self.tool_map[tool_def["name"]] = func
        logger.info(f"Registered tool: {tool_def['name']}")

    async def _execute_tool(self, tool_name: str, arguments: str) -> Dict[str, Any]:
        """Execute a registered tool by name with JSON arguments."""
        if tool_name not in self.tool_map:
            return {"error": f"Unknown tool: {tool_name}"}

        try:
            args = json.loads(arguments)
            logger.info(f"Executing tool '{tool_name}' with args: {args}")
            result = await self.tool_map[tool_name](**args)
            logger.info(f"Tool '{tool_name}' returned: {result}")
            return result
        except json.JSONDecodeError:
            return {"error": f"Invalid arguments for tool {tool_name}"}
        except Exception as e:
            logger.error(f"Tool execution error ({tool_name}): {e}")
            return {"error": str(e)}

    def _build_messages(
        self,
        user_message: str,
        conversation_history: List[Dict[str, Any]],
        memory_context: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Build the full message array for the API call."""
        system_content = self.system_prompt
        if memory_context:
            system_content += (
                f"\n\n--- User Memory Context ---\n{memory_context}\n--- End Memory ---"
            )

        messages = [{"role": "system", "content": system_content}]
        messages.extend(conversation_history)
        messages.append({"role": "user", "content": user_message})
        return messages

    async def get_response(
        self,
        user_message: str,
        conversation_history: Optional[List[Dict[str, Any]]] = None,
        memory_context: Optional[str] = None,
        max_tool_rounds: int = 5,
    ) -> Dict[str, Any]:
        """
        Full agentic response loop:
        1. Send message to LLM
        2. If LLM requests tool calls, execute them
        3. Feed results back to LLM
        4. Repeat until LLM gives a text response (or max rounds)
        """
        client = _get_client()
        messages = self._build_messages(
            user_message,
            conversation_history or [],
            memory_context,
        )

        tool_results = []

        for round_num in range(max_tool_rounds):
            kwargs: Dict[str, Any] = {
                "model": self.model,
                "messages": messages,
            }
            if self.tools:
                kwargs["tools"] = self.tools
                kwargs["tool_choice"] = "auto"

            try:
                response = await client.chat.completions.create(**kwargs)
                choice = response.choices[0]
                assistant_msg = choice.message

                # If no tool calls, return the text response
                if not assistant_msg.tool_calls:
                    return {
                        "role": "assistant",
                        "content": assistant_msg.content or "",
                        "tool_calls": None,
                        "tool_results": tool_results if tool_results else None,
                        "usage": {
                            "prompt_tokens": response.usage.prompt_tokens,
                            "completion_tokens": response.usage.completion_tokens,
                        } if response.usage else None,
                    }

                # Tool calls requested — execute them
                messages.append(assistant_msg.model_dump(exclude_none=True))

                for tool_call in assistant_msg.tool_calls:
                    result = await self._execute_tool(
                        tool_call.function.name,
                        tool_call.function.arguments,
                    )
                    tool_results.append({
                        "tool": tool_call.function.name,
                        "arguments": json.loads(tool_call.function.arguments),
                        "result": result,
                    })
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(result, default=str),
                    })

            except Exception as e:
                logger.error(f"Agent error (round {round_num}): {e}")
                return {
                    "role": "assistant",
                    "content": f"I encountered an error processing your request: {str(e)}",
                    "tool_calls": None,
                    "tool_results": tool_results if tool_results else None,
                    "usage": None,
                }

        # Max rounds exceeded
        return {
            "role": "assistant",
            "content": "I've completed the available tool operations. Is there anything else you need?",
            "tool_calls": None,
            "tool_results": tool_results,
            "usage": None,
        }

    async def stream_response(
        self,
        user_message: str,
        conversation_history: Optional[List[Dict[str, Any]]] = None,
        memory_context: Optional[str] = None,
    ) -> AsyncGenerator[str, None]:
        """Stream a text response token-by-token. Falls back to non-streaming for tool calls."""
        client = _get_client()
        messages = self._build_messages(
            user_message,
            conversation_history or [],
            memory_context,
        )

        kwargs: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "stream": True,
        }
        if self.tools:
            kwargs["tools"] = self.tools
            kwargs["tool_choice"] = "auto"

        try:
            stream = await client.chat.completions.create(**kwargs)
            collected_tool_calls = []
            tool_call_args: Dict[int, str] = {}

            async for chunk in stream:
                delta = chunk.choices[0].delta

                # Streaming text content
                if delta.content:
                    yield delta.content

                # Collecting tool call deltas
                if delta.tool_calls:
                    for tc_delta in delta.tool_calls:
                        idx = tc_delta.index
                        if idx not in tool_call_args:
                            tool_call_args[idx] = ""
                            collected_tool_calls.append(tc_delta)
                        if tc_delta.function and tc_delta.function.arguments:
                            tool_call_args[idx] += tc_delta.function.arguments

            # If tool calls were collected, execute them and get final response
            if collected_tool_calls:
                yield "\n\n*Executing requested actions...*\n\n"
                full_response = await self.get_response(
                    user_message, conversation_history or [], memory_context
                )
                yield full_response.get("content", "")

        except Exception as e:
            logger.error(f"Stream error: {e}")
            yield f"I encountered an error: {str(e)}"


# Global agent instance
agent = EchoAgent()
