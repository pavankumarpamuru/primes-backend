from opentelemetry import metrics
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource


def setup_metrics(
    service_name: str = "primes-backend",
    otlp_endpoint: str = "http://otel-collector:4317",
    environment: str = "development",
):
    resource = Resource(
        attributes={
            "service.name": service_name,
            "service.version": "1.0.0",
            "deployment.environment": environment,
        }
    )

    otlp_exporter = OTLPMetricExporter(endpoint=otlp_endpoint, insecure=True)

    reader = PeriodicExportingMetricReader(
        exporter=otlp_exporter, export_interval_millis=15000
    )

    meter_provider = MeterProvider(resource=resource, metric_readers=[reader])

    metrics.set_meter_provider(meter_provider)

    return meter_provider
