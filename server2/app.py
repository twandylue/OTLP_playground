# NOTE: This one is the receiver service.
from flask import Flask, request
from opentelemetry import trace, baggage
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, BatchSpanProcessor
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
setup_logging()

# calling the middleware
app.wsgi_app = OtlpMiddleware(app.wsgi_app)


@app.route("/")
def hello():
    environ: dict[str, str] = request.environ
    # print(f"Received environ: {environ}")
    tracer: trace.Tracer = environ.get("otlp.tracer", None)
    if tracer is None:
        return "No tracer found in the environment"

    # Reuse the context to create a new span
    with tracer.start_as_current_span("hello_span") as span:
        # get the baggage from context
        if "otlp.context" in environ:
            ctx = environ["otlp.context"]
            print(f"Received bag in hello: {baggage.get_baggage('hello', ctx)}")

        return f"{howdy()} from API 2!"


def howdy() -> str:
    return "Howdy"


if __name__ == "__main__":
    app.run(port=5002)
