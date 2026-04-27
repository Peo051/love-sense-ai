import asyncio

from app.services.ai_service import AIService


def analyze(chat_text: str, profile_context: str = ""):
    return asyncio.run(AIService().analyze_emotion(chat_text, profile_context))


def test_affectionate_teasing_chat_is_not_classified_as_plain_neutral():
    result = analyze(
        "\n".join(
            [
                "A: anh iu ngủ ngon nhó",
                "A: yeuu anh 🥺",
                "B: khong thích ấy",
                "B: Không thích ngủ ngon",
                "B: Thích ngủ cà dựt cà dựt",
                "B: Ngủ bị mộng du qua ôm bé được hong",
                "B: yeuemm 🥺",
            ]
        ),
        "Nội dung đoạn chat được trích xuất từ ảnh OCR, có thể có lỗi nhận diện.",
    )

    normalized_emotion = result.overall_emotion.lower()

    assert any(keyword in normalized_emotion for keyword in ["thân mật", "trêu đùa", "quan tâm"])
    assert "trung lập" not in normalized_emotion
    assert result.confidence >= 0.6
    assert result.evidence
    assert result.evidence[0].quote
    assert result.evidence[0].label
    assert result.evidence[0].reason
    assert result.input_quality in {"medium", "good"}


def test_fatigue_chat_keeps_fatigue_and_light_avoidance_signal():
    result = analyze("A: Em sao vậy?\nB: Em mệt thôi.\nB: Mai nói nha.")

    normalized_emotion = result.overall_emotion.lower()

    assert "mệt" in normalized_emotion
    assert "né tránh" in normalized_emotion
    assert result.confidence >= 0.65
    assert result.evidence


def test_sulking_chat_detects_light_irritation():
    result = analyze("B: ừ sao cũng được\nB: anh muốn làm gì thì làm")

    normalized_emotion = result.overall_emotion.lower()

    assert any(keyword in normalized_emotion for keyword in ["khó chịu", "giận dỗi"])
    assert result.confidence >= 0.6
    assert result.evidence


def test_short_chat_returns_low_confidence_insufficient_data():
    result = analyze("ok")

    assert "chưa đủ dữ liệu" in result.overall_emotion.lower()
    assert result.confidence < 0.4
    assert result.input_quality != "good"
    assert result.uncertainty_reasons
