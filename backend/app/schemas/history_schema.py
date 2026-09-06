from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel


class HistoryItem(BaseModel):
    id: str
    analyzed_at: datetime
    overall_emotion: str
    confidence: float
    emotion_distribution: dict[str, Any]
    summary: str
    context_note: str
    suggested_reply: str
    warning: str
    save_input: bool
    save_result: bool
    chat_text: Optional[str] = None


class HistoryListResponse(BaseModel):
    items: list[HistoryItem]
