from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class MasteryAuditResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="ID bản ghi kiểm toán")
    user_id: str = Field(..., description="ID sinh viên sở hữu")
    skill_id: str = Field(..., description="Mã kỹ năng chuẩn hóa")
    attempt_id: str = Field(..., description="ID lần thử bài làm phát sinh cập nhật")
    event_type: str = Field(..., description="Loại sự kiện (independent_success, hint_l1_success, etc.)")
    previous_score: float = Field(..., ge=0.0, le=1.0, description="Điểm số trước khi cập nhật")
    new_score: float = Field(..., ge=0.0, le=1.0, description="Điểm số sau khi cập nhật")
    reason: str = Field(..., description="Giải trình sư phạm của lần cập nhật điểm")
    created_at: datetime = Field(..., description="Thời điểm ghi nhận kiểm toán")


class AttemptOutcomeResolutionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    outcome: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Kết quả tương tác thực tế của lần thử (resolved, likely_resolved, failed, unresolved, solution_revealed)",
    )
    highest_hint_level: int = Field(
        default=0,
        ge=0,
        le=4,
        description="Cấp độ gợi ý cao nhất sinh viên đã sử dụng trong lần thử này",
    )
    solution_revealed: bool = Field(
        default=False,
        description="Cờ đánh dấu sinh viên có xem lời giải chi tiết (Level 4) hay không",
    )
    hints_used: int = Field(
        default=0,
        ge=0,
        description="Tổng số gợi ý đã sử dụng trong lần thử này",
    )
    custom_reason: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Ghi chú/lý do tùy chỉnh cho việc cập nhật",
    )


class AttemptOutcomeResolutionResponse(BaseModel):
    attempt_id: str
    success_state: str
    audit_records: list[MasteryAuditResponse]
