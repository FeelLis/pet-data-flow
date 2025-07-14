from fastapi import APIRouter

router = APIRouter(prefix="/recommendations")

@router.post(path="/one")
def upload_one_recommendation(type: data: dict):
    