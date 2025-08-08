"""FastAPI 應用程式的進入點，負責初始化服務與路由。"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

# 匯入 API 路由與資料庫設定
from app.api.router import api_router
from app.core.database import Base
from app.job import scheduler
from sqlalchemy.ext.asyncio import create_async_engine
from app.core.config import settings
from app.core.rate_limit import limiter, rate_limit_exceeded_handler

async_engine = create_async_engine(settings.database_url)

async def init_db():
    """初始化資料庫並建立所有資料表。"""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# 建立 FastAPI 主要應用程式實例
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# TODO 未來要處理指定的 CORS origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 從環境變數取得自訂的 API 前綴，方便部署於不同路徑
base_router = os.getenv("BASE_ROUTER", "")
app.include_router(api_router, prefix=f"/{base_router}/api")

if os.getenv("CRON_JOB", "false").lower() in {"1", "true", "yes"}:
    # 依環境設定啟動排程工作
    scheduler.start()
