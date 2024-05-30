# NOTE This one is the sender service
from flask import Flask
import requests
from opentelemetry import trace, propagators, baggage
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
from opentelemetry.baggage.propagation import W3CBaggagePropagator
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, BatchSpanProcessor

app = Flask(__name__)

# Initialize the tracer
trace.set_tracer_provider(TracerProvider())
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(ConsoleSpanExporter())
)

tracer = trace.get_tracer(__name__)


@app.route("/")
def hello():
    with tracer.start_as_current_span("hello") as span:
        ctx = baggage.set_baggage("hello", "world")
        # NOTE: Add multiple baggage items
        ctx = baggage.set_baggage("howdy2", "world", context=ctx)

        headers = {}
        W3CBaggagePropagator().inject(headers, ctx)
        TraceContextTextMapPropagator().inject(headers, ctx)
        print(headers)

        response = requests.get("http://localhost:5002/", headers=headers)
        return f"Hell from API 1! Response from API 2: {response.text}"


if __name__ == "__main__":
    app.run(port=5001)
