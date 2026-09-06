from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.database.connection import get_db
from app.models.user import User
from app.schemas.history_schema import HistoryItem, HistoryListResponse
from app.services.db_store import HistoryRepository

router = APIRouter()


@router.get("/history", response_model=HistoryListResponse)
async def get_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await HistoryRepository.list_history(db, current_user.id)


@router.delete("/history")
async def clear_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await HistoryRepository.clear_history(db, current_user.id)
    return {"deleted": True}


@router.get("/history/{analysis_id}", response_model=HistoryItem)
async def get_history_detail(
    analysis_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    item = await HistoryRepository.get_history_item(db, current_user.id, analysis_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy lịch sử phân tích.")
    return item


@router.delete("/history/{analysis_id}")
async def delete_history_item(
    analysis_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    deleted = await HistoryRepository.delete_history_item(db, current_user.id, analysis_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Không tìm thấy lịch sử phân tích.")
    return {"deleted": True}
