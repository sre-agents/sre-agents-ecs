import json

from src.utils.logger import filter_log
from sre_example.prompts.sre_agent_prompts import RISK_CHECKER_SYSTEM_PROMPT
from tests.data.test_risk_checker import test_data, validate_data
from tests.utils.common_utils import create_agent, run_agent

filter_log()


def test_command_risk_checker():
    risk_checker = create_agent(
        name="SRE_command_risk_checker",
        description="Check command risk level",
        system_prompt=RISK_CHECKER_SYSTEM_PROMPT
        + "\n Please make sure the command sequence keeps the same with the input.",
    )

    acutal_result, _ = run_agent(risk_checker, str(test_data))
    acutal_result = json.loads(acutal_result)

    for i in range(len(acutal_result)):
        if validate_data[i]["risk_level"] in ["high", "medium"]:
            assert acutal_result[i]["risk_level"] in ["high", "medium"]
        elif validate_data[i]["risk_level"] == "low":
            assert acutal_result[i]["risk_level"] == "low"
        else:
            raise ValueError("Invalid risk level in validate data.")
