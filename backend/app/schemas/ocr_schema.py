from typing import Optional
from pydantic import BaseModel, Field, field_validator, model_validator


class VisionOcrResponse(BaseModel):
    text: str = Field(default="")
    problem_statement: Optional[str] = None
    student_code: Optional[str] = None
    compiler_error: Optional[str] = None
    confidence: float = 0.0
    warnings: list[str] = Field(default_factory=list)
    provider: str = "vision"

    @field_validator("problem_statement", "compiler_error", mode="before")
    @classmethod
    def normalize_optional_text(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        normalized = "\n".join(line.strip() for line in str(value).replace("\r\n", "\n").replace("\r", "\n").split("\n"))
        normalized = normalized.strip()
        return normalized if normalized else None

    @field_validator("student_code", mode="before")
    @classmethod
    def normalize_student_code(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        # Preserve inner indentation, normalize line breaks, strip outer whitespace
        lines = str(value).replace("\r\n", "\n").replace("\r", "\n").split("\n")
        while lines and not lines[0].strip():
            lines.pop(0)
        while lines and not lines[-1].strip():
            lines.pop()
        if not lines:
            return None
        return "\n".join(lines)

    @field_validator("text", mode="before")
    @classmethod
    def normalize_text(cls, value: Optional[str]) -> str:
        if value is None:
            return ""
        normalized = str(value).replace("\r\n", "\n").replace("\r", "\n").strip()
        return normalized

    @field_validator("warnings", mode="before")
    @classmethod
    def normalize_warnings(cls, value: list[str]) -> list[str]:
        if not isinstance(value, list):
            return []
        return [str(warning).strip() for warning in value if str(warning).strip()]

    @model_validator(mode="after")
    def populate_and_validate_content(self) -> "VisionOcrResponse":
        # If text is empty but candidate fields are provided, assemble text from candidates
        if not self.text.strip():
            parts = []
            if self.problem_statement:
                parts.append(f"Đề bài:\n{self.problem_statement}")
            if self.student_code:
                parts.append(f"Mã nguồn C#:\n{self.student_code}")
            if self.compiler_error:
                parts.append(f"Lỗi biên dịch:\n{self.compiler_error}")
            if parts:
                self.text = "\n\n".join(parts)

        if not self.text.strip() and not (self.problem_statement or self.student_code or self.compiler_error):
            raise ValueError("Vision OCR text must not be empty.")

        self.confidence = max(0.0, min(100.0, float(self.confidence)))
        return self
