import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

from app import settings
from app.database import create_db_and_tables
from app.routers import auth_router, primes_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()

    if os.getenv("ENABLE_METRICS", "false").lower() == "true":
        from app.observability.metrics import setup_metrics

        otlp_endpoint = os.getenv("OTLP_ENDPOINT", "http://otel-collector:4317")
        environment = os.getenv("ENVIRONMENT", "development")
        setup_metrics(
            service_name=settings.APP_NAME,
            otlp_endpoint=otlp_endpoint,
            environment=environment,
        )
        SQLAlchemyInstrumentor().instrument()

    yield


app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION, lifespan=lifespan)

if os.getenv("ENABLE_METRICS", "false").lower() == "true":
    FastAPIInstrumentor.instrument_app(app)

app.include_router(auth_router)
app.include_router(primes_router)


@app.get("/")
async def root():
    return {
        "message": "Primes Backend API",
        "version": settings.APP_VERSION,
        "docs": "/docs",
    }
