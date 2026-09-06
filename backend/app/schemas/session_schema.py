from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class SessionCreateRequest(BaseModel):
    """Yêu cầu khởi tạo một phiên học tập mới."""
    title: str = Field(..., min_length=1, max_length=255, description="Tiêu đề phiên học")
    language: str = Field(default="csharp", max_length=50, description="Ngôn ngữ lập trình")
    topic: Optional[str] = Field(default=None, max_length=100, description="Chủ đề bài toán C# OOP")
    initial_problem: Optional[str] = Field(default=None, max_length=5000, description="Đề bài ban đầu nếu có")
    initial_code: Optional[str] = Field(default=None, max_length=50000, description="Mã nguồn ban đầu nếu có")
    save_input: bool = Field(default=False, description="Sự đồng thuận của sinh viên cho phép lưu mã nguồn")
    save_result: bool = Field(default=True, description="Đồng thuận lưu kết quả chẩn đoán vào phiên")

    @field_validator("title")
    @classmethod
    def clean_title(cls, value: str) -> str:
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("Title must not be empty or whitespace only.")
        return trimmed

    @field_validator("language")
    @classmethod
    def clean_language(cls, value: str) -> str:
        normalized = value.strip().lower()
        if normalized in ("c#", "cs"):
            return "csharp"
        return normalized


class AttemptCreateRequest(BaseModel):
    """Yêu cầu thêm một lần thử làm bài trong phiên học."""
    problem_reference: str = Field(..., min_length=1, max_length=5000, description="Đề bài hoặc tham chiếu bài toán")
    student_code: Optional[str] = Field(default=None, max_length=50000, description="Mã nguồn của sinh viên")
    save_input: bool = Field(default=False, description="Cờ đồng thuận lưu trữ mã nguồn")
    diagnosis: Optional[dict[str, Any]] = Field(default=None, description="Kết quả chẩn đoán kỹ thuật")
    hint_progression: Optional[dict[str, Any]] = Field(default=None, description="Trạng thái cấp độ gợi ý")
    success_state: str = Field(default="in_progress", max_length=50, description="Trạng thái hoàn thành bài làm")

    @field_validator("problem_reference")
    @classmethod
    def clean_problem_ref(cls, value: str) -> str:
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("Problem reference must not be empty.")
        return trimmed


class MessageCreateRequest(BaseModel):
    """Yêu cầu thêm tin nhắn hội thoại vào phiên học."""
    role: str = Field(..., max_length=30, description="Vai trò gửi tin nhắn: student, tutor, system")
    content: str = Field(..., min_length=1, max_length=10000, description="Nội dung văn bản của tin nhắn")
    attempt_id: Optional[str] = Field(default=None, description="ID của lần thử liên quan nếu có")

    @field_validator("role")
    @classmethod
    def validate_role(cls, value: str) -> str:
        cleaned = value.strip().lower()
        if cleaned not in ("student", "tutor", "system"):
            raise ValueError("Role must be one of: student, tutor, system.")
        return cleaned

    @field_validator("content")
    @classmethod
    def clean_content(cls, value: str) -> str:
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("Message content must not be empty.")
        return trimmed


class TutorMessageResponse(BaseModel):
    """Phản hồi thông tin một tin nhắn trong phiên học."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    session_id: str
    attempt_id: Optional[str] = None
    role: str
    sanitized_textual_message: str
    created_at: datetime


class StudentAttemptResponse(BaseModel):
    """Phản hồi thông tin một lần thử làm bài trong phiên học."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    session_id: str
    problem_reference: str
    diagnosis: Optional[dict[str, Any]] = None
    hint_progression: Optional[dict[str, Any]] = None
    success_state: str
    save_input: bool
    student_code: Optional[str] = None
    created_at: datetime


class SessionSummaryResponse(BaseModel):
    """Tóm tắt thông tin phiên học cho danh sách phiên."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    language: str
    topic: Optional[str] = None
    title: str
    created_at: datetime
    updated_at: datetime
    attempt_count: int = 0
    message_count: int = 0


class SessionDetailResponse(BaseModel):
    """Chi tiết toàn bộ phiên học kèm các lần thử và tin nhắn trao đổi."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    language: str
    topic: Optional[str] = None
    title: str
    created_at: datetime
    updated_at: datetime
    attempt_count: int = 0
    message_count: int = 0
    attempts: list[StudentAttemptResponse] = Field(default_factory=list)
    messages: list[TutorMessageResponse] = Field(default_factory=list)


class SessionDeleteResponse(BaseModel):
    """Phản hồi sau khi xóa phiên học thành công."""
    deleted: bool = True
    id: str
