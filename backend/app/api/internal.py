"""內部使用的監控與健康檢查 API。"""

from fastapi import APIRouter, HTTPException, status
from sqlalchemy.sql import text
from app.core import database
from aiokafka import AIOKafkaProducer
from app.core.config import settings

router = APIRouter(prefix="/internal/v1", tags=["internal"])


@router.get("/readiness")
def readiness() -> dict:
    """Return service readiness state."""
    return {"status": "ready"}


@router.get("/liveness")
async def liveness() -> dict:
    """Check database and Kafka connectivity."""
    try:
        with database.SessionLocal() as session:
            session.execute(text("SELECT 1"))
        producer = AIOKafkaProducer(
            bootstrap_servers=settings.kafka_bootstrap_servers
        )
        await producer.start()
        await producer.stop()
    except Exception as exc:  # pragma: no cover - error path
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service unavailable",
        ) from exc
    return {"status": "ok"}
