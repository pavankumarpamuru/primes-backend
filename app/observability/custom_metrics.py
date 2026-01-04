import psutil
from opentelemetry import metrics
from opentelemetry.metrics import CallbackOptions, Observation

meter = metrics.get_meter(__name__)

primes_requests_counter = meter.create_counter(
    name="primes.requests.total",
    description="Total number of prime generation requests",
    unit="1",
)

primes_generation_duration = meter.create_histogram(
    name="primes.generation.duration",
    description="Time taken to generate primes in milliseconds",
    unit="ms",
)

http_errors_counter = meter.create_counter(
    name="http.errors.total",
    description="HTTP errors by status code and endpoint",
)

auth_attempts_counter = meter.create_counter(
    name="auth.attempts.total",
    description="Authentication attempts by result",
)

db_query_duration = meter.create_histogram(
    name="db.query.duration",
    description="Database query execution time",
    unit="ms",
)


def record_prime_generation(duration_ms: float):
    primes_requests_counter.add(1)
    primes_generation_duration.record(duration_ms)


def record_http_error(status_code: int, endpoint: str):
    http_errors_counter.add(1, {"status_code": str(status_code), "endpoint": endpoint})


def record_auth_attempt(success: bool, reason: str = None):
    labels = {"success": str(success).lower()}
    if not success and reason:
        labels["reason"] = reason
    auth_attempts_counter.add(1, labels)


def record_db_query(duration_ms: float, operation: str):
    db_query_duration.record(duration_ms, {"operation": operation})


def get_cpu_usage(options: CallbackOptions):
    return [Observation(psutil.cpu_percent(interval=0.1))]


def get_memory_usage(options: CallbackOptions):
    return [Observation(psutil.virtual_memory().percent)]


def get_disk_usage(options: CallbackOptions):
    return [Observation(psutil.disk_usage("/").percent)]


system_cpu_usage = meter.create_observable_gauge(
    name="system.cpu.usage",
    description="CPU usage percentage",
    callbacks=[get_cpu_usage],
    unit="%",
)

system_memory_usage = meter.create_observable_gauge(
    name="system.memory.usage",
    description="Memory usage percentage",
    callbacks=[get_memory_usage],
    unit="%",
)

system_disk_usage = meter.create_observable_gauge(
    name="system.disk.usage",
    description="Disk usage percentage",
    callbacks=[get_disk_usage],
    unit="%",
)
