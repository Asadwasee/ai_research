from fastapi import APIRouter

router = APIRouter(
    prefix="/health",
    tags=["Health"]
)

@router.get("")
async def health_check():
    """
    Basic liveness endpoint to check if the API is running.
    """
    return {"status": "healthy"}