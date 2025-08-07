"""資料庫連線與 Session 管理。"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.config import settings

engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

async_engine = None
AsyncSessionLocal = None
if not settings.database_url.startswith("sqlite"):
    # 針對非 SQLite 資料庫嘗試建立非同步引擎
    async_database_url = settings.database_url.replace("+psycopg2", "+asyncpg")
    try:  # pragma: no cover - only exercised when asyncpg is installed
        async_engine = create_async_engine(async_database_url)
        AsyncSessionLocal = async_sessionmaker(
            bind=async_engine, expire_on_commit=False
        )
    except ModuleNotFoundError:
        # asyncpg 為選用套件；若缺少則忽略非同步引擎
        pass

Base = declarative_base()
