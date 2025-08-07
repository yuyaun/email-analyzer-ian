"""整合所有 API 子路由。"""

from fastapi import APIRouter
from app.api.v1.jwt import router as jwt_router
from app.api.v1.generate import router as generate_router
from app.api.internal import router as internal_router


api_router = APIRouter()
# 依序將各模組路由註冊到主路由器
api_router.include_router(internal_router)
api_router.include_router(jwt_router)
api_router.include_router(generate_router)
