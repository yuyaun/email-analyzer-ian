from datetime import datetime
import jwt  # PyJWT library
from fastapi import APIRouter
from pydantic import BaseModel

from app.core.config import settings

router = APIRouter()


class JWTRequest(BaseModel):
    userSn: str
    exp: datetime


@router.post("/v1/jwt")
def generate_jwt(payload: JWTRequest) -> dict:
    data = {"userSn": payload.userSn, "exp": int(payload.exp.timestamp())}
    token = jwt.encode(data, settings.jwt_secret, algorithm="HS256")
    return {"token": token}
