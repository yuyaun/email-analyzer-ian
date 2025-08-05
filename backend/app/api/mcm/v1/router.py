from fastapi import APIRouter
from app.api.mcm.v1.endpoints import product

router = APIRouter()
router.include_router(product.router, prefix="/products", tags=["mcm:products"])