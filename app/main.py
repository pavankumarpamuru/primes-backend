from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.database import create_db_and_tables
from app.routers import auth_router
from app import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan
)

app.include_router(auth_router)


@app.get("/")
async def root():
    return {
        "message": "Primes Backend API",
        "version": settings.APP_VERSION,
        "docs": "/docs"
    }
