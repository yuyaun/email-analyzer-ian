"""提供將 LLM 任務加入佇列並接收結果的公開 API。"""

import asyncio
import json
from contextlib import asynccontextmanager, suppress
from uuid import uuid4

import jwt
from aiokafka import AIOKafkaConsumer
from fastapi import APIRouter, Depends, HTTPException, FastAPI, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field

from app.core.config import settings
from app.core.rate_limit import limiter
from app.memory_store import save_task_result, get_task_result_with_lock
from app.mq import producer
from app.core.logger import log_event

router = APIRouter(prefix="/public/v1", tags=["public"])
security = HTTPBearer()

kafka_producer: producer.KafkaProducer | None = None

class GenerateRequest(BaseModel):
    """使用者提交的產生任務內容。"""

    campaign_sn: str = Field(alias="campaignSn")
    magic_type: str = Field(default="title_optimize", alias="magicType")
    content: str
    num_suggestions: int = Field(default=1)


class GenerateResponse(BaseModel):
    """API 回傳的結果格式。"""
    magic_type: str
    status: str
    result: dict | list[dict] | None = None


@router.post("/generate", response_model=GenerateResponse, status_code=200)
@limiter.limit(settings.generate_rate_limit)
async def generate(
    request: Request,
    payload: GenerateRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """驗證 JWT 並將單筆任務送入 Kafka，並等待結果回傳。"""
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
        except RuntimeError as exc:  # pragma: no cover - producer init failure
            raise HTTPException(status_code=503, detail=str(exc)) from exc

    task_id = str(uuid4())
    data = payload.model_dump(by_alias=True)
    data["task_id"] = task_id
    await kafka_producer.send_and_wait(
        settings.kafka_topic, json.dumps(data).encode("utf-8")
    )

    for _ in range(100):
        result = await get_task_result_with_lock(task_id)
        if result:
            return GenerateResponse(
                magic_type=payload.magic_type, status="done", result=result
            )
        await asyncio.sleep(0.1)
    else:  # pragma: no cover - timeout branch
        raise HTTPException(status_code=504, detail="Task result timeout")


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
            results = data.get("results")
            if task_id is not None and results is not None:
                await save_task_result(task_id, results)
    finally:
        await consumer.stop()


@asynccontextmanager
async def lifespan(_: FastAPI):  # pragma: no cover - simple lifespan hook
    task = asyncio.create_task(_consume_results())
    global kafka_producer
    if kafka_producer is None:
        try:
            kafka_producer = producer.KafkaProducer(
                bootstrap_servers=settings.kafka_bootstrap_servers
            )
            await kafka_producer.start()
        except RuntimeError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc
    try:
        yield
    finally:
        task.cancel()
        with suppress(Exception):
            await task

router.lifespan_context = lifespan
