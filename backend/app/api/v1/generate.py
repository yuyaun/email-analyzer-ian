"""提供將 LLM 任務加入佇列的公開 API。"""

import json
import jwt
from aiokafka import AIOKafkaProducer
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field

from app.core.config import settings

router = APIRouter(prefix="/public/v1", tags=["public"])
security = HTTPBearer()

producer: AIOKafkaProducer | None = None


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

    global producer
    if producer is None:
        producer = AIOKafkaProducer(
            bootstrap_servers=settings.kafka_bootstrap_servers
        )
        await producer.start()

    data = [payload.model_dump(by_alias=True) for payload in payloads]
    await producer.send_and_wait(
        settings.kafka_topic, json.dumps(data).encode("utf-8")
    )

    return GenerateResponse(status="queued")
