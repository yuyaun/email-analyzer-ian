from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
import jwt

from app.core.config import settings

router = APIRouter(prefix="/public/v1", tags=["public"])
security = HTTPBearer()


class Suggestion(BaseModel):
    title: str
    content: str


class GenerateRequest(BaseModel):
    campaignSn: str
    content: str
    generation_type: str
    num_suggestions: int = Field(1, ge=1, le=5)


class GenerateData(BaseModel):
    suggestions: list[Suggestion]


class GenerateResponse(BaseModel):
    status: str
    data: GenerateData


@router.post("/generate", response_model=GenerateResponse)
def generate(
    payload: GenerateRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    try:
        jwt.decode(credentials.credentials, settings.jwt_secret, algorithms=["HS256"])
    except jwt.PyJWTError as exc:  # pragma: no cover - can't trigger easily
        raise HTTPException(status_code=401, detail="Invalid token") from exc

    suggestions = [
        Suggestion(title=f"建議 {i+1}", content="這是示範內容")
        for i in range(payload.num_suggestions)
    ]
    return GenerateResponse(status="success", data=GenerateData(suggestions=suggestions))
