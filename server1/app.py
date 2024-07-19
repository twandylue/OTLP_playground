# NOTE This one is the sender service
from flask import Flask
import requests
from opentelemetry import trace, propagators, baggage
from opentelemetry.context.context import Context
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


@app.route("/test_1")
def test_tracecontext():
    """
    With only TraceContextTextMapPropagator
    """
    with tracer.start_as_current_span("test_1") as span:
        headers = {}
        TraceContextTextMapPropagator().inject(headers)
        print(f"headers: {headers}")

        response = requests.get("http://localhost:5002/", headers=headers)
        return f"test_1: {response.text}"


@app.route("/test_3")
def test_no_tracecontext():
    """
    Without propagators
    """
    with tracer.start_as_current_span("test_3") as span:
        headers = {}
        print(f"headers: {headers}")

        response = requests.get("http://localhost:5002/", headers=headers)
        return f"test_3: {response.text}"


@app.route("/test_2")
def test_both():
    """
    With W3CBaggagePropagator and TraceContextTextMapPropagator
    """
    with tracer.start_as_current_span("test_2") as span:
        # NOTE: Add multiple baggage items
        ctx: Context = baggage.set_baggage("hello", "world")
        ctx: Context = baggage.set_baggage("howdy2", "world", context=ctx)

        headers = {}
        W3CBaggagePropagator().inject(headers, ctx)
        # NOTE:
        # traceparent_string = f"00-{format_trace_id(span_context.trace_id)}-{format_span_id(span_context.span_id)}-{span_context.trace_flags:02x}"
        # ref: https://github.com/open-telemetry/opentelemetry-python/blob/ba22b165471bde2037620f2c850ab648a849fbc0/opentelemetry-api/src/opentelemetry/trace/propagation/tracecontext.py#L103C1-L104C1
        TraceContextTextMapPropagator().inject(headers, ctx)
        print(headers)

        response = requests.get("http://localhost:5002/", headers=headers)
        return f"test_2: {response.text}"


# WARNING: This is invalid operation to just have baggage in headers
# @app.route("/test_3")
# def test_w3c():
#     """
#     With only W3CBaggagePropagator
#     """
#     with tracer.start_as_current_span("test_3") as span:
#         # NOTE: Add multiple baggage items
#         ctx: Context = baggage.set_baggage("hello", "world")
#         ctx: Context = baggage.set_baggage("howdy2", "world", context=ctx)
#
#         headers = {}
#         W3CBaggagePropagator().inject(headers, ctx)
#         print(headers)
#
#         response = requests.get("http://localhost:5002/", headers=headers)
#         return f"test_3: {response.text}"


if __name__ == "__main__":
    app.run(port=5001)
