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


class RecentAttemptSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    attempt_id: str = Field(..., description="ID lần thử làm bài")
    session_id: Optional[str] = Field(None, description="ID phiên học tập liên quan")
    problem_title: str = Field(..., description="Tên hoặc trích dẫn đề bài bài tập")
    outcome: str = Field(..., description="Trạng thái kết quả lần thử (resolved, failed, v.v.)")
    skills: list[str] = Field(default_factory=list, description="Danh sách mã kỹ năng liên quan")
    hints_used: int = Field(default=0, ge=0, description="Số lượng gợi ý đã sử dụng")
    highest_hint_level: int = Field(default=0, ge=0, le=4, description="Cấp độ gợi ý cao nhất đã dùng")
    created_at: datetime = Field(..., description="Thời điểm thực hiện lần thử")


class StudentProgressDashboardResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    total_skills: int = Field(..., description="Tổng số kỹ năng trong taxonomy C# OOP")
    practiced_skills: int = Field(..., description="Số kỹ năng sinh viên đã thực hành")
    current_mastery_estimate: float = Field(..., ge=0.0, le=1.0, description="Điểm thuần thục trung bình ước lượng của hệ thống")
    is_empty: bool = Field(..., description="True nếu người dùng chưa có lần thử hoặc kỹ năng thực hành nào")
    strong_topics: list[SkillMasteryResponse] = Field(default_factory=list, description="Các kỹ năng vững vàng nhất của sinh viên")
    topics_needing_practice: list[SkillMasteryResponse] = Field(default_factory=list, description="Các kỹ năng cần ôn luyện thêm")
    all_skills: list[SkillMasteryResponse] = Field(default_factory=list, description="Toàn bộ danh sách kỹ năng C# OOP")
    recent_attempts: list[RecentAttemptSummary] = Field(default_factory=list, description="Danh sách các lần thử gần nhất")
    average_hint_level: Optional[float] = Field(None, description="Cấp độ gợi ý trung bình (null nếu chưa có bài tập)")
    independent_solution_rate: Optional[float] = Field(None, ge=0.0, le=1.0, description="Tỷ lệ giải thành công độc lập không cần gợi ý (null nếu chưa có bài giải thành công)")
    total_attempts_count: int = Field(default=0, ge=0, description="Tổng số lần thử bài tập đã thực hiện")
    independent_success_count: int = Field(default=0, ge=0, description="Số lần giải thành công độc lập")

