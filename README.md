# primes-backend
To find n primes

Everything runs in Docker using pure OpenTelemetry Protocol (OTLP).

## Quick Start

### 1. Start everything
```bash
docker compose up -d --build
```

This starts 4 containers:
- **FastAPI app** on port 8000
- **OpenTelemetry Collector** on ports 4317 (gRPC), 4318 (HTTP)
- **VictoriaMetrics** on port 8428
- **Grafana** on port 3000

### 2. Open Grafana
```
http://localhost:3000
Username: admin
Password: admin
```
