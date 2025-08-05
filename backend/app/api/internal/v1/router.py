from fastapi import APIRouter
from app.api.internal.v1.endpoints import healthcheck

router = APIRouter()
router.include_router(healthcheck.router, tags=["internal:health"])
