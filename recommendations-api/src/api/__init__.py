from fastapi import APIRouter

from .recommendations import router as recommendations_router

router = APIRouter()
router.include_router(recommendations_router)


@router.get("/health")
def healthcheck():
    return 200
