from fastapi import APIRouter, Depends
from app.schemas.history_schema import HistoryResponse
from typing import List

router = APIRouter()

@router.get("/history", response_model=List[HistoryResponse])
async def get_history():
    # TODO: Get from database
    return [
        HistoryResponse(
            id="1",
            date="2026-04-26",
            message="Em nhớ anh quá!",
            emotion="Hạnh phúc",
            confidence=0.85
        )
    ]

@router.get("/history/{analysis_id}", response_model=HistoryResponse)
async def get_history_detail(analysis_id: str):
    # TODO: Get from database
    return HistoryResponse(
        id=analysis_id,
        date="2026-04-26",
        message="Em nhớ anh quá!",
        emotion="Hạnh phúc",
        confidence=0.85
    )
