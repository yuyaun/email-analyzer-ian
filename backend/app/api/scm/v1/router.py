from fastapi import APIRouter
from app.api.scm.v1.endpoints import order

router = APIRouter()
router.include_router(order.router, prefix="/orders", tags=["scm:orders"])