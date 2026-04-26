from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    chat_text: str = Field(
        ...,
        min_length=1,
        max_length=8000,
        description="Đoạn hội thoại người dùng nhập thủ công.",
    )
    profile_context: str = Field(
        default="",
        max_length=3000,
        description="Bối cảnh cá nhân hóa như sở thích, phong cách giao tiếp, cách phản ứng.",
    )
    save_input: bool = Field(
        default=False,
        description="MVP chưa lưu dữ liệu; trường này giữ để chuẩn bị cho tính năng lưu có đồng ý.",
    )


class AnalyzeResponse(BaseModel):
    overall_emotion: str
    confidence: float
    emotion_distribution: dict[str, float]
    summary: str
    context_note: str
    suggested_reply: str
    warning: str
