from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.tutor.mastery import MasteryEvent


class SkillMasteryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    skill_id: str = Field(..., description="Mã kỹ năng chuẩn hóa (ví dụ: csharp.property)")
    skill_name: Optional[str] = Field(None, description="Tên hiển thị tiếng Việt của kỹ năng")
    mastery_score: float = Field(..., ge=0.0, le=1.0, description="Điểm thuần thục trong khoảng [0.0, 1.0]")
    success_count: int = Field(..., ge=0, description="Số lần giải thành công")
    failure_count: int = Field(..., ge=0, description="Số lần thử thất bại/chưa sửa được")
    hint_count: int = Field(..., ge=0, description="Tổng số gợi ý đã sử dụng")
    last_practiced_at: Optional[datetime] = Field(None, description="Thời điểm luyện tập gần nhất")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class StudentMasterySummaryResponse(BaseModel):
    total_skills: int = Field(..., description="Tổng số kỹ năng trong phiên bản taxonomy hiện tại")
    practiced_skills: int = Field(..., description="Số kỹ năng sinh viên đã từng luyện tập")
    average_mastery: float = Field(..., ge=0.0, le=1.0, description="Điểm thuần thục trung bình")
    skills: list[SkillMasteryResponse] = Field(default_factory=list, description="Danh sách chi tiết từng kỹ năng")


class EventDeltaInfoResponse(BaseModel):
    delta: float
    description: str
    pedagogical_rationale: str


class FormulaDocumentationResponse(BaseModel):
    formula_name: str
    version: str
    initial_mastery: float
    score_bounds: list[float]
    mathematical_formula: str
    description: str
    event_deltas: dict[str, EventDeltaInfoResponse]
    initial_state_explanation: str
    clamping_rule: str


class RecordPracticeAttemptRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    skill_ids: list[str] = Field(..., min_length=1, description="Danh sách các mã kỹ năng liên quan đến bài tập")
    event: MasteryEvent = Field(..., description="Loại kết quả/sự kiện luyện tập")
    hints_used: int = Field(default=0, ge=0, description="Số lượng gợi ý đã dùng trong lần thử này")
