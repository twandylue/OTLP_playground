from opentelemetry import trace, baggage
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
from opentelemetry.baggage.propagation import W3CBaggagePropagator
from tracer import init_tracer
from werkzeug.wrappers import Request, Response, ResponseStream


class OtlpMiddleware:
    """
    Middleware for the application to handle the incoming request with OTLP headers
    """

    def __init__(self, app):
        # TODO: Set to True for debugging. We can use environment variables to set this flag?
        self.tracer: trace.Tracer = init_tracer(debug=True)
        self.app: callable[..., ResponseStream] = app

    def __call__(self, environ: dict[str, str], start_response: callable):
        request: Request = Request(environ)
        headers: dict[str, str] = request.headers
        # print(f"Received headers: {headers}")

        carrier: dict[str, str] = {"traceparent": headers["Traceparent"]}
        ctx: trace.SpanContext = TraceContextTextMapPropagator().extract(
            carrier=carrier
        )
        # print(f"Received context: {ctx}")

        b2: dict[str, str] = {"baggage": headers["Baggage"]}
        ctx2: trace.SpanContext = W3CBaggagePropagator().extract(b2)
        # print(f"Received context2: {ctx2}")

        # # Start a new span
        # with tracer.start_span("api2_span", context=ctx2):
        #     print(baggage.get_baggage("hello", ctx2))
        #     return "Hello from API 2!"

        # Reuse the context to create a new span
        with self.tracer.start_span("api2_middleware_span", context=ctx2):
            # NOTE: Set the tracer in the environment for context propagation
            environ["otlp.tracer"] = self.tracer
            environ["otlp.context"] = ctx2

            return self.app(environ, start_response)


"""
Unit tests of wsgi.py
"""
import pytest
import json
from flask import Flask, request


@pytest.fixture
def app():
    app: Flask = Flask(__name__)
    app.wsgi_app = OtlpMiddleware(app.wsgi_app)

    @app.route("/echo")
    def echo() -> str:
        environ: dict[str, str] = request.environ
        tracer: trace.Tracer = environ["otlp.tracer"]
        with tracer.start_span("echo_span") as span:
            trace_id: str = span.get_span_context().trace_id
            ctx: trace.SpanContext = environ["otlp.context"]
            bag: str = baggage.get_baggage("test_key", ctx)
            return json.dumps({"trace_id": trace_id, "baggage": bag})

    return app


# def test_app_case_1(app):
#     tracer: trace.Tracer = init_tracer()
#     with app.test_client() as client:
#         with tracer.start_as_current_span("test_span") as span:
#             ctx = baggage.set_baggage("test_key", "test_value")
#             headers = {}
#             W3CBaggagePropagator().inject(headers, ctx)
#             TraceContextTextMapPropagator().inject(headers, ctx)
#
#             response: Response = client.get("/echo", headers=headers)
#             assert response.status_code == 200
#             data: dict[str, str] = json.loads(response.data)
#             assert "trace_id" in data
#             assert data["trace_id"] == span.get_span_context().trace_id
#             assert "baggage" in data
#             assert data["baggage"] == "test_value"
