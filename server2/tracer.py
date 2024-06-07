from opentelemetry import trace, baggage
from opentelemetry.sdk.trace import TracerProvider, SpanProcessor
from opentelemetry.sdk.resources import Resource, SERVICE_NAME


def init_TracerProvider(processor: SpanProcessor = None):
    """
    Initialize TracerProvider
    """

    resource: Resource = Resource(
        attributes={
            SERVICE_NAME: "andylu-http-example",
        }
    )

    # NOTE: Initialize the TracerProvider
    tracer_provider: TracerProvider = TracerProvider(resource=resource)
    trace.set_tracer_provider(tracer_provider)

    # NOTE: Register the span processors with TracerProvider
    tracer_provider.add_span_processor(processor)
