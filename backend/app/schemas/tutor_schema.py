from datetime import datetime
from enum import Enum, IntEnum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class HintLevel(IntEnum):
    """
    Cấp độ gợi ý sư phạm:
    - SOCRATIC_QUESTION = 1: Câu hỏi gợi mở Socratic, định hướng tư duy tổng quan.
    - CONCEPTUAL_EXPLANATION = 2: Giải thích khái niệm/nguyên lý OOP liên quan và manh mối logic.
    - DIRECTED_HINT = 3: Gợi ý có định hướng từng bước (không đưa mã giải hoàn chỉnh).
    - EXPLICIT_SOLUTION = 4: Giải pháp rõ ràng kèm mã sửa lỗi cụ thể (chỉ khi được cấu hình).
    """
    SOCRATIC_QUESTION = 1
    CONCEPTUAL_EXPLANATION = 2
    DIRECTED_HINT = 3
    EXPLICIT_SOLUTION = 4

    # Aliases tương thích ngược
    POINTING = 1
    CONCEPTUAL = 2
    CONCRETE = 3


class IssueSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class TutorDiagnosis(BaseModel):
    """
    Kết quả chẩn đoán kỹ thuật về bài làm của sinh viên.
    """
    issue_type: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Loại lỗi (ví dụ: syntax_error, semantic_error, logical_error, conceptual_misconception, oop_design_flaw, none)",
    )
    severity: str = Field(
        default="warning",
        description="Mức độ nghiêm trọng của vấn đề (info, warning, error)",
    )
    location: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Vị trí trong mã nguồn sinh viên (ví dụ: dòng code, tên method, tên class)",
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Độ tin cậy của chẩn đoán (thang điểm 0.0 - 1.0)",
    )

    @field_validator("issue_type", "severity")
    @classmethod
    def strip_and_lower(cls, value: str) -> str:
        trimmed = value.strip().lower()
        if not trimmed:
            raise ValueError("Field must not be empty.")
        return trimmed

    @field_validator("location")
    @classmethod
    def clean_location(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        trimmed = value.strip()
        return trimmed if trimmed else None


class PossibleMisconception(BaseModel):
    """
    Giả thuyết về ngộ nhận có thể có trong tư duy lập trình OOP của sinh viên.
    NGUYÊN TẮC SƯ PHẠM: Không gán định đoạt trạng thái nhận thức hay khả năng của sinh viên;
    luôn biểu diễn dưới dạng giả thuyết có thể xảy ra (possible misconception semantics).
    """
    type: str = Field(
        ...,
        min_length=1,
        max_length=120,
        description="Mã phân loại ngộ nhận (ví dụ: method_confused_with_constructor, scope_misunderstanding, encapsulation_bypass)",
    )
    description: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Mô tả ngộ nhận có thể có dựa trên bằng chứng đoạn mã",
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Độ tin cậy của giả thuyết ngộ nhận (thang điểm 0.0 - 1.0)",
    )

    @field_validator("type")
    @classmethod
    def strip_type(cls, value: str) -> str:
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("Misconception type must not be empty.")
        return trimmed

    @field_validator("description")
    @classmethod
    def clean_description(cls, value: str) -> str:
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("Misconception description must not be empty.")
        return trimmed


class TutorEvidence(BaseModel):
    """
    Bằng chứng cụ thể trích từ mã nguồn của sinh viên kèm lý giải sư phạm.
    """
    code: str = Field(
        ...,
        max_length=5000,
        description="Đoạn mã thể hiện vấn đề hoặc ngộ nhận",
    )
    reason: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Lý giải nguyên nhân đoạn mã thể hiện vấn đề",
    )

    @field_validator("code")
    @classmethod
    def clean_code(cls, value: str) -> str:
        return value.strip()

    @field_validator("reason")
    @classmethod
    def clean_reason(cls, value: str) -> str:
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("Evidence reason must not be empty.")
        return trimmed


class TutorResponse(BaseModel):
    """
    Mô hình phản hồi có cấu trúc từ AI Tutor cho sinh viên học C# OOP.
    """
    diagnosis: TutorDiagnosis = Field(
        ...,
        description="Chẩn đoán kỹ thuật về bài làm",
    )
    knowledge_components: list[str] = Field(
        default_factory=list,
        description="Danh sách các thành phần kiến thức OOP liên quan",
    )
    possible_misconception: Optional[PossibleMisconception] = Field(
        default=None,
        description="Giả định ngộ nhận có thể có của sinh viên",
    )
    evidence: Optional[TutorEvidence] = Field(
        default=None,
        description="Bằng chứng từ mã nguồn của sinh viên",
    )
    teaching_strategy: str = Field(
        ...,
        min_length=1,
        max_length=120,
        description="Chiến lược sư phạm được áp dụng (ví dụ: socratic_questioning, progressive_hinting, worked_example_analogy)",
    )
    tutor_response: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="Nội dung hướng dẫn sư phạm dành cho sinh viên",
    )
    hint_level: int = Field(
        default=1,
        ge=1,
        le=4,
        description="Mức độ gợi ý của phản hồi (1: Socratic question, 2: Conceptual explanation, 3: Directed hint, 4: Explicit solution)",
    )
    solution_revealed: bool = Field(
        default=False,
        description="Đánh dấu phản hồi có đưa ra mã giải trọn vẹn hay không (chỉ được phép khi hint_level = 4)",
    )
    next_action: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Hành động cụ thể gợi ý cho sinh viên thực hiện tiếp theo",
    )
    prompt_version: str = Field(
        default="v1",
        description="Phiên bản prompt được áp dụng để sinh phản hồi",
    )
    session_id: Optional[str] = Field(
        default=None,
        description="ID phiên hướng dẫn nếu được lưu trữ",
    )
    created_at: Optional[datetime] = Field(
        default=None,
        description="Thời điểm tạo phản hồi",
    )

    @field_validator("knowledge_components")
    @classmethod
    def clean_knowledge_components(cls, value: list[str]) -> list[str]:
        cleaned = [item.strip() for item in value if item and item.strip()]
        return cleaned

    @field_validator("teaching_strategy", "tutor_response", "next_action")
    @classmethod
    def clean_text_fields(cls, value: str) -> str:
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("Field must not be empty or whitespace only.")
        return trimmed


# Alias để tương thích tên gọi
TutorFeedbackResponse = TutorResponse


class TutorRequest(BaseModel):
    """
    Mô hình yêu cầu hướng dẫn học tập lập trình C# OOP gửi đến AI Tutor.
    """
    problem_statement: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="Nội dung đề bài bài tập lập trình",
    )
    student_code: str = Field(
        ...,
        min_length=1,
        max_length=20000,
        description="Mã nguồn C# hiện tại của sinh viên",
    )
    programming_language: str = Field(
        default="csharp",
        description="Ngôn ngữ lập trình (Phiên bản V1 chỉ hỗ trợ 'csharp')",
    )
    compiler_error: Optional[str] = Field(
        default=None,
        max_length=10000,
        description="Thông báo lỗi biên dịch từ compiler (nếu có)",
    )
    student_question: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Câu hỏi hoặc thắc mắc cụ thể của sinh viên (nếu có)",
    )
    topic: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Chủ đề OOP (ví dụ: class_object, encapsulation, inheritance, polymorphism, abstraction)",
    )
    hint_level: int = Field(
        default=1,
        ge=1,
        le=4,
        description="Mức độ gợi ý yêu cầu (1: Socratic question, 2: Conceptual explanation, 3: Directed hint, 4: Explicit solution)",
    )
    save_input: bool = Field(
        default=False,
        description="Đồng ý lưu mã nguồn bài làm vào lịch sử",
    )
    save_result: bool = Field(
        default=True,
        description="Đồng ý lưu kết quả hướng dẫn vào lịch sử",
    )

    @field_validator("programming_language")
    @classmethod
    def validate_language(cls, value: str) -> str:
        normalized = value.strip().lower()
        if normalized in ("csharp", "cs", "c#"):
            return "csharp"
        raise ValueError(
            f"Unsupported programming language '{value}'. Version 1 of Adaptive Programming Tutor only supports 'csharp'."
        )

    @field_validator("problem_statement")
    @classmethod
    def validate_problem_statement(cls, value: str) -> str:
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("Problem statement must not be empty or contain only whitespace.")
        return trimmed

    @field_validator("student_code")
    @classmethod
    def validate_student_code(cls, value: str) -> str:
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("Student code must not be empty or contain only whitespace.")
        return trimmed

    @field_validator("compiler_error", "student_question", "topic")
    @classmethod
    def clean_optional_strings(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        trimmed = value.strip()
        return trimmed if trimmed else None

    @model_validator(mode="after")
    def validate_input_combinations(self) -> "TutorRequest":
        if len(self.problem_statement) < 5:
            raise ValueError("Problem statement is too short to provide meaningful context (minimum 5 characters).")
        return self


# Alias để tương thích tên gọi
TutorFeedbackRequest = TutorRequest
