from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmResponse
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.tool_context import ToolContext


class BaseTracer(ABC):
    def __init__(self, endpoint: str, app_key: str):
        self.endpoint = endpoint
        self.app_key = app_key

    @abstractmethod
    def upload_data(self, agent_name: str, event: str, data: dict):
        pass

    @classmethod
    def get_callbacks(cls, instance) -> list:
        def after_model_callback(
            callback_context: CallbackContext, llm_response: LlmResponse
        ) -> Optional[LlmResponse]:
            agent_name = callback_context.agent_name
            data = {"model_name": "", "prompt": "", "response": ""}
            instance.upload_data(agent_name=agent_name, event="Model call", data=data)

        def after_tool_callback(
            tool: BaseTool,
            args: Dict[str, Any],
            tool_context: ToolContext,
            tool_response: Dict,
        ) -> Optional[Dict]:
            agent_name = tool_context.agent_name
            data = {"tool_name": "", "args": {}, "response": ""}
            instance.upload_data(agent_name=agent_name, event="Tool call", data=data)

        return {
            "after_model_callback": after_model_callback,
            "after_tool_callback": after_tool_callback,
        }
