from src.agent import Agent
from src.memory.long_term_memory import LongTermMemory
from src.memory.short_term_memory import ShortTermMemory
from src.utils.logger import filter_log
from sre_example.sub_agent_configs import agent_configs

filter_log()  # remove the verbose logs


def get_timestamp():
    import time

    return time.strftime("%Y%md%H%M%S", time.localtime())


def init_agents(
    configs: list = [],
    short_term_memory: ShortTermMemory = None,
    enable_sampling: bool = False,
):
    agents = []
    for config in configs:
        agent = Agent(
            **config,
            short_term_memory=short_term_memory,
            enable_sampling=enable_sampling,
        )
        agents.append(agent)
    return agents


async def run_workflow(agents: list, prompt: str):
    input = prompt
    for agent in agents:
        res = await agent.run(input)
        input = res


async def run(prompt: str, enable_sampling: bool = False):
    # Init memories
    short_term_memory_name = "test_short_term_memory" + get_timestamp()
    short_term_memory = await ShortTermMemory.create(name=short_term_memory_name)

    long_term_memory_name = "test_long_term_memory" + get_timestamp()
    long_term_memory = LongTermMemory(name=long_term_memory_name)
    agent_configs[2]["long_term_memory"] = (
        long_term_memory  # enable long-term-memory in command executor
    )

    # Build sub agents
    sub_agents = init_agents(agent_configs, short_term_memory, enable_sampling)

    # Run SRE workflow
    await run_workflow(sub_agents, prompt)


def main(
    prompt: str,
    enable_sampling: bool = False,
):
    import asyncio

    asyncio.run(run(prompt=prompt, enable_sampling=enable_sampling))
