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
        description="Chỉ lưu nội dung chat nếu người dùng đồng ý rõ ràng.",
    )
    save_result: bool = Field(
        default=False,
        description="Lưu kết quả tổng hợp vào lịch sử nếu người dùng đồng ý.",
    )


class AnalyzeResponse(BaseModel):
    overall_emotion: str
    confidence: float
    emotion_distribution: dict[str, float]
    summary: str
    context_note: str
    suggested_reply: str
    warning: str
    tone: str | None = Field(
        default=None,
        description="Sắc thái giao tiếp nổi bật, ví dụ thân mật, trêu đùa, mệt mỏi hoặc giận dỗi.",
    )
    evidence: list[str] = Field(
        default_factory=list,
        description="Một vài câu trong đoạn chat làm căn cứ cho nhận định. Không dùng để kết luận chắc chắn.",
    )
    uncertainty_reasons: list[str] = Field(
        default_factory=list,
        description="Các lý do cần thận trọng khi đọc kết quả, nhất là khi input ngắn hoặc đến từ OCR.",
    )
    input_quality: str = Field(
        default="medium",
        description="Đánh giá chất lượng đầu vào: good, medium hoặc low.",
    )
    reply_style: str | None = Field(
        default=None,
        description="Phong cách phản hồi nên dùng dựa trên sắc thái hội thoại.",
    )
