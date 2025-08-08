"""提供將 LLM 任務加入佇列並接收結果的公開 API。"""

import asyncio
import json
from contextlib import suppress
from uuid import uuid4

import jwt
from aiokafka import AIOKafkaConsumer
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field

from app.core.config import settings
from app.memory_store import save_task_result, get_task_result_with_lock
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
    result: dict | list[dict] | None = None


@router.post("/generate", response_model=GenerateResponse, status_code=200)
async def generate(
    payloads: list[GenerateRequest],
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """驗證 JWT 並將任務列表送入 Kafka，並等待結果回傳。"""
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

    results: list[dict] = []
    for payload in payloads:
        task_id = str(uuid4())
        data = payload.model_dump(by_alias=True)
        data["task_id"] = task_id

        await kafka_producer.send_and_wait(
            settings.kafka_topic, json.dumps(data).encode("utf-8")
        )

        for _ in range(100):
            result = await get_task_result_with_lock(task_id)
            if result:
                results.append(result)
                break
            await asyncio.sleep(0.1)
        else:  # pragma: no cover - timeout branch
            raise HTTPException(status_code=504, detail="Task result timeout")

    return GenerateResponse(
        status="done", result=results[0] if len(results) == 1 else results
    )


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
            log_event(
                "llm_handler",
                "consume_result",
                {"message": msg.value.decode("utf-8")},
            )
            data = json.loads(msg.value.decode("utf-8"))
            task_id = data.get("task_id")
            if task_id:
                await save_task_result(task_id, data)
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
