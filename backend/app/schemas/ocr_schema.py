from pydantic import BaseModel, Field, field_validator


class VisionOcrResponse(BaseModel):
    text: str = Field(..., min_length=1)
    confidence: float = 0.0
    warnings: list[str] = Field(default_factory=list)
    provider: str = "vision"

    @field_validator("text")
    @classmethod
    def normalize_text(cls, value: str) -> str:
        normalized = "\n".join(line.strip() for line in value.replace("\r\n", "\n").replace("\r", "\n").split("\n"))
        normalized = "\n".join(line for line in normalized.split("\n") if line)
        if not normalized:
            raise ValueError("Vision OCR text must not be empty.")
        return normalized

    @field_validator("warnings")
    @classmethod
    def normalize_warnings(cls, value: list[str]) -> list[str]:
        return [warning.strip() for warning in value if warning.strip()]
