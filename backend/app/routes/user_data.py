from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.deps.auth import CurrentUser, get_current_user
from app.services.db_store import UserDataRepository

router = APIRouter()


@router.delete("/user-data")
async def delete_user_data(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await UserDataRepository.delete_all_user_data(db, current_user.id)
    return {"deleted": True}
