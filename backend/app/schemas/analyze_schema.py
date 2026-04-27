from pydantic import BaseModel, Field, field_validator


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


class EvidenceItem(BaseModel):
    quote: str
    label: str
    reason: str


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
    evidence: list[EvidenceItem] = Field(
        default_factory=list,
        description="Các câu trong đoạn chat làm căn cứ tham khảo cho từng nhận định quan trọng.",
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

    @field_validator("evidence", mode="before")
    @classmethod
    def normalize_evidence(cls, value):
        if not value:
            return []

        if not isinstance(value, list):
            return []

        normalized_items: list[dict[str, str]] = []
        for item in value:
            if isinstance(item, EvidenceItem):
                quote = item.quote.strip()
                label = item.label.strip() or "tín hiệu hội thoại"
                reason = item.reason.strip() or "Câu này được dùng làm căn cứ tham khảo cho phân tích."
                if quote:
                    normalized_items.append({"quote": quote, "label": label, "reason": reason})
                continue

            if isinstance(item, str):
                cleaned_quote = item.strip()
                if cleaned_quote:
                    normalized_items.append(
                        {
                            "quote": cleaned_quote,
                            "label": "tín hiệu hội thoại",
                            "reason": "Câu này được dùng làm căn cứ tham khảo cho phân tích.",
                        }
                    )
                continue

            if isinstance(item, dict):
                quote = str(item.get("quote", "")).strip()
                label = str(item.get("label", "")).strip() or "tín hiệu hội thoại"
                reason = str(item.get("reason", "")).strip() or "Câu này được dùng làm căn cứ tham khảo cho phân tích."
                if quote:
                    normalized_items.append({"quote": quote, "label": label, "reason": reason})

        return normalized_items
