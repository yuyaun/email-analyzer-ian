from datetime import datetime
import jwt
from fastapi import APIRouter
from pydantic import BaseModel

from app.core.config import settings

router = APIRouter(prefix="/public/v1", tags=["public"])


class JWTRequest(BaseModel):
    userSn: str
    exp: datetime


@router.post("/jwt")
def generate_jwt(payload: JWTRequest) -> dict:
    data = {"userSn": payload.userSn, "exp": int(payload.exp.timestamp())}
    token = jwt.encode(data, settings.jwt_secret, algorithm="HS256")
    return {"token": token}
