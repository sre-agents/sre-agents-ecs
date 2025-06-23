from src.config import settings
from src.tracing.base_tracer import BaseTracer
from src.utils.logger import get_logger

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

logger = get_logger(__name__)


class APMPlusTracer(BaseTracer):
    def __init__(
        self,
        endpoint: str = settings.apmplus_endpoint,
        app_key: str = settings.apmplus_appkey,
        service_name: str = "veagent_tracing",
        tracer_name: str = "veagent_tracer",
    ):
        super().__init__(endpoint, app_key)

        self.service_name = service_name
        self.tracer_name = tracer_name
        self.tracer = self._create_tracer()

    def _create_tracer(self):
        endpoint = self.endpoint
        headers = {
            "x-byteapm-appkey": self.app_key,
        }
        resource_attributes = {
            "service.name": self.service_name,
        }
        resource = Resource.create(resource_attributes)

        exporter = OTLPSpanExporter(endpoint=endpoint, insecure=True, headers=headers)
        provider = TracerProvider(resource=resource)
        processor = BatchSpanProcessor(exporter)
        provider.add_span_processor(processor)

        trace.set_tracer_provider(provider)

        tracer = trace.get_tracer(self.tracer_name)
        return tracer

    def upload_data(self, agent_name: str, event: str, data: dict):
        span_name = f"{agent_name}_{event}"
        span = self.tracer.start_span(span_name)
        span.add_event(event, data)
        span.end()
        logger.info(
            f"Upload data to apmplus, span:{span_name}, event: {event}, data: {data}"
        )
