from deepeval import assert_test
from deepeval.dataset import EvaluationDataset
from deepeval.key_handler import KEY_FILE_HANDLER, KeyValues
from deepeval.metrics import GEval
from deepeval.models import LocalModel
from deepeval.test_case import LLMTestCase, LLMTestCaseParams

from src.config import API_BASE_URL, API_KEY, LLM
from tests.prompts.deepeval_prompts import EVAL_MODEL_PROMPT


def create_eval_model(
    model_name: str = LLM, api_key: str = API_KEY, api_base: str = API_BASE_URL
):
    KEY_FILE_HANDLER.write_key(KeyValues.LOCAL_MODEL_NAME, model_name)
    KEY_FILE_HANDLER.write_key(KeyValues.LOCAL_MODEL_BASE_URL, api_base)
    if api_key:
        KEY_FILE_HANDLER.write_key(KeyValues.LOCAL_MODEL_API_KEY, api_key)
    if format:
        KEY_FILE_HANDLER.write_key(KeyValues.LOCAL_MODEL_FORMAT, "json")
    KEY_FILE_HANDLER.write_key(KeyValues.USE_LOCAL_MODEL, "YES")
    KEY_FILE_HANDLER.write_key(KeyValues.USE_AZURE_OPENAI, "NO")

    return LocalModel()


def deepeval_assert(test_case: LLMTestCase):
    eval_model = create_eval_model(
        model_name=LLM,
        api_key=API_KEY,
        api_base=API_BASE_URL,
    )
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


def build_deepeval_dataset(
    inputs: list[str], acutal_outputs: list[str], expected_outputs: list[str]
):
    test_cases = []
    for input, acutal_output, expected_output in zip(
        inputs, acutal_outputs, expected_outputs
    ):
        test_case = LLMTestCase(
            input=input,
            actual_output=acutal_output,
            expected_output=expected_output,
        )
        test_cases.append(test_case)

    return EvaluationDataset(test_cases=test_cases)
