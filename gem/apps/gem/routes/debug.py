from fastapi import APIRouter

from db import recreate_db

router = APIRouter()


@router.post("/wipeout")
async def debug_wipeout():
    recreate_db()
    print("Wipedout")
    return {"done": True}
