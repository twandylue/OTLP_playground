from opentelemetry import trace, baggage
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource, SERVICE_NAME


def init_TracerProvider():
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

    console_exporter: ConsoleSpanExporter = ConsoleSpanExporter()
    # otlp_exporter = OTLPSpanExporter(endpoint="localhost:4317")

    # Get the environment variable to indicate the application mode
    import os

    env = os.getenv("ENV", "Dev")
    if env == "DEV":
        # NOTE: Create multiple span processors for different exporters with TracerProvider
        print("Running in Dev mode")
        console_processor: BatchSpanProcessor = BatchSpanProcessor(console_exporter)
        # otlp_processor: BatchSpanProcessor = BatchSpanProcessor(otlp_exporter)

        # NOTE: Register the span processors with TracerProvider
        tracer_provider.add_span_processor(console_processor)
        # tracer_provider.add_span_processor(otlp_processor)
