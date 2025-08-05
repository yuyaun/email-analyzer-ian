from fastapi import APIRouter, HTTPException, status
from sqlalchemy.sql import text
from app.core import database
from confluent_kafka import Producer

router = APIRouter(prefix="/internal/v1", tags=["internal"])


@router.get("/readiness")
def readiness() -> dict:
    """Return service readiness state."""
    return {"status": "ready"}


@router.get("/liveness")
def liveness() -> dict:
    """Check database and Kafka connectivity."""
    try:
        with database.SessionLocal() as session:
            session.execute(text("SELECT 1"))
        producer = Producer({})
        producer.list_topics(timeout=1)
    except Exception as exc:  # pragma: no cover - error path
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service unavailable",
        ) from exc
    return {"status": "ok"}
