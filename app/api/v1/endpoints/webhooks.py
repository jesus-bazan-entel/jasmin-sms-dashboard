from fastapi import APIRouter, Request

router = APIRouter()

@router.post("/")
async def handle_webhook(request: Request):
    payload = await request.json()
    print(f"Received webhook: {payload}")
    return {"status": "received"}
