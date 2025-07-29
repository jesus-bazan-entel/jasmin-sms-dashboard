from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def read_contacts():
    return [{"name": "Contact 1"}, {"name": "Contact 2"}]
