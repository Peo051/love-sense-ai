import asyncio
import json

import httpx

from app.core.config import settings
from app.schemas.analyze_schema import AnalyzeResponse
from app.services.analysis_output_validator import validate_analysis_output
from app.services.analysis_policy import WARNING_MESSAGE
from app.services.llm_client import OpenAICompatibleLLMClient


def build_result(**overrides) -> AnalyzeResponse:
    payload = {
        "overall_emotion": "mệt mỏi / né tránh nhẹ",
        "confidence": 0.82,
        "emotion_distribution": {"mệt_mỏi": 0.7, "trung_lập": 0.3},
        "summary": "Đoạn chat có dấu hiệu mệt mỏi nhẹ.",
        "context_note": "Bối cảnh chỉ dùng để tham khảo.",
        "suggested_reply": "Em nghỉ một chút nha, khi nào muốn nói anh vẫn ở đây nghe em.",
        "warning": WARNING_MESSAGE,
        "tone": "mệt mỏi",
        "evidence": [
            {
                "quote": "Em mệt thôi.",
                "label": "mệt mỏi",
                "reason": "Câu này nói trực tiếp về trạng thái mệt.",
            }
        ],
        "uncertainty_reasons": [],
        "input_quality": "good",
        "reply_style": "nhẹ nhàng",
    }
    payload.update(overrides)
    return AnalyzeResponse.model_validate(payload)


def test_validator_fills_required_text_fields_and_warning():
    result = validate_analysis_output(
        build_result(
            overall_emotion="",
            summary="",
            context_note="",
            suggested_reply="",
            warning="missing",
        ),
        "A: Em sao vậy?\nB: Em mệt thôi.",
    )

    assert result.overall_emotion
    assert result.summary
    assert result.context_note
    assert result.suggested_reply
    assert result.warning == WARNING_MESSAGE


def test_validator_normalizes_string_evidence_to_supported_object():
    result = validate_analysis_output(
        build_result(evidence=["Em mệt thôi"]),
        "A: Em sao vậy?\nB: Em mệt thôi.",
    )

    assert len(result.evidence) == 1
    assert result.evidence[0].quote == "Em mệt thôi"
    assert result.evidence[0].label
    assert result.evidence[0].reason


def test_validator_drops_unsupported_evidence_and_caps_confidence():
    result = validate_analysis_output(
        build_result(confidence=0.95, evidence=[{"quote": "Câu không có trong đoạn chat", "label": "mệt", "reason": "Sai."}]),
        "A: Em sao vậy?\nB: Em mệt thôi.",
    )

    assert result.evidence == []
    assert result.confidence <= 0.6
    assert any("Không có câu làm căn cứ" in reason for reason in result.uncertainty_reasons)


def test_validator_caps_confidence_for_short_chat():
    result = validate_analysis_output(
        build_result(confidence=0.95, evidence=["ok"]),
        "ok",
    )

    assert result.confidence <= 0.45
    assert result.input_quality == "low"


def test_validator_caps_confidence_for_low_quality_ocr_context():
    result = validate_analysis_output(
        build_result(confidence=0.95),
        "A: Em sao vậy?\nB: Em mệt thôi.",
        "Cảnh báo OCR: OCR nhận diện quá ít nội dung, vui lòng kiểm tra lại.",
    )

    assert result.confidence <= 0.65
    assert result.input_quality == "low"


def test_validator_rewrites_unsafe_claims():
    result = validate_analysis_output(
        build_result(
            overall_emotion="chắc chắn hết yêu",
            summary="Người này chắc chắn phản bội.",
            suggested_reply="Em đang lừa dối anh đúng không?",
            tone="chắc chắn lừa dối",
            evidence=[{"quote": "Em mệt thôi.", "label": "chắc chắn hết yêu", "reason": "phản bội"}],
        ),
        "A: Em sao vậy?\nB: Em mệt thôi.",
    )

    combined_output = " ".join(
        [
            result.overall_emotion,
            result.summary,
            result.suggested_reply,
            result.tone or "",
            *(item.label for item in result.evidence),
            *(item.reason for item in result.evidence),
        ]
    ).lower()

    assert "hết yêu" not in combined_output
    assert "phản bội" not in combined_output
    assert "lừa dối" not in combined_output
    assert "chắc chắn" not in combined_output


def test_validator_normalizes_distribution_keys_and_total():
    result = validate_analysis_output(
        build_result(emotion_distribution={"mệt_mỏi": 2, "trung lập": 1, "khó chịu": -3}),
        "A: Em sao vậy?\nB: Em mệt thôi.",
    )

    assert "met_moi" in result.emotion_distribution
    assert "trung_lap" in result.emotion_distribution
    assert "mệt_mỏi" not in result.emotion_distribution
    assert "than_mat" in result.emotion_distribution
    assert abs(sum(result.emotion_distribution.values()) - 1.0) < 0.0001


def test_llm_client_validates_provider_output(monkeypatch):
    monkeypatch.setattr(settings, "llm_base_url", "http://localhost:20128/v1")
    monkeypatch.setattr(settings, "llm_api_key", "local-test-key")
    monkeypatch.setattr(settings, "llm_model", "api_models_all")

    content = {
        "overall_emotion": "chắc chắn hết yêu",
        "confidence": 0.99,
        "emotion_distribution": {"mệt_mỏi": 2, "trung_lập": 1},
        "summary": "Người này chắc chắn phản bội.",
        "context_note": "Bối cảnh tham khảo.",
        "suggested_reply": "Em đang lừa dối anh đúng không?",
        "warning": "missing",
        "evidence": [{"quote": "Không có trong chat", "label": "mệt", "reason": "Sai."}],
    }

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={"choices": [{"message": {"content": json.dumps(content, ensure_ascii=False)}}]},
        )

    client = OpenAICompatibleLLMClient(transport=httpx.MockTransport(handler))
    result = asyncio.run(
        client.analyze_emotion("ok", "Cảnh báo OCR: OCR nhận diện quá ít nội dung.")
    )

    assert result.overall_emotion == "chưa đủ dữ liệu"
    assert result.confidence <= 0.45
    assert result.evidence == []
    assert result.warning == WARNING_MESSAGE
