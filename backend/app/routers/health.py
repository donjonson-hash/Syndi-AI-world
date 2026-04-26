from fastapi import APIRouter
from ..schemas import HealthCheck
router = APIRouter()

@router.get("/health", response_model=HealthCheck)
async def health_check():
    return HealthCheck(status="ok", version="1.0.0", database="connected")
