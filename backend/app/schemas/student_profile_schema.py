from datetime import datetime
from enum import Enum
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class PreferredExplanation(str, Enum):
    CONCISE = "concise"
    STEP_BY_STEP = "step_by_step"
    EXAMPLE_FIRST = "example_first"


class SolutionPreference(str, Enum):
    HINT_FIRST = "hint_first"
    BALANCED = "balanced"


class StudentProfileRequest(BaseModel):
    """
    Yêu cầu khởi tạo hoặc cập nhật hồ sơ học tập của sinh viên.
    Sử dụng extra="forbid" để tuyệt đối không chấp nhận các thuộc tính cá nhân/tình cảm không liên quan.
    """
    model_config = ConfigDict(extra="forbid")

    display_name: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Tên hiển thị của sinh viên trong môi trường học tập",
    )
    programming_language: Literal["csharp"] = Field(
        default="csharp",
        description="Ngôn ngữ lập trình được hỗ trợ trong phiên bản V1 (csharp)",
    )
    skill_level: Literal["beginner"] = Field(
        default="beginner",
        description="Trình độ lập trình của sinh viên (beginner)",
    )
    current_course: Optional[str] = Field(
        default=None,
        max_length=120,
        description="Khóa học lập trình C# OOP hiện tại đang theo học",
    )
    preferred_explanation: PreferredExplanation = Field(
        default=PreferredExplanation.STEP_BY_STEP,
        description="Phong cách giải thích sư phạm mong muốn: concise, step_by_step, example_first",
    )
    solution_preference: SolutionPreference = Field(
        default=SolutionPreference.HINT_FIRST,
        description="Tùy chọn gợi ý giải pháp: hint_first, balanced",
    )

    @field_validator("display_name", "current_course")
    @classmethod
    def clean_optional_strings(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        trimmed = value.strip()
        return trimmed if trimmed else None

    @field_validator("programming_language", mode="before")
    @classmethod
    def normalize_language(cls, value: str) -> str:
        if not isinstance(value, str):
            raise ValueError("Programming language must be a string.")
        cleaned = value.strip().lower()
        if cleaned in ("c#", "cs"):
            return "csharp"
        return cleaned


class StudentProfileResponse(BaseModel):
    """
    Mô hình phản hồi hồ sơ học tập của sinh viên.
    Độc lập hoàn toàn với historical relationship schema.
    """
    model_config = ConfigDict(from_attributes=True, extra="forbid")

    id: str
    user_id: str
    display_name: Optional[str] = None
    programming_language: str
    skill_level: str
    current_course: Optional[str] = None
    preferred_explanation: str
    solution_preference: str
    created_at: datetime
    updated_at: datetime


class StudentProfileDeleteResponse(BaseModel):
    """Phản hồi sau khi xóa hồ sơ sinh viên thành công."""
    deleted: bool = True
