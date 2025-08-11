"""內部使用的監控與健康檢查 API。"""

from fastapi import APIRouter, HTTPException, status
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
    """Check database and Kafka connectivity."""
    try:
        async with database.AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        kafka = producer.KafkaProducer(
            bootstrap_servers=settings.kafka_bootstrap_servers,
        )
        await kafka.start()
        await kafka.stop()
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    except Exception as exc:  # pragma: no cover - error path
        print(f"Error during liveness check: {exc}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service unavailable",
        ) from exc
    return {"status": "ok"}
