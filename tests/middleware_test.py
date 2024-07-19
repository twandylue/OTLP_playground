# Unit tests of middleware.py

import sys

sys.path.append("../server2/")
from middleware import OtlpMiddleware

import pytest
from typing import Optional
from opentelemetry import trace, baggage
from opentelemetry.trace import SpanContext
from opentelemetry.context import Context
from opentelemetry.baggage.propagation import W3CBaggagePropagator
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry.sdk.trace import ReadableSpan, SpanProcessor
import json
from flask import Flask, request, Response


def middleware_app_test(proce: SpanProcessor) -> Flask:
    app: Flask = Flask(__name__)
    app.wsgi_app = OtlpMiddleware(app.wsgi_app, processor=proce)

    @app.route("/echo")
    def echo() -> str:
        environ: dict[str, str] = request.environ
        tracer: trace.Tracer = trace.get_tracer(__name__)
        with tracer.start_as_current_span("echo_span") as span:
            trace_id: str = span.get_span_context().trace_id
            ctx: Optional[Context] = None
            if "otlp.context" in environ:
                ctx = environ["otlp.context"]
            bags: list[str] = [
                f"{key}={value}" for key, value in baggage.get_all(ctx).items()
            ]
            return json.dumps({"trace_id": trace_id, "baggage": bags})

    return app


exporter: InMemorySpanExporter = InMemorySpanExporter()
processor: SimpleSpanProcessor = SimpleSpanProcessor(exporter)
app: Flask = middleware_app_test(processor)


def test_middleware_case_1():
    """
    Both W3CBaggagePropagator and TraceContextTextMapPropagator
    """
    tracer: trace.Tracer = trace.get_tracer(__name__)
    with app.test_client() as client:
        with tracer.start_as_current_span("test_span") as span:
            ctx = baggage.set_baggage("test_key_1", "test_value_1")
            ctx = baggage.set_baggage("test_key_2", "test_value_2", context=ctx)
            headers = {}
            W3CBaggagePropagator().inject(headers, ctx)
            TraceContextTextMapPropagator().inject(headers, ctx)
            # NOTE: set the trace_flags to 1 manually because we use the sampler in the middleware, and it will make every trace_flags to 0 (span.is_recording() = False)
            n = list(headers["traceparent"])
            n[-1] = "1"
            headers["traceparent"] = "".join(n)

            response: Response = client.get("/echo", headers=headers)

            # Check the response (context)
            assert response.status_code == 200
            data: dict[str, str] = json.loads(response.data)
            assert "trace_id" in data
            trace_id: str = span.get_span_context().trace_id
            assert data["trace_id"] == trace_id
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
                assert span.get_span_context().trace_id == trace_id
                if span.name == "middleware_span":
                    assert span.kind == trace.SpanKind.SERVER
                    assert span.attributes == {
                        "test_key_1": "test_value_1",
                        "test_key_2": "test_value_2",
                    }
                assert span.name in ["middleware_span", "echo_span"]

    # Clean up
    exporter.clear()


# TODO: need to check
@pytest. mark. skip(reason="We don't have the case without TraceContextTextMapPropagator") 
def test_middleware_case_2():
    """
    Only W3CBaggagePropagator
    """
    tracer: trace.Tracer = trace.get_tracer(__name__)
    with app.test_client() as client:
        with tracer.start_as_current_span("test_span") as span:
            ctx = baggage.set_baggage("test_key_1", "test_value_1")
            ctx = baggage.set_baggage("test_key_3", "test_value_3", context=ctx)
            headers = {}
            W3CBaggagePropagator().inject(headers, ctx)

            response: Response = client.get("/echo", headers=headers)

            # Check the response (context)
            assert response.status_code == 200
            data: dict[str, str] = json.loads(response.data)
            assert "trace_id" in data
            trace_id: str = span.get_span_context().trace_id
            assert data["trace_id"] == trace_id
            assert "baggage" in data
            assert data["baggage"] == [
                "test_key_1=test_value_1",
                "test_key_3=test_value_3",
            ]

            # Check the span
            span_list: tuple[ReadableSpan, ...] = exporter.get_finished_spans()
            for s in span_list:
                print(s.to_json())
            assert len(span_list) == 2
            for span in span_list:
                assert span.get_span_context().trace_id == trace_id
                if span.name == "middleware_span":
                    assert span.kind == trace.SpanKind.SERVER
                    assert span.attributes == {
                        "test_key_1": "test_value_1",
                        "test_key_3": "test_value_3",
                    }
                assert span.name in ["middleware_span", "echo_span"]
    # Clean up
    exporter.clear()


def test_middleware_case_3():
    """
    Only TraceContextTextMapPropagator
    """
    tracer: trace.Tracer = trace.get_tracer(__name__)
    with app.test_client() as client:
        with tracer.start_as_current_span("test_span") as span:
            headers = {}
            TraceContextTextMapPropagator().inject(headers)
            # NOTE: set the trace_flags to 1 manually because we use the sampler in the middleware, and it will make every trace_flags to 0 (span.is_recording() = False)
            n = list(headers["traceparent"])
            n[-1] = "1"
            headers["traceparent"] = "".join(n)

            response: Response = client.get("/echo", headers=headers)

            # Check the response (context)
            assert response.status_code == 200
            data: dict[str, str] = json.loads(response.data)
            assert "trace_id" in data
            trace_id: str = span.get_span_context().trace_id
            assert data["trace_id"] == trace_id
            assert "baggage" in data
            assert data["baggage"] == []

            # Check the span
            span_list: tuple[ReadableSpan, ...] = exporter.get_finished_spans()
            for s in span_list:
                print(s.to_json())
            assert len(span_list) == 2
            for span in span_list:
                assert span.get_span_context().trace_id == trace_id
                if span.name == "middleware_span":
                    assert span.kind == trace.SpanKind.SERVER
                    assert span.attributes == {}
                assert span.name in ["middleware_span", "echo_span"]
    # Clean up
    exporter.clear()


def test_middleware_case_4():
    """
    No propagator
    """
    tracer: trace.Tracer = trace.get_tracer(__name__)
    with app.test_client() as client:
        headers = {}
        response: Response = client.get("/echo", headers=headers)

        # Check the response (context)
        assert response.status_code == 200
        data: dict[str, str] = json.loads(response.data)
        assert "trace_id" in data
        # Trace ID is generated by the middleware
        assert data["trace_id"] is not None
        assert "baggage" in data
        assert data["baggage"] == []

        # Check the span
        span_list: tuple[ReadableSpan, ...] = exporter.get_finished_spans()
        for s in span_list:
            print(s.to_json())
        assert len(span_list) == 0
    # Clean up
    exporter.clear()
