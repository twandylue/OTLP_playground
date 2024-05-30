# Description: Middleware for the application
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
        self.tracer: trace.Tracer = init_tracer()
        self.app: callable[..., ResponseStream] = app

    def __call__(self, environ: dict[str, str], start_response: callable):
        request: Request = Request(environ)
        headers: dict[str, str] = request.headers
        print(f"Received headers: {headers}")

        carrier: dict[str, str] = {"traceparent": headers["Traceparent"]}
        ctx: trace.SpanContext = TraceContextTextMapPropagator().extract(
            carrier=carrier
        )
        print(f"Received context: {ctx}")

        b2: dict[str, str] = {"baggage": headers["Baggage"]}
        ctx2: trace.SpanContext = W3CBaggagePropagator().extract(b2)
        print(f"Received context2: {ctx2}")

        # # Start a new span
        # with tracer.start_span("api2_span", context=ctx2):
        #     print(baggage.get_baggage("hello", ctx2))
        #     return "Hello from API 2!"

        # Reuse the context to create a new span
        with self.tracer.start_span("api2_middleware_span", context=ctx):
            # NOTE: Set the tracer in the environment for context propagation
            environ["otlp.tracer"] = self.tracer
            environ["otlp.context"] = ctx

            return self.app(environ, start_response)
