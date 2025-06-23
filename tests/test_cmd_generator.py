import asyncio
from typing import Callable

import nest_asyncio
from deepeval.metrics import BaseMetric, GEval
from deepeval.test_case import LLMTestCaseParams
from src.evaluation.evaluator import Evaluator
from src.memory.short_term_memory import ShortTermMemory
from sre_example.prompts.sre_agent_prompts import CMD_GENERATOR_SYSTEM_PROMPT
from tests.data.test_cmd_generator import data
from tests.prompts.deepeval_prompts import EVAL_MODEL_PROMPT
from tests.utils.common_utils import create_agent
from tests.utils.deepeval_utils import create_eval_model

nest_asyncio.apply()


async def build_callable_agent() -> Callable:
    short_term_memory = await ShortTermMemory.create()
    cmd_generator = create_agent(
        name="SRE_command_generator",
        description="Generate commands to execute",
        system_prompt=CMD_GENERATOR_SYSTEM_PROMPT,
        short_term_memory=short_term_memory,
    )
    return cmd_generator.run


def build_metrics() -> list[BaseMetric]:
    metrics = [
        GEval(
            name="Correctness",
            criteria=EVAL_MODEL_PROMPT,
            evaluation_params=[
                LLMTestCaseParams.ACTUAL_OUTPUT,
                LLMTestCaseParams.EXPECTED_OUTPUT,
            ],
            threshold=0.5,
            model=create_eval_model(),
        ),
    ]
    return metrics


async def main():
    # prepare data
    inputs = [data_uint["prompt"] for data_uint in data]
    expected_output = [str(data_uint["expected_output"]) for data_uint in data]

    # agent.run
    inference_funcs = [await build_callable_agent() for _ in range(len(inputs))]

    # evaluator
    cmd_exe_evaluator = Evaluator(metrics=build_metrics(), upload=False)

    await cmd_exe_evaluator.evaluate(
        inputs=inputs,  # prompts
        expected_outputs=expected_output,
        inference_funcs=inference_funcs,
    )


if __name__ == "__main__":
    asyncio.run(main())
