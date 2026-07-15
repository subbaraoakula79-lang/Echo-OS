import json
from typing import List, Dict, Any, Callable
from openai import AsyncOpenAI
from core.config import settings

# Wait to initialize client until it's needed or wrap in a robust way
# for now, placeholder API key to avoid crash on startup if not set
client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY or "dummy-key")

class EchoAgent:
    def __init__(self):
        self.model = "gpt-4-turbo-preview"
        self.system_prompt = (
            "You are ECHO, an intelligent personal operating system inspired by JARVIS.\n"
            "You help the user manage tasks, information, communication and productivity.\n"
            "Rules:\n"
            "- Be concise.\n"
            "- Confirm sensitive actions before executing.\n"
            "- Never perform destructive actions without approval.\n"
            "- Remember user preferences.\n"
            "- Use available tools whenever necessary.\n"
            "- Explain actions clearly."
        )
        self.tools = []
        self.tool_map = {}

    def register_tool(self, tool_def: Dict[str, Any], func: Callable):
        self.tools.append({"type": "function", "function": tool_def})
        self.tool_map[tool_def["name"]] = func

    async def get_response(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        msgs = [{"role": "system", "content": self.system_prompt}] + messages
        kwargs = {
            "model": self.model,
            "messages": msgs,
        }
        if self.tools:
            kwargs["tools"] = self.tools
            kwargs["tool_choice"] = "auto"
            
        try:
            response = await client.chat.completions.create(**kwargs)
            c_msg = response.choices[0].message
            return {
                "role": c_msg.role,
                "content": c_msg.content,
                "tool_calls": [t.model_dump() for t in c_msg.tool_calls] if c_msg.tool_calls else None
            }
        except Exception as e:
            return {
                "role": "assistant",
                "content": f"System Error: {str(e)}",
                "tool_calls": None
            }

agent = EchoAgent()
