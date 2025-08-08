"""提供將 LLM 任務加入佇列並接收結果的公開 API。"""

import asyncio
import json
from contextlib import suppress

import jwt
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field

from app.core.config import settings
from app.memory_store import save_task_result
from app.mq import producer
from app.core.logger import log_event

router = APIRouter(prefix="/public/v1", tags=["public"])
security = HTTPBearer()

kafka_producer: producer.KafkaProducer | None = None
result_task: asyncio.Task | None = None

class GenerateRequest(BaseModel):
    """使用者提交的產生任務內容。"""

    campaign_sn: str = Field(alias="campaignSn")
    magic_type: str = Field(default="title_optimize", alias="magicType")
    content: str
    num_suggestions: int = Field(default=1)


class GenerateResponse(BaseModel):
    """API 回傳的結果格式。"""

    status: str


@router.post("/generate", response_model=GenerateResponse, status_code=202)
async def generate(
    payloads: list[GenerateRequest],
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """驗證 JWT 並將任務列表送入 Kafka。"""
    try:
        jwt.decode(credentials.credentials, settings.jwt_secret, algorithms=["HS256"])
    except jwt.PyJWTError as exc:  # pragma: no cover - can't trigger easily
        raise HTTPException(status_code=401, detail="Invalid token") from exc

    global kafka_producer
    if kafka_producer is None:
        try:
            kafka_producer = producer.KafkaProducer(
                bootstrap_servers=settings.kafka_bootstrap_servers
            )
            await kafka_producer.start()
        except RuntimeError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc

    data = [payload.model_dump(by_alias=True) for payload in payloads]
    await kafka_producer.send_and_wait(
        settings.kafka_topic, json.dumps(data).encode("utf-8")
    )

    return GenerateResponse(status="queued")


async def _consume_results() -> None:
    """Background task to consume result messages and cache them in memory."""
    consumer = AIOKafkaConsumer(
        settings.kafka_result_topic,
        bootstrap_servers=settings.kafka_bootstrap_servers,
        group_id=f"{settings.kafka_consumer_group}-result",
        auto_offset_reset="earliest",
    )
    print("Starting Kafka consumer for results...")
    await consumer.start()
    try:
        async for msg in consumer:
            log_event("llm_handler", "consume_result", {"message": msg.value.decode("utf-8")})
            data = json.loads(msg.value.decode("utf-8"))
            for item in data:
                task_id = item.get("campaign_sn")
                if task_id:
                    await save_task_result(task_id, item)
    finally:
        await consumer.stop()


@router.on_event("startup")
async def _start_consumer() -> None:  # pragma: no cover - simple startup hook
    global result_task
    result_task = asyncio.create_task(_consume_results())


@router.on_event("shutdown")
async def _stop_consumer() -> None:  # pragma: no cover - simple shutdown hook
    if result_task:
        result_task.cancel()
        with suppress(Exception):
            await result_task
