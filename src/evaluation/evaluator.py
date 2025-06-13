import asyncio
from typing import Callable

from deepeval import evaluate
from deepeval.key_handler import KEY_FILE_HANDLER, KeyValues
from deepeval.models import LocalModel
from deepeval.test_case import LLMTestCase
from src.config import settings


class Evaluator:
    def __init__(
        self, tested_model: str = "", metrics: str = None, upload: bool = False
    ):
        self.tested_model = tested_model
        self.metrics = metrics
        self.judge_model = self._create_judge_model()

        # whether upload to Prometheus -> Grafana
        self.upload = upload

    def _create_judge_model(
        model_name: str = settings.judge_model,
        api_key: str = settings.judge_model_api_key,
        api_base: str = settings.judge_model_api_base_url,
    ):
        assert api_key != "", "JUDGE_MODEL_API_KEY cannot be an null string."

        KEY_FILE_HANDLER.write_key(KeyValues.LOCAL_MODEL_NAME, model_name)
        KEY_FILE_HANDLER.write_key(KeyValues.LOCAL_MODEL_BASE_URL, api_base)
        KEY_FILE_HANDLER.write_key(KeyValues.LOCAL_MODEL_API_KEY, api_key)
        KEY_FILE_HANDLER.write_key(KeyValues.USE_LOCAL_MODEL, "YES")
        KEY_FILE_HANDLER.write_key(KeyValues.USE_AZURE_OPENAI, "NO")
        return LocalModel()

    async def _inference(self, inputs, inference_funcs):
        tasks = []
        for idx, input in enumerate(inputs):
            if isinstance(inference_funcs, list):
                task = asyncio.create_task(inference_funcs[idx](input))
                tasks.append(task)
            elif isinstance(inference_funcs, Callable):
                task = asyncio.create_task(inference_funcs(input))
                tasks.append(task)
            else:
                raise TypeError(
                    "inference_funcs must be a list of Callable or a Callable."
                )
        actual_outputs = await asyncio.gather(*tasks)
        return actual_outputs

    def _build_testcases(self, inputs, actual_outputs, expected_outputs, **kwargs):
        test_cases = []
        for input, actual_output in zip(inputs, actual_outputs):
            test_case = LLMTestCase(
                input=input,
                actual_output=actual_output,
                **kwargs,  # for other params such as called_tools
            )
            test_cases.append(test_case)
        return test_cases

    def evaluate(
        self, inputs: list[str], expected_outputs: list[str], inference_funcs: Callable
    ):
        actual_outputs = asyncio.run(self._inference(inputs, inference_funcs))
        test_cases = self._build_testcases(
            inputs=inputs,
            actual_outputs=actual_outputs,
            expected_outputs=expected_outputs,
        )
        results = evaluate(test_cases=test_cases, metrics=self.metrics)

        if self.upload:
            return self._parse_result(results)
        else:
            return results

    def _parse_result(self, results):
        test_cases_total = 0
        test_cases_failure = 0
        test_cases_pass = 0
        test_data_list = []
        eval_data = []
        case_threshold = 0.5
        diff_threshold = 0.2
        return {
            "test_cases_total": test_cases_total,
            "test_cases_failure": test_cases_failure,
            "test_cases_pass": test_cases_pass,
            "test_data_list": test_data_list,
            "eval_data": eval_data,
            "case_threshold": case_threshold,
            "diff_threshold": diff_threshold,
        }
