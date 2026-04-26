from pydantic import BaseModel
from typing import Optional

class HistoryResponse(BaseModel):
    id: str
    date: str
    message: str
    emotion: str
    confidence: float
    suggested_reply: Optional[str] = None
