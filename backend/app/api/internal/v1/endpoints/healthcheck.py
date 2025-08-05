from fastapi import APIRouter, HTTPException
from sqlalchemy import text
from confluent_kafka import Producer

from app.core.config import settings
from app.core.database import engine
from app.core.logger import log_event


router = APIRouter()

@router.get("/readiness")
def readiness() -> dict:
    """Simple readiness probe."""
    return {"status": "ready"}

@router.get("/liveness")
def liveness() -> dict:
    """Check database and Kafka availability."""
    db_ok = False
    kafka_ok = False
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        db_ok = True
    except Exception as exc:  # pragma: no cover
        log_event("liveness", "db_error", {"error": str(exc)}, level="ERROR")

    try:
        producer = Producer({"bootstrap.servers": settings.kafka_bootstrap_servers})
        producer.list_topics(timeout=1)
        kafka_ok = True
    except Exception as exc:  # pragma: no cover
        log_event("liveness", "kafka_error", {"error": str(exc)}, level="ERROR")

    if not (db_ok and kafka_ok):
        raise HTTPException(status_code=503, detail={"db": db_ok, "kafka": kafka_ok})

    return {"status": "ok"}
