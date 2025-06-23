import asyncio

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseServerParams
from google.genai import types
from pydantic import BaseModel

import src.tools.call_agent as call_agent_module
from src.config import settings
from src.memory.short_term_memory import ShortTermMemory
from src.prompts.agent_calling_prompt import (
    AGENT_CALLING_PROMPT,
    SUB_AGENT_INFO_TEMPLATE,
)
from src.prompts.knowledgebase_prompt import (
    KNOWLEDGEBASE_DOC_TEMPLATE,
    KNOWLEDGEBASE_PROMPT,
)
from src.prompts.long_term_memory_prompt import (
    LONG_TERM_MEMORY_PROMPT,
    SINGLE_MEMORY_TEMPLATE,
)
from src.sampling.sampler import Sampler
from src.tools.call_agent import call_agent
from src.tracing.tracer_factory import TracerFactory
from src.utils.logger import get_logger

logger = get_logger(__name__)


def create_reasoning_model(
    model_provider: str, model: str, api_key: str, api_base: str
):
    return LiteLlm(
        model=f"{model_provider}/{model}",
        api_key=api_key,
        api_base=api_base,
    )


class Agent:
    def __init__(
        self,
        name: str,
        description: str,
        model: str = settings.model,
        api_key: str = settings.model_api_key,
        api_base: str = settings.model_api_base_url,
        system_prompt: str = "",
        user_prompt_template: str = "{prompt}",
        tools: list = [],
        mcp_servers: list = [],
        sub_agents: list = [],
        knowledgebase=None,
        short_term_memory=None,
        long_term_memory=None,
        input_schema=None,
        output_schema=None,
        enable_sampling: bool = False,
        enable_tracing: bool = False,
    ) -> None:
        logger.debug(f"Initializing {name} agent with {model} model.")

        self.name = name
        self.description = description
        self.model = create_reasoning_model(
            model_provider=settings.model_provider,
            model=model,
            api_key=api_key,
            api_base=api_base,
        )
        self.system_prompt = system_prompt

        self.tools = tools
        for mcp_server in mcp_servers:
            mcp_tool = MCPToolset(
                connection_params=SseServerParams(
                    url=mcp_server,
                )
            )
            self.tools.append(mcp_tool)

        if sub_agents != []:
            self._add_sub_agents(sub_agents)

        if enable_tracing:
            self.tracer = TracerFactory(type="APMPlus")
            callbacks = self.tracer.get_callbacks(self.tracer)
            self.agent = LlmAgent(
                name=self.name,
                description=self.description,
                instruction=self.system_prompt,
                model=self.model,
                tools=self.tools,
                # use callbacks to upload data to tracing system (e.g., Volcengine APMPlus)
                after_model_callback=callbacks["after_model_callback"],
                after_tool_callback=callbacks["after_tool_callback"],
            )
        else:
            self.agent = LlmAgent(
                name=self.name,
                description=self.description,
                instruction=self.system_prompt,
                model=self.model,
                tools=self.tools,
            )

        self.user_prompt_template = user_prompt_template
        self.knowledgebase = knowledgebase

        if short_term_memory is None:
            self.short_term_memory = asyncio.run(ShortTermMemory.create())
        else:
            self.short_term_memory = short_term_memory
        self.long_term_memory = long_term_memory

        self.runner = Runner(
            agent=self.agent,
            app_name=self.short_term_memory.app_name,
            session_service=self.short_term_memory.session_service,
        )

        self.input_schema = input_schema
        self.output_schema = output_schema
        self.input_schema_str = ""
        self.output_schema_str = ""
        self._process_schemas()

        self.enable_sampling = enable_sampling
        self.called_tools = []
        if enable_sampling:
            logger.info(f"Enable sampling for {self.name} agent.")
            self.sampler = Sampler(
                agent=self, dataset_name="agents", dataset_path="datasets"
            )
        else:
            self.sampler = None

        # register self to support protential call_agent function
        call_agent_module.AGENTS[self.name] = self

    def _add_sub_agents(self, sub_agents: list) -> None:
        self.system_prompt += AGENT_CALLING_PROMPT
        for sub_agent in sub_agents:
            self.system_prompt += SUB_AGENT_INFO_TEMPLATE.format(
                id=sub_agents.index(sub_agent),
                name=sub_agent.name,
                description=sub_agent.description,
                input_schema=sub_agent.input_schema_str
                if sub_agent.input_schema_str != ""
                else "No provided, you can choose a suitable prompt to call this agent.",
                output_schema=sub_agent.output_schema_str
                if sub_agent.output_schema_str != ""
                else "No provided, you should understand the subagent outputs by its description.",
            )
        self.tools.append(call_agent)

    def _process_schemas(self):
        schemas = ""
        if self.input_schema is not None:
            if not issubclass(self.input_schema, BaseModel):
                logger.warning("input_schema must be a subclass of BaseModel. Skip!")
            else:
                schemas += f"\n<input> {self.input_schema.model_fields} </input>\n"
                self.input_schema_str = str(self.input_schema.model_fields)

        if self.output_schema is not None:
            if not issubclass(self.output_schema, BaseModel):
                logger.warning("output_schema must be a subclass of BaseModel. Skip!")
            else:
                schemas += f"\n<output> {self.output_schema.model_fields} </output>\n"
                self.output_schema_str = str(self.output_schema.model_fields)

        self.system_prompt += schemas

    def _build_knowledgebase_rag_prompt(self, prompt: str, documents: list[str]):
        if documents != []:
            prompt += KNOWLEDGEBASE_PROMPT
            for i in range(len(documents)):
                prompt += KNOWLEDGEBASE_DOC_TEMPLATE.format(
                    id=str(i + 1), content=documents[i]
                )
        return prompt

    def _build_longterm_memory_rag_prompt(self, prompt: str, documents: list[str]):
        if documents != []:
            prompt += LONG_TERM_MEMORY_PROMPT
            for i in range(len(documents)):
                prompt += SINGLE_MEMORY_TEMPLATE.format(
                    id=str(i + 1), content=documents[i]
                )
        return prompt

    def _pre_run(self, prompt: str):
        self.called_tools = []
        prompt = self.user_prompt_template.format(prompt=prompt)
        if self.long_term_memory is not None:
            documents = self.long_term_memory.search(prompt)
            prompt = self._build_longterm_memory_rag_prompt(prompt, documents)

        if self.knowledgebase is not None:
            documents = self.knowledgebase.search(prompt)
            prompt = self._build_knowledgebase_rag_prompt(prompt, documents)

        return prompt

    async def _run(self, prompt: str):
        message = types.Content(role="user", parts=[types.Part(text=prompt)])

        async for event in self.runner.run_async(
            user_id=self.short_term_memory.user_id,
            session_id=self.short_term_memory.session_id,
            new_message=message,
        ):
            for part in event.content.parts:
                if part.function_call is not None:
                    self.called_tools.append(part.function_call.name)
            if event.content.parts == []:
                logger.error(
                    f"Agent {self.name} response is empty. Too-long long-term-memory may lead this, considering to create a new conllection in your vector database."
                )
            elif (
                event.is_final_response()
                and event.content.parts[0].text is not None
                and len(event.content.parts[0].text.strip()) > 0
            ):
                logger.debug(
                    f"Agent {self.name} response: {event.content.parts[0].text}"
                )
                return event.content.parts[0].text.strip(), event

        return "", None

    async def _post_run(self, prompt: str, event):
        # cleanup mcp tools
        for tool in self.tools:
            if isinstance(tool, MCPToolset):
                await tool.close()

        # process long term memory
        if self.long_term_memory is not None:
            session = await self.runner.session_service.get_session(
                app_name=self.short_term_memory.app_name,
                user_id=self.short_term_memory.user_id,
                session_id=self.short_term_memory.session_id,
            )
            self.long_term_memory.add_session_to_memory(session)

        # record (input, response) pair in dataset if enable sampling
        if self.sampler is not None and self.enable_sampling:
            self.sampler.add_sample(
                input=prompt,
                output=event.content.parts[0].text.strip(),
            )

    async def run(self, prompt: str) -> str:
        logger.debug(f"Running {self.name} agent with prompt: {prompt}")

        # In pre-run, we do:
        # 1. search long-term memory
        # 2. search knowledgebase
        # 3. build final prompt
        prompt = self._pre_run(prompt)
        logger.debug(f"Final prompt: {prompt}")

        response, final_event = await self._run(prompt)

        # In post-run, we do:
        # 1. cleanup mcp tools
        # 2. add session to long-term memory
        # 3. record (input, response) pair in dataset if enable sampling
        if final_event is not None:
            await self._post_run(prompt, final_event)

        return response
