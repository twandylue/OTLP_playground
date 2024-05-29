# NOTE: Initialize the tracer
# Description: Middleware for the application
from opentelemetry import trace, baggage
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, BatchSpanProcessor


def init_tracer() -> trace.Tracer:
    """
    Initialize the tracer
    """

    # resource: Resource = Resource(
    #     attributes={
    #         SERVICE_NAME: "otel-collector",
    #     }
    # )

    # NOTE: Initialize the tracer
    traceProvider: TracerProvider = TracerProvider()
    # traceProvider = TracerProvider(resource=resource)
    trace.set_tracer_provider(traceProvider)

    # NOTE: Create multiple exporters and we will use console exporter for debugging
    console_exporter: ConsoleSpanExporter = ConsoleSpanExporter()
    # otlp_exporter = OTLPSpanExporter(endpoint="localhost:4317")

    # NOTE: Create multiple span processors for different exporters with TracerProvider
    console_processor: BatchSpanProcessor = BatchSpanProcessor(console_exporter)
    # otlp_processor = BatchSpanProcessor(otlp_exporter)

    # NOTE: Register the span processors with TracerProvider
    traceProvider.add_span_processor(console_processor)
    # traceProvider.add_span_processor(otlp_processor)

    # reader = PeriodicExportingMetricReader(
    #     OTLPExporter(endpoint="localhost:4317/v1/metrics"),
    # )
    # meterProvider = MeterProvider(resource=resource, metric_reader=[reader])
    # metrics.set_meter_provider(meterProvider)

    # NOTE: Get a Tracer instance
    return trace.get_tracer(__name__)
