"""FastAPI application entry point that wires routes and services."""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

# Import API router and database settings
from app.api.router import api_router
from app.core.database import Base
from app.job import scheduler
from sqlalchemy.ext.asyncio import create_async_engine
from app.core.config import settings
from app.core.rate_limit import limiter, rate_limit_exceeded_handler

async_engine = create_async_engine(settings.database_url)

async def init_db():
    """Initialize the database and create all tables."""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# Create the FastAPI application instance
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# TODO Handle specific CORS origins in the future
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Read API prefix from environment for flexible deployment paths
base_router = os.getenv("BASE_ROUTER", "")
app.include_router(api_router, prefix=f"/{base_router}/api")


def _cron_job_enabled() -> bool:
    """Return True when scheduled jobs should run."""
    return os.getenv("CRON_JOB", "false").lower() in {"1", "true", "yes"}


if _cron_job_enabled():
    # Start background scheduler based on environment configuration
    scheduler.start()
