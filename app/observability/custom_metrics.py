from opentelemetry import metrics

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


def record_prime_generation(duration_ms: float):
    primes_requests_counter.add(1)
    primes_generation_duration.record(duration_ms)
