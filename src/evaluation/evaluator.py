import asyncio
import uuid
from typing import Callable

from deepeval import evaluate
from deepeval.evaluate.types import EvaluationResult
from deepeval.key_handler import KEY_FILE_HANDLER, KeyValues
from deepeval.metrics import BaseMetric
from deepeval.models import LocalModel
from deepeval.test_case import LLMTestCase
from src.config import settings
from src.evaluation.show import show_eval_results
from src.evaluation.schema import TestcaseData, EvaluationMetadata


class Evaluator:
    def __init__(
        self, tested_model: str = "", metrics: list[BaseMetric] = None, upload: bool = False
    ):
        self.tested_model = tested_model
        self.metrics = metrics
        self.judge_model = self._create_judge_model()

        # whether upload to Prometheus -> Grafana
        self.upload = upload

    def _create_judge_model(
        self,
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

    def _build_testcases(
            self, inputs, actual_outputs, expected_outputs, **kwargs
    ) ->list[LLMTestCase]:
        test_cases = []
        for input, actual_output, expected_output in zip(inputs, actual_outputs,expected_outputs):
            test_case = LLMTestCase(
                input=input,
                actual_output=actual_output,
                expected_output=expected_output,
                **kwargs,  # for other params such as called_tools
            )
            test_cases.append(test_case)
        return test_cases

    async def evaluate(
        self, inputs: list[str], expected_outputs: list[str], inference_funcs: Callable | list[Callable]
    ):
        actual_outputs = await self._inference(inputs, inference_funcs)
        test_cases = self._build_testcases(
            inputs=inputs,
            actual_outputs=actual_outputs,
            expected_outputs=expected_outputs,
        )
        results = evaluate(test_cases=test_cases, metrics=self.metrics)

        if self.upload:
            eval_results =self._parse_result(inputs, results)
            show_eval_results(**eval_results)
            return results
        else:
            return results

    def _parse_result(self, inputs: list[str], results: EvaluationResult):
        test_results = results.test_results
        # Specific information
        test_name = str(uuid.uuid4())
        test_cases_total = len(test_results)
        test_cases_failure = 0
        test_cases_pass = 0
        test_data_list = []
        eval_data = EvaluationMetadata(
            tested_model=str(settings.model),
            judge_model=str(settings.judge_model),
        )
        case_threshold = 0.5
        diff_threshold = 0.2

        for i, (input_str, test_result)in enumerate(zip(inputs, test_results)):
            pass_flag = 'PASSED'
            if test_result.success:
                test_cases_pass += 1
            else:
                pass_flag = 'FAILURE'
                test_cases_failure += 1

            test_data_list.append(
                TestcaseData(
                    id=str(i),
                    input=input_str,
                    actual_output=test_result.actual_output,
                    expected_output=test_result.expected_output,
                    # [temporary] score: This method is not generally applicable now and is currently only available in the GEval mode.
                    score=str(test_result.metrics_data[0].score),
                    reason=test_result.metrics_data[0].reason,
                    status=pass_flag,
                )
            )



        return {
            "test_name": test_name,
            "test_cases_total": test_cases_total,
            "test_cases_failure": test_cases_failure,
            "test_cases_pass": test_cases_pass,
            "test_data_list": test_data_list,
            "eval_data": eval_data,
            "case_threshold": case_threshold,
            "diff_threshold": diff_threshold,
        }