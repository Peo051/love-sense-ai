from fastapi import APIRouter

from app.services.memory_store import UserDataService

router = APIRouter()


@router.delete("/user-data")
async def delete_user_data():
    UserDataService.delete_all_user_data()
    return {"deleted": True}
