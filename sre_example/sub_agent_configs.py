from pydantic import BaseModel, Field
from sre_example.config import settings
from sre_example.prompts.sre_agent_prompts import (
    CMD_EXECUTOR_SYSTEM_PROMPT,
    CMD_EXECUTOR_USER_PROMPT_TEMPLATE,
    CMD_GENERATOR_SYSTEM_PROMPT,
    CMD_GENERATOR_USER_PROMPT_TEMPLATE,
    RISK_CHECKER_SYSTEM_PROMPT,
    RISK_CHECKER_USER_PROMPT_TEMPLATE,
    TASK_EVALUATOR_SYSTEM_PROMPT,
)
from veadk.knowledgebase import KnowledgeBase
from veadk.tools import ask_for_approve
from veadk.utils.misc import read_file

agent_configs = []


#
# Command generator config
#
class CommandGeneratorOutputSchema(BaseModel):
    command: str = Field(..., description="The command to execute")
    reason: str = Field(..., description="The reason for the command")


config = {
    "name": "SRE_command_generator",
    "description": "Generate a command",
    "system_prompt": CMD_GENERATOR_SYSTEM_PROMPT,
    "user_prompt_template": CMD_GENERATOR_USER_PROMPT_TEMPLATE,
    "output_schema": CommandGeneratorOutputSchema,
}
agent_configs.append(config)


#
# Command risk checker config
#
class CommandRiskCheckerInputSchema(BaseModel):
    command: str = Field(..., description="The command to execute")
    reason: str = Field(..., description="The reason for the command")


class CommandRiskCheckerOutputSchema(BaseModel):
    command: str = Field(..., description="The command to execute")
    risk_level: str = Field(..., description="The risk level of the command")
    reason: str = Field(..., description="The reason for the risk level")


risky_commands = read_file("assets/risky_commands.txt")
config = {
    "name": "SRE_command_risk_checker",
    "description": "Check command risk level",
    "system_prompt": RISK_CHECKER_SYSTEM_PROMPT,
    "user_prompt_template": RISK_CHECKER_USER_PROMPT_TEMPLATE,
    "knowledgebase": KnowledgeBase(
        config={"collection_name": "risk_checker"},
        data=risky_commands,
        backend=settings.knowledgebase.backend,
    ),
    "input_schema": CommandRiskCheckerInputSchema,
    "output_schema": CommandRiskCheckerOutputSchema,
}
agent_configs.append(config)


#
# Command executor config
#
class CommandExecutorInputSchema(BaseModel):
    command: str = Field(..., description="The command to execute")
    risk_level: str = Field(..., description="The risk level of the command")
    reason: str = Field(..., description="The reason for the risk level")


class CommandExecutorOutputSchema(BaseModel):
    command: str = Field(..., description="The command to execute")
    result: str = Field(..., description="The execute result of the command")


config = {
    "name": "SRE_command_executor",
    "description": "Command executor",
    "system_prompt": CMD_EXECUTOR_SYSTEM_PROMPT,
    "user_prompt_template": CMD_EXECUTOR_USER_PROMPT_TEMPLATE,
    "mcp_servers": [settings.mcp_server.ecs_mcp_server],
    "tools": [ask_for_approve],
    # "long_term_memory": long_term_memory,
    "input_schema": CommandExecutorInputSchema,
    "output_schema": CommandExecutorOutputSchema,
}
agent_configs.append(config)


#
# Task evaluator config
#
config = {
    "name": "SRE_task_evaluator",
    "description": "Evaluate the SRE task finish status.",
    "system_prompt": TASK_EVALUATOR_SYSTEM_PROMPT,
}
agent_configs.append(config)
