from src.utils.logger import get_logger

logger = get_logger(__name__)

# Store registered agents in a dictionary
AGENTS = {}


async def call_agent(agent_name: str, prompt: str):
    """Calls the specified agent with the given prompt.
    Args:
        agent_name (str): The name of the agent to call.
        prompt (str): The prompt to pass to the agent.
    Returns:
        str: The response from the agent.
    """
    logger.debug(f"Calling sub agent {agent_name} with prompt: {prompt}")

    agent = AGENTS.get(agent_name)
    res = await agent.run(prompt)
    return res
