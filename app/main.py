from contextlib import asynccontextmanager

from fastapi import FastAPI

from app import settings
from app.database import create_db_and_tables
from app.routers import auth_router, primes_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION, lifespan=lifespan)

app.include_router(auth_router)
app.include_router(primes_router)


@app.get("/")
async def root():
    return {
        "message": "Primes Backend API",
        "version": settings.APP_VERSION,
        "docs": "/docs",
    }
