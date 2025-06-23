from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmResponse
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.tool_context import ToolContext
from src.config import settings


class BaseTracer(ABC):
    def __init__(self, endpoint: str, app_key: str):
        self.endpoint = endpoint
        self.app_key = app_key
        self.data = []

    @abstractmethod
    def upload_data(self):
        pass

    @classmethod
    def get_callbacks(cls, instance) -> dict:
        def after_model_callback(
            callback_context: CallbackContext, llm_response: LlmResponse
        ) -> Optional[LlmResponse]:
            agent_name = callback_context.agent_name
            # prompts
            prompts = []
            if (
                callback_context.user_content.role == "user"
                and callback_context.user_content.parts
            ):
                for part in callback_context.user_content.parts:
                    if part.text is not None:
                        prompts.append(part.text)
                    else:
                        prompts.append("")
            # responses
            responses = []
            if llm_response.content.role == "model" and llm_response.content.parts:
                for part in llm_response.content.parts:
                    if part.text is not None:
                        responses.append(part.text)
                    else:
                        responses.append("")
            data = {
                "model_name": settings.model,
                "prompt": prompts,
                "response": responses,
            }
            # event parts
            instance.data.append(
                {"agent_name": agent_name, "event": "model_call", "data": data}
            )

        def after_tool_callback(
            tool: BaseTool,
            args: Dict[str, Any],
            tool_context: ToolContext,
            tool_response: Dict,
        ) -> Optional[Dict]:
            agent_name = tool_context.agent_name
            data = {"tool_name": tool.name, "args": args, "response": tool_response}
            instance.data.append(
                {"agent_name": agent_name, "event": "tool_call", "data": data}
            )

        return {
            "after_model_callback": after_model_callback,
            "after_tool_callback": after_tool_callback,
        }
