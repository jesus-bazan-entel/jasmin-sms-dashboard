from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def read_templates():
    return [{"name": "Welcome Template"}, {"name": "Offer Template"}]
