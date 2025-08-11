"""FastAPI application entry point that wires routes and services."""

import asyncio
import os
from contextlib import asynccontextmanager, suppress

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


def _cron_job_enabled() -> bool:
    """Return True when scheduled jobs should run."""
    return os.getenv("CRON_JOB", "false").lower() in {"1", "true", "yes"}


def _consumer_enabled() -> bool:
    """Return True when the Kafka consumer should run."""
    return os.getenv("CONSUMER", "false").lower() in {"1", "true", "yes"}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage optional background services during app lifespan."""
    consumer_task = None
    if _cron_job_enabled():
        scheduler.start()
    if _consumer_enabled():
        from app.mq.consumer import consume_messages

        consumer_task = asyncio.create_task(consume_messages())
    try:
        yield
    finally:
        if _cron_job_enabled():
            scheduler.shutdown()
        if consumer_task:
            consumer_task.cancel()
            with suppress(asyncio.CancelledError):
                await consumer_task


# Create the FastAPI application instance
app = FastAPI(lifespan=lifespan)
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
