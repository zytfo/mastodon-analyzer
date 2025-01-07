"""Utility functions."""

from html.parser import HTMLParser

# thirdparty
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import \
    OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from prometheus_client import CollectorRegistry, multiprocess
from prometheus_client.openmetrics.exposition import (CONTENT_TYPE_LATEST,
                                                      generate_latest)
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp


class HTMLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.fed = []

    def handle_data(self, data):
        self.fed.append(data)

    def get_data(self):
        return ''.join(self.fed)


def strip_html(html):
    stripper = HTMLStripper()
    stripper.feed(html)
    return stripper.get_data()

def metrics(request: Request) -> Response:
    """Generate metrics for Prometheus."""
    registry = CollectorRegistry()
    multiprocess.MultiProcessCollector(registry)
    data = generate_latest(registry)
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)


def setup_otlp(app: ASGIApp, app_name: str, endpoint: str, log_correlation: bool = True) -> None:
    """Setting up OpenTelemetry."""
    # Setting OpenTelemetry
    # set the service name to show in traces
    resource = Resource.create(attributes={"service.name": app_name, "compose_service": app_name})

    # set the tracer provider
    tracer = TracerProvider(resource=resource)
    trace.set_tracer_provider(tracer)

    tracer.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint=endpoint)))

    if log_correlation:
        LoggingInstrumentor().instrument(set_logging_format=True)

    FastAPIInstrumentor.instrument_app(app, tracer_provider=tracer)
