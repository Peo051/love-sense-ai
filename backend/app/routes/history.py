from fastapi import APIRouter, HTTPException

from app.schemas.history_schema import HistoryItem, HistoryListResponse
from app.services.memory_store import HistoryService

router = APIRouter()


@router.get("/history", response_model=HistoryListResponse)
async def get_history():
    return HistoryService.list_history()


@router.delete("/history")
async def clear_history():
    HistoryService.clear_history()
    return {"deleted": True}


@router.get("/history/{analysis_id}", response_model=HistoryItem)
async def get_history_detail(analysis_id: str):
    item = HistoryService.get_history_item(analysis_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy lịch sử phân tích.")
    return item


@router.delete("/history/{analysis_id}")
async def delete_history_item(analysis_id: str):
    deleted = HistoryService.delete_history_item(analysis_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Không tìm thấy lịch sử phân tích.")
    return {"deleted": True}
