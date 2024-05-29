# NOTE: This one is the receiver service.
from flask import Flask, request
from opentelemetry import trace, baggage
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, BatchSpanProcessor
from opentelemetry.baggage.propagation import W3CBaggagePropagator
from wsgi import otlp_middleware

app = Flask(__name__)

# calling the middleware
app.wsgi_app = otlp_middleware(app.wsgi_app)


@app.route("/")
def hello():
    environ: dict[str, str] = request.environ
    # print(f"Received environ: {environ}")
    tracer: trace.Tracer = environ["otlp.tracer"]
    ctx: trace.SpanContext = environ["otlp.context"]
    # Reuse the context to create a new span
    with tracer.start_span("hello_span", context=ctx):
        return f"{howdy()} from API 2!"


def howdy() -> str:
    return "Howdy"


if __name__ == "__main__":
    app.run(port=5002)
