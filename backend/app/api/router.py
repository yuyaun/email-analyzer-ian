from fastapi import APIRouter
from app.api.v1.jwt import router as jwt_router

api_router = APIRouter()
api_router.include_router(jwt_router)
