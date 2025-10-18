from fastapi import APIRouter

router = APIRouter()

@router.get("/health", tags=["health"])
async def healthcheck():
    return {"status": "ok", "message": "API is healthy"}
