from src.tracing.base_tracer import BaseTracer
from src.tracing.apmplus_tracer import APMPlusTracer


class TracerFactory:
    @staticmethod
    def create_tracer(type: str) -> BaseTracer:
        if type.lower() == "apmplus":
            return APMPlusTracer()
        else:
            raise ValueError(f"Unknown tracer type: {type}")
