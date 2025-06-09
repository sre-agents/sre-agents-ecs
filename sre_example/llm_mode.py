from src.agent import Agent
from src.memory.long_term_memory import LongTermMemory
from src.memory.short_term_memory import ShortTermMemory
from src.utils.logger import filter_log
from sre_example.prompts.sre_orchestrator_prompt import ORCHESTRATOR_SYSTEM_PROMPT
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

    # Run SRE by LLM
    orchestrator = Agent(
        name="sre_orchestrator",
        description="Orchestrator",
        system_prompt=ORCHESTRATOR_SYSTEM_PROMPT,
        sub_agents=sub_agents,
        short_term_memory=short_term_memory,
    )

    res = await orchestrator.run(prompt=prompt)
    print(f"====== Final response ======\n{res}")


def main(
    prompt: str,
    enable_sampling: bool = False,
):
    import asyncio

    asyncio.run(run(prompt=prompt, enable_sampling=enable_sampling))
