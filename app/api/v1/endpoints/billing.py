from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_billing_info():
    return {"credits": 1000, "plan": "premium"}
