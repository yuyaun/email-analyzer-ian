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
    campaign_sn: str = Field(alias="campaignSn")
    magic_type: str = Field(alias="magicType")
    content: str


class GenerateResponse(BaseModel):
    status: str


@router.post("/generate", response_model=GenerateResponse, status_code=202)
def generate(
    payload: GenerateRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    try:
        jwt.decode(credentials.credentials, settings.jwt_secret, algorithms=["HS256"])
    except jwt.PyJWTError as exc:  # pragma: no cover - can't trigger easily
        raise HTTPException(status_code=401, detail="Invalid token") from exc

    data = payload.model_dump(by_alias=True)
    producer.produce(settings.kafka_topic, json.dumps(data))
    producer.flush()

    return GenerateResponse(status="queued")
