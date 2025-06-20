import asyncio
from concurrent.futures import ThreadPoolExecutor
from deepeval.test_case import ToolCall

from src.agent import Agent


def create_agent(
    name: str,
    description: str,
    system_prompt: str,
    mcp_servers: list = [],
    tools: list = [],
):
    agent = Agent(
        name=name,
        description=description,
        system_prompt=system_prompt,
        mcp_servers=mcp_servers,
        tools=tools,
    )
    return agent


def run_agent(agent, prompt):
    res = asyncio.run(agent.run(prompt))
    tools = [ToolCall(name=tool) for tool in agent.called_tools]
    return res, tools


def run_batch_agent(agent, prompts, max_workers=8):
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(run_agent, agent, prompt) for prompt in prompts]
        results = [future.result() for future in futures]
        res_list, tools_list = zip(*results)
        return res_list, tools_list
