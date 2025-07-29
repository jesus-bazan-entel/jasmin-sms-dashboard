from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def read_messages():
    return [{"text": "Hello"}, {"text": "World"}]
