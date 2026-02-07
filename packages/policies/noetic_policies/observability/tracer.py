"""OpenTelemetry tracer configuration."""

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider


# T019: Tracer module
def get_tracer(name: str = "noetic_policies") -> trace.Tracer:
    """
    Get or create a tracer for the noetic-policies package.

    Args:
        name: Tracer name (default: "noetic_policies")

    Returns:
        OpenTelemetry tracer instance
    """
    # Get the global tracer provider, or create a default one
    provider = trace.get_tracer_provider()

    # If no provider is set, create a basic one
    if not isinstance(provider, TracerProvider):
        provider = TracerProvider()
        trace.set_tracer_provider(provider)

    return trace.get_tracer(name)
