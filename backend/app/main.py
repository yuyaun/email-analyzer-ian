import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.router import api_router
from app.core.database import Base
from app.job import scheduler
from sqlalchemy.ext.asyncio import create_async_engine
from app.core.config import settings

async_engine = create_async_engine(settings.database_url)

async def init_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


app = FastAPI()

# TODO 未來要處理指定的 CORS origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

base_router = os.getenv("BASE_ROUTER", "")
app.include_router(api_router, prefix=f"/{base_router}/api")

if os.getenv("CRON_JOB", "false").lower() in {"1", "true", "yes"}:
    scheduler.start()
