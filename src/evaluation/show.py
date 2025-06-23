from prometheus_client import CollectorRegistry, Gauge
from src.evaluation.prometheus_utils import post_pushgateway
from src.evaluation.schema import EvaluationMetadata, TestcaseData

registry = CollectorRegistry()


test_cases_total_metric = Gauge(
    "test_cases_total",
    "Total number of test cases in this evaluation",
    registry=registry,
)

test_cases_success_metric = Gauge(
    "test_cases_success", "Success number of test cases", registry=registry
)

test_cases_pass_metric = Gauge(
    "test_cases_pass", "Passed number of test cases", registry=registry
)

test_cases_failure_metric = Gauge(
    "test_cases_failure", "Failuer number of test cases", registry=registry
)

# test_cases_unpass_metric = Gauge(
#     "test_cases_unpass", "Unpassed number of test cases", registry=registry
# )

case_threshold_metric = Gauge("threshold", "Threshold of test cases", registry=registry)
diff_threshold_metric = Gauge(
    "diff_threshold", "Diff threshold of test cases", registry=registry
)

test_cases_data_metric = Gauge(
    "test_cases_data",
    "Specific data of test cases",
    registry=registry,
    labelnames=["data"],
)

eval_data_metric = Gauge(
    "eval_data",
    "Specific data of evaluation",
    registry=registry,
    labelnames=["data"],
)


def show_eval_results(
    test_name: str,
    test_cases_total: int,
    test_cases_failure: int,
    test_cases_pass: int,
    test_data_list: list[TestcaseData],
    eval_data: EvaluationMetadata,
    case_threshold: float = 0.5,
    diff_threshold: float = 0.2,
    url: str = "",
    username: str = "",
    password: str = "",
):
    test_cases_total_metric.set(test_cases_total)
    test_cases_failure_metric.set(test_cases_failure)
    test_cases_pass_metric.set(test_cases_pass)

    for test_data in test_data_list:
        test_cases_data_metric.labels(data=str(test_data.__dict__)).set(1)

    eval_data_metric.labels(data=str(eval_data.__dict__)).set(1)
    case_threshold_metric.set(case_threshold)
    diff_threshold_metric.set(diff_threshold)

    post_pushgateway(
        pushgateway_url=url,
        username=username,
        password=password,
        job_name="agent-evaluation",
        registry=registry,
        grouping_key={"test_name": test_name},
    )
