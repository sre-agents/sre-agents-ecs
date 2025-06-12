from dataclasses import dataclass


@dataclass
class TestcaseData:
    id: str
    input: str
    actual_output: str
    expected_output: str
    score: str
    reason: str


@dataclass
class EvaluationMetadata:
    tested_model: str
    judge_model: str
