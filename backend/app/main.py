import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.router import api_router
from app.core.database import Base, engine
from app.job import scheduler

Base.metadata.create_all(bind=engine)

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
