from prometheus_client import CollectorRegistry, push_to_gateway
from prometheus_client.exposition import basic_auth_handler


def post_pushgateway(
    pushgateway_url: str,
    username: str,
    password: str,
    job_name: str,
    registry: CollectorRegistry,
    grouping_key: dict[str, str] = None,
):
    def auth_handler(url, method, timeout, headers, data):
        return basic_auth_handler(
            url, method, timeout, headers, data, username, password
        )

    push_to_gateway(
        gateway=pushgateway_url,
        job=job_name,
        registry=registry,
        grouping_key=grouping_key,
        handler=auth_handler,
    )
