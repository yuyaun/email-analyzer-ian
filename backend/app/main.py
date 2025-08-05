import os
from fastapi import FastAPI
from app.api.router import api_router
from app.core.database import Base, engine
from app.job import scheduler

Base.metadata.create_all(bind=engine)

app = FastAPI()
base_router = os.getenv("BASE_ROUTER", "")
app.include_router(api_router, prefix=f"/{base_router}/api")

if os.getenv("CRON_JOB", "false").lower() in {"1", "true", "yes"}:
    scheduler.start()
