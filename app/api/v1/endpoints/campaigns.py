from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def read_campaigns():
    return [{"name": "Campaign A"}, {"name": "Campaign B"}]
