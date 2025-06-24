import nest_asyncio
from sre_example.config import settings
from sre_example.sub_agent_configs import agent_configs
from veadk import Agent
from veadk.memory import LongTermMemory, ShortTermMemory
from veadk.tracing import TracerFactory
from veadk.utils.logger import filter_log

nest_asyncio.apply()
filter_log()  # remove the verbose logs


def get_timestamp():
    import time

    return time.strftime("%Y%md%H%M%S", time.localtime())


def init_agents(
    configs: list = [],
    short_term_memory: ShortTermMemory = None,
):
    agents = []
    for config in configs:
        agent = Agent(
            **config,
            api_key=settings.model.api_key,
            short_term_memory=short_term_memory,
            tracers=[
                TracerFactory.create_tracer(
                    type="APMPlus",
                    config={
                        "endpoint": settings.tracing.apmplus.endpoint,
                        "app_key": settings.tracing.apmplus.app_key,
                    },
                )
            ],
        )
        agents.append(agent)
    return agents


async def run_workflow(agents: list, prompt: str) -> list[str]:
    results = []
    input = prompt
    for agent in agents:
        res = await agent.run(input)
        input = res
        results.append(f"Agent {agent.name} response: {res}")
    return results


async def run(prompt: str, enable_sampling: bool = False) -> list[str]:
    # Init memories
    short_term_memory_name = "test_short_term_memory" + get_timestamp()
    short_term_memory = await ShortTermMemory.create(name=short_term_memory_name)

    long_term_memory_name = "test_long_term_memory" + get_timestamp()
    long_term_memory = LongTermMemory(
        config={"collection_name": long_term_memory_name},
        backend=settings.longterm_memory.backend,
    )
    agent_configs[2]["long_term_memory"] = (
        long_term_memory  # enable long-term-memory in command executor
    )

    # Build sub agents
    sub_agents = init_agents(agent_configs, short_term_memory)

    # Run SRE workflow
    return await run_workflow(sub_agents, prompt)


def main(
    prompt: str,
    enable_sampling: bool = False,
) -> list[str]:
    import asyncio

    return asyncio.run(run(prompt=prompt, enable_sampling=enable_sampling))
