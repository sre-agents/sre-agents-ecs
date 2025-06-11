import pytest
from deepeval import assert_test
from deepeval.dataset import EvaluationDataset
from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCase, LLMTestCaseParams

from sre_example.prompts.sre_agent_prompts import CMD_GENERATOR_SYSTEM_PROMPT
from tests.data.test_cmd_generator import data
from tests.prompts.deepeval_prompts import EVAL_MODEL_PROMPT
from tests.utils.common_utils import create_agent, run_batch_agent
from tests.utils.deepeval_utils import create_eval_model


def build_deepeval_dataset(
    inputs: list[str], actual_outputs: list[str], expected_outputs: list[str]
):
    test_cases = []
    for input, actual_output, expected_output in zip(
        inputs, actual_outputs, expected_outputs
    ):
        test_case = LLMTestCase(
            input=input,
            actual_output=actual_output,
            expected_output=expected_output,
        )
        test_cases.append(test_case)

    return EvaluationDataset(test_cases=test_cases)


def build_dataset():
    cmd_generator = create_agent(
        name="SRE_command_generator",
        description="Generate commands to execute",
        system_prompt=CMD_GENERATOR_SYSTEM_PROMPT,
    )

    prompts = []
    for data_uint in data:
        prompts.append(data_uint["prompt"])

    actual_outputs, _ = run_batch_agent(cmd_generator, prompts)

    expected_outputs = []
    for data_uint in data:
        expected_outputs.append(str(data_uint["expected_output"]))

    return build_deepeval_dataset(
        inputs=prompts, actual_outputs=actual_outputs, expected_outputs=expected_outputs
    )


dataset = build_dataset()


@pytest.mark.parametrize(
    "test_case",
    dataset,
)
def test_cmd_generator(test_case: LLMTestCase):
    eval_model = create_eval_model()
    correctness_metric = GEval(
        name="Correctness",
        criteria=EVAL_MODEL_PROMPT,
        evaluation_params=[
            LLMTestCaseParams.ACTUAL_OUTPUT,
            LLMTestCaseParams.EXPECTED_OUTPUT,
        ],
        threshold=0.5,
        model=eval_model,
    )
    assert_test(test_case, [correctness_metric])
