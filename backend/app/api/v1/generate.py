"""提供將 LLM 任務加入佇列的公開 API。"""

import json
import jwt
from confluent_kafka import Producer
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field

from app.core.config import settings

router = APIRouter(prefix="/public/v1", tags=["public"])
security = HTTPBearer()

producer = Producer({"bootstrap.servers": settings.kafka_bootstrap_servers})


class GenerateRequest(BaseModel):
    """使用者提交的產生任務內容。"""

    campaign_sn: str = Field(alias="campaignSn")
    magic_type: str = Field(default="title_optimize", alias="magicType")
    content: str


class GenerateResponse(BaseModel):
    """API 回傳的結果格式。"""

    status: str


@router.post("/generate", response_model=GenerateResponse, status_code=202)
def generate(
    payload: GenerateRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """驗證 JWT 並將任務送入 Kafka。"""
    try:
        jwt.decode(credentials.credentials, settings.jwt_secret, algorithms=["HS256"])
    except jwt.PyJWTError as exc:  # pragma: no cover - can't trigger easily
        raise HTTPException(status_code=401, detail="Invalid token") from exc

    data = payload.model_dump(by_alias=True)
    producer.produce(settings.kafka_topic, json.dumps(data))
    producer.flush()

    return GenerateResponse(status="queued")
