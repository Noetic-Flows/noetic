"""OpenTelemetry metrics configuration."""

from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider


# T021: Metrics module
def get_meter(name: str = "noetic_policies") -> metrics.Meter:
    """
    Get or create a meter for the noetic-policies package.

    Args:
        name: Meter name (default: "noetic_policies")

    Returns:
        OpenTelemetry meter instance
    """
    # Get the global meter provider, or create a default one
    provider = metrics.get_meter_provider()

    # If no provider is set, create a basic one
    if not isinstance(provider, MeterProvider):
        provider = MeterProvider()
        metrics.set_meter_provider(provider)

    return metrics.get_meter(name)


class ValidationMetrics:
    """Metrics for policy validation operations."""

    def __init__(self, meter: metrics.Meter | None = None):
        """
        Initialize validation metrics.

        Args:
            meter: OpenTelemetry meter (creates default if None)
        """
        self.meter = meter or get_meter()

        # Create metrics
        self.validation_duration = self.meter.create_histogram(
            name="validation.duration",
            description="Duration of policy validation in milliseconds",
            unit="ms",
        )

        self.validation_count = self.meter.create_counter(
            name="validation.count",
            description="Number of policy validations performed",
        )

        self.validation_errors = self.meter.create_counter(
            name="validation.errors",
            description="Number of validation errors encountered",
        )

    def record_validation(
        self,
        duration_ms: float,
        mode: str,
        is_valid: bool,
        error_count: int = 0,
    ) -> None:
        """
        Record a validation operation.

        Args:
            duration_ms: Duration in milliseconds
            mode: Validation mode ("fast" or "thorough")
            is_valid: Whether validation passed
            error_count: Number of errors found
        """
        attributes = {
            "mode": mode,
            "result": "valid" if is_valid else "invalid",
        }

        self.validation_duration.record(duration_ms, attributes)
        self.validation_count.add(1, attributes)

        if error_count > 0:
            self.validation_errors.add(error_count, attributes)
