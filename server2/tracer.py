from typing import Optional
from opentelemetry import trace, baggage
from opentelemetry.sdk.trace import TracerProvider, SpanProcessor
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from opentelemetry.sdk.trace.sampling import (
    Sampler,
    StaticSampler,
    Decision,
    ParentBased,
)


def init_TracerProvider(
    processor: Optional[SpanProcessor] = None, sampler: Optional[Sampler] = None
):
    """
    Initialize TracerProvider
    """

    # NOTE: Initialize the TracerProvider
    tracer_provider: TracerProvider = TracerProvider(
        resource=Resource(
            attributes={
                SERVICE_NAME: "andylu-http-example",
            }
        ),
        sampler=sampler,
    )

    # NOTE: Register the span processors with TracerProvider
    if processor is not None:
        tracer_provider.add_span_processor(processor)

    trace.set_tracer_provider(tracer_provider)
