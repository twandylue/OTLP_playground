from typing import Optional
from tracer import init_TracerProvider
from werkzeug.wrappers import Request, Response, ResponseStream
from opentelemetry import trace, baggage
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
from opentelemetry.baggage.propagation import W3CBaggagePropagator
from opentelemetry.context.context import Context
from opentelemetry.sdk.trace import SpanProcessor
from opentelemetry.trace import NonRecordingSpan, INVALID_SPAN, SpanContext, TraceFlags
from opentelemetry.sdk.trace.sampling import (
    Sampler,
    ParentBased,
    ALWAYS_OFF,
    ALWAYS_ON,
)


class OtlpMiddleware:
    """
    Middleware for the application to handle the incoming request with OTLP headers
    """

    def __init__(self, app, processor: Optional[SpanProcessor] = None):
        self.app = app
        # Initialize TracerProvider
        init_TracerProvider(
            processor=processor,
            sampler=ParentBased(root=ALWAYS_OFF),
        )

    def __call__(
        self, environ: dict[str, str], start_response: callable
    ) -> ResponseStream:
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
        if "Traceparent" not in headers and "Baggage" not in headers:
            print("Not going to recording span")
            ctx = trace.set_span_in_context(INVALID_SPAN)
        tracer: trace.Tracer = trace.get_tracer(__name__)
        # Reuse the context to create a new span
        with tracer.start_as_current_span(
            "middleware_span", context=ctx, kind=trace.SpanKind.SERVER
        ) as span:
            # NOTE: Set the context in the environment and use it later
            if ctx is not None:
                environ["otlp.context"] = ctx
            for key, value in baggage.get_all(ctx).items():
                span.set_attribute(key, value)

            return self.app(environ, start_response)
