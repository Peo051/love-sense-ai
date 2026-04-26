from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ConsentSettings(BaseModel):
    history_enabled: bool = True
    save_input: bool = False
    save_result: bool = False
    consent_type: str = Field(default="analysis_history", max_length=80)
    is_accepted: bool = False
    accepted_at: Optional[datetime] = None


class ConsentUpdate(BaseModel):
    history_enabled: bool = True
    save_input: bool = False
    save_result: bool = False
    consent_type: str = Field(default="analysis_history", max_length=80)
    is_accepted: bool = False
