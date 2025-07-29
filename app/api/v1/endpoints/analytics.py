from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_analytics_data():
    return {"users": 150, "messages_sent": 25000}
