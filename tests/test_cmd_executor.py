import json

import pytest
from deepeval import assert_test
from deepeval.dataset import EvaluationDataset
from deepeval.metrics import ToolCorrectnessMetric
from deepeval.test_case import LLMTestCase, ToolCall

from src.tools.ask_for_approve import ask_for_approve
from sre_example.prompts.sre_agent_prompts import CMD_EXECUTOR_SYSTEM_PROMPT
from tests.data.test_cmd_executor import data
from tests.utils.common_utils import create_agent, run_batch_agent


def mock_ecs_server_tool(instance: str, region: str, command_content: str):
    """
    Execute commands on the specified ECS instance and return the execution results.

    Parameters:
        instance (str): The identifier of the ECS instance on which to execute the command.
        region (str): The region where the ECS instance is located.
        command_content (str): The content of the command to be executed on the ECS instance.

    Returns:
        dict: A dictionary containing the executed command and the execution result, with the following structure:
              {
                  "command": str,  # The content of the executed command
                  "result": str    # The result information of the command execution
              }
    """
    return {"command": command_content, "result": f"{command_content} execute success."}


def build_deepeval_dataset(
    inputs: list[str],
    actual_outputs: list[str],
    tools_called_list: list[list[ToolCall]],
    expected_tools_list: list[list[ToolCall]],
):
    test_cases = []
    for input_str, actual_output, tools_called, expected_tools in zip(
        inputs, actual_outputs, tools_called_list, expected_tools_list
    ):
        test_case = LLMTestCase(
            input=input_str,
            actual_output=actual_output,
            tools_called=tools_called,
            expected_tools=expected_tools,
        )
        test_cases.append(test_case)

    return EvaluationDataset(test_cases=test_cases)


def build_dataset():
    cmd_executor = create_agent(
        name="SRE_command_executor",
        description="Command executor",
        system_prompt=CMD_EXECUTOR_SYSTEM_PROMPT,
        tools=[ask_for_approve, mock_ecs_server_tool],
    )

    prompts = []
    for data_uint in data:
        prompt_str = json.dumps(data_uint["prompt"])
        prompts.append(prompt_str)

    actual_outputs, tools_called_list = run_batch_agent(cmd_executor, prompts)

    expected_tools_list = []
    for data_uint in data:
        expected_tools_list.append(data_uint["expected_tools"])

    return build_deepeval_dataset(
        inputs=prompts,
        actual_outputs=actual_outputs,
        tools_called_list=tools_called_list,
        expected_tools_list=expected_tools_list,
    )


dataset = build_dataset()


def build_metrics():
    metrics = [
        ToolCorrectnessMetric(threshold=1.0),
    ]
    return metrics


@pytest.mark.parametrize(
    "test_case",
    dataset,
)
def test_cmd_executor(test_case: LLMTestCase):
    metrics = build_metrics()
    assert_test(test_case, metrics)
