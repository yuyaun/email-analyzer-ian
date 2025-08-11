"""內部使用的監控與健康檢查 API。"""

from fastapi import APIRouter
from sqlalchemy.sql import text
from app.core import database
from app.core.config import settings
from app.mq import producer

router = APIRouter(prefix="/internal/v1", tags=["internal"])


@router.get("/readiness")
def readiness() -> dict:
    """Return service readiness state."""
    return {"status": "ready"}


@router.get("/liveness")
async def liveness() -> dict:
    """Perform liveness checks without failing if dependencies are unavailable."""
    try:
        async with database.AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
    except Exception as exc:  # pragma: no cover - best-effort check
        print(f"Database liveness check failed: {exc}")

    try:
        kafka = producer.KafkaProducer(
            bootstrap_servers=settings.kafka_bootstrap_servers,
        )
        await kafka.start()
        await kafka.stop()
    except Exception as exc:  # pragma: no cover - best-effort check
        print(f"Kafka liveness check failed: {exc}")

    return {"status": "ok"}
