from tracer import init_TracerProvider
from werkzeug.wrappers import Request, Response, ResponseStream
from opentelemetry import trace, baggage
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
from opentelemetry.baggage.propagation import W3CBaggagePropagator
from opentelemetry.context.context import Context
from opentelemetry.sdk.trace import SpanProcessor


class OtlpMiddleware:
    """
    Middleware for the application to handle the incoming request with OTLP headers
    """

    def __init__(self, app, processor: SpanProcessor = None):
        self.app = app
        # Initialize TracerProvider
        init_TracerProvider(processor)

    def __call__(
        self, environ: dict[str, str], start_response: callable
    ) -> ResponseStream:
        # request url
        print(f"Request URL: {environ['PATH_INFO']}")
        # request method
        print(f"Request Method: {environ['REQUEST_METHOD']}")
        tracer: trace.Tracer = trace.get_tracer(__name__)
        request: Request = Request(environ)
        headers: dict[str, str] = request.headers

        ctx: Optional[Context] = None
        if "Traceparent" in headers:
            ctx = TraceContextTextMapPropagator().extract(
                carrier={"traceparent": headers["Traceparent"]}
            )
        if "Baggage" in headers:
            ctx = W3CBaggagePropagator().extract(
                carrier={"baggage": headers["Baggage"]},
                context=ctx,
            )

        # Reuse the context to create a new span
        with tracer.start_as_current_span(
            "middleware_span", context=ctx, kind=trace.SpanKind.SERVER
        ) as span:
            # NOTE: Set the context in the environment and use it later
            environ["otlp.context"] = ctx
            for key, value in baggage.get_all(ctx).items():
                span.set_attribute(key, value)

            return self.app(environ, start_response)


"""
Unit tests of wsgi.py
"""
import pytest
import json
from flask import Flask, request


# @pytest.fixture
def tset_middleware_app(proce: SpanProcessor):
    app: Flask = Flask(__name__)
    app.wsgi_app = OtlpMiddleware(app.wsgi_app, processor=proce)

    @app.route("/echo")
    def echo() -> str:
        environ: dict[str, str] = request.environ
        tracer: trace.Tracer = trace.get_tracer(__name__)
        with tracer.start_as_current_span("echo_span") as span:
            trace_id: str = span.get_span_context().trace_id
            ctx: trace.SpanContext = environ["otlp.context"]
            bags: list[str] = [
                f"{key}={value}" for key, value in baggage.get_all(ctx).items()
            ]
            return json.dumps({"trace_id": trace_id, "baggage": bags})

    return app


from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry.sdk.trace import ReadableSpan


def test_middleware_case_1():
    exporter: InMemorySpanExporter = InMemorySpanExporter()
    processor: SimpleSpanProcessor = SimpleSpanProcessor(exporter)
    app = tset_middleware_app(processor)
    tracer: trace.Tracer = trace.get_tracer(__name__)
    with app.test_client() as client:
        with tracer.start_as_current_span("test_span") as span:
            ctx = baggage.set_baggage("test_key_1", "test_value_1")
            ctx = baggage.set_baggage("test_key_2", "test_value_2", context=ctx)
            headers = {}
            W3CBaggagePropagator().inject(headers, ctx)
            TraceContextTextMapPropagator().inject(headers, ctx)

            response: Response = client.get("/echo", headers=headers)

            # Check the response (context)
            assert response.status_code == 200
            data: dict[str, str] = json.loads(response.data)
            assert "trace_id" in data
            assert data["trace_id"] == span.get_span_context().trace_id
            assert "baggage" in data
            assert data["baggage"] == [
                "test_key_1=test_value_1",
                "test_key_2=test_value_2",
            ]

            # Check the span
            span_list: tuple[ReadableSpan, ...] = exporter.get_finished_spans()
            for s in span_list:
                print(s.to_json())
            assert len(span_list) == 2
            for span in span_list:
                assert span.get_span_context().trace_id == data["trace_id"]
                if span.name == "middleware_span":
                    assert span.kind == trace.SpanKind.SERVER
                    assert span.attributes == {
                        "test_key_1": "test_value_1",
                        "test_key_2": "test_value_2",
                    }
                assert span.name in ["middleware_span", "echo_span"]
