# NOTE: This one is the receiver service.
from flask import Flask, request
from opentelemetry import trace, baggage
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    ConsoleSpanExporter,
    BatchSpanProcessor,
)
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.baggage.propagation import W3CBaggagePropagator
from middleware import OtlpMiddleware
import logging
from logging.handlers import RotatingFileHandler


def setup_logging():
    """
    Setup logging configuration
    """

    # Note: Create a file handler
    file_handler: RotatingFileHandler = RotatingFileHandler(
        "app.log", maxBytes=10000, backupCount=3
    )
    file_handler.setLevel(logging.WARNING)

    # Note: Create a logging format
    formatter: logging.Formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(formatter)

    # NOTE: Add the handlers to the logger
    logger: logging.Logger = logging.getLogger()
    logger.setLevel(logging.WARNING)
    logger.addHandler(file_handler)
    app.logger.addHandler(file_handler)


app = Flask(__name__)
# seup_logging()
processor: BatchSpanProcessor = BatchSpanProcessor(ConsoleSpanExporter())
app.wsgi_app = OtlpMiddleware(app.wsgi_app, processor=processor)


@app.route("/")
def hello():
    environ: dict[str, str] = request.environ
    tracer: trace.Tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span("route_span") as span:
        if "otlp.context" in environ:
            ctx = environ["otlp.context"]
            print(f"Received bag in hello: {baggage.get_baggage('hello', ctx)}")

        return f"{howdy()} from API 2!"


def howdy() -> str:
    tracer: trace.Tracer = trace.get_tracer(__name__)

    with tracer.start_as_current_span("howdy_span") as span:
        span.set_attribute("howdy", "in howdy function")
        with tracer.start_as_current_span("another_func_span"):
            another_func()
        return "Howdy"


def another_func() -> None:
    print("Another function")


if __name__ == "__main__":
    app.run(port=5002)
