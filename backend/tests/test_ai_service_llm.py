import asyncio
import json

import httpx
import pytest

from app.core.config import settings
from app.schemas.analyze_schema import AnalyzeResponse
from app.services.ai_service import AIService
from app.services.analysis_policy import WARNING_MESSAGE
from app.services.llm_client import LLMClientError, OpenAICompatibleLLMClient


class FakeLLMClient:
    def __init__(self):
        self.called = False

    async def analyze_emotion(self, chat_text: str, profile_context: str = "") -> AnalyzeResponse:
        self.called = True
        return AnalyzeResponse(
            overall_emotion="LLM result",
            confidence=0.8,
            emotion_distribution={"trung_lập": 1.0},
            summary=f"Analyzed: {chat_text}",
            context_note=profile_context,
            suggested_reply="Phản hồi nhẹ nhàng.",
            warning=WARNING_MESSAGE,
        )


class FailingLLMClient:
    async def analyze_emotion(self, chat_text: str, profile_context: str = "") -> AnalyzeResponse:
        raise LLMClientError("provider is unavailable")


def test_ai_service_uses_mock_by_default(monkeypatch):
    monkeypatch.setattr(settings, "llm_mock_mode", True)
    monkeypatch.setattr(settings, "llm_provider", "mock")
    fake_client = FakeLLMClient()

    result = asyncio.run(AIService(llm_client=fake_client).analyze_emotion("Em mệt thôi."))

    assert fake_client.called is False
    assert result.overall_emotion == "mệt mỏi / né tránh nhẹ"


def test_ai_service_uses_llm_when_mock_mode_is_disabled(monkeypatch):
    monkeypatch.setattr(settings, "llm_mock_mode", False)
    monkeypatch.setattr(settings, "llm_provider", "9router")
    fake_client = FakeLLMClient()

    result = asyncio.run(AIService(llm_client=fake_client).analyze_emotion("Tin nhắn cần phân tích."))

    assert fake_client.called is True
    assert result.overall_emotion == "LLM result"


def test_ai_service_falls_back_to_mock_when_llm_fails(monkeypatch):
    monkeypatch.setattr(settings, "llm_mock_mode", False)
    monkeypatch.setattr(settings, "llm_provider", "9router")

    result = asyncio.run(AIService(llm_client=FailingLLMClient()).analyze_emotion("Em mệt thôi."))

    assert result.overall_emotion == "mệt mỏi / né tránh nhẹ"


def test_ai_service_falls_back_when_llm_configuration_is_missing(monkeypatch):
    monkeypatch.setattr(settings, "llm_mock_mode", False)
    monkeypatch.setattr(settings, "llm_provider", "9router")
    monkeypatch.setattr(settings, "llm_base_url", "http://localhost:20128/v1")
    monkeypatch.setattr(settings, "llm_api_key", "")
    monkeypatch.setattr(settings, "llm_model", "api_models_all")

    result = asyncio.run(AIService().analyze_emotion("Em mệt thôi."))

    assert result.overall_emotion == "mệt mỏi / né tránh nhẹ"
    assert "tham khảo" in result.warning.lower()


def test_ai_service_falls_back_to_mock_when_llm_times_out(monkeypatch):
    monkeypatch.setattr(settings, "llm_mock_mode", False)
    monkeypatch.setattr(settings, "llm_provider", "9router")
    monkeypatch.setattr(settings, "llm_base_url", "http://localhost:20128/v1")
    monkeypatch.setattr(settings, "llm_api_key", "local-test-key")
    monkeypatch.setattr(settings, "llm_model", "api_models_all")
    monkeypatch.setattr(settings, "llm_max_retries", 0)

    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("request timed out", request=request)

    client = OpenAICompatibleLLMClient(transport=httpx.MockTransport(handler))
    result = asyncio.run(AIService(llm_client=client).analyze_emotion("Em mệt thôi."))

    assert result.overall_emotion == "mệt mỏi / né tránh nhẹ"
    assert "tham khảo" in result.warning.lower()


def test_llm_client_retries_temporary_error_then_succeeds(monkeypatch):
    monkeypatch.setattr(settings, "llm_base_url", "http://localhost:20128/v1")
    monkeypatch.setattr(settings, "llm_api_key", "local-test-key")
    monkeypatch.setattr(settings, "llm_model", "api_models_all")
    monkeypatch.setattr(settings, "llm_max_retries", 2)
    monkeypatch.setattr(settings, "llm_retry_base_delay_seconds", 0)
    attempts = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            return httpx.Response(503, json={"error": "temporary unavailable"})
        return _llm_success_response()

    client = OpenAICompatibleLLMClient(transport=httpx.MockTransport(handler))
    result = asyncio.run(client.analyze_emotion("Tin nhắn cần phân tích."))

    assert attempts == 2
    assert result.overall_emotion == "LLM result"


def test_llm_client_does_not_retry_invalid_schema(monkeypatch):
    monkeypatch.setattr(settings, "llm_base_url", "http://localhost:20128/v1")
    monkeypatch.setattr(settings, "llm_api_key", "local-test-key")
    monkeypatch.setattr(settings, "llm_model", "api_models_all")
    monkeypatch.setattr(settings, "llm_max_retries", 2)
    attempts = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1
        return httpx.Response(200, json={"choices": [{"message": {"content": "not json"}}]})

    client = OpenAICompatibleLLMClient(transport=httpx.MockTransport(handler))

    with pytest.raises(LLMClientError, match="JSON hợp lệ"):
        asyncio.run(client.analyze_emotion("Tin nhắn cần phân tích."))

    assert attempts == 1


def test_ai_service_falls_back_after_retry_exhausted(monkeypatch):
    monkeypatch.setattr(settings, "llm_mock_mode", False)
    monkeypatch.setattr(settings, "llm_provider", "9router")
    monkeypatch.setattr(settings, "llm_base_url", "http://localhost:20128/v1")
    monkeypatch.setattr(settings, "llm_api_key", "local-test-key")
    monkeypatch.setattr(settings, "llm_model", "api_models_all")
    monkeypatch.setattr(settings, "llm_max_retries", 2)
    monkeypatch.setattr(settings, "llm_retry_base_delay_seconds", 0)
    attempts = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1
        return httpx.Response(503, json={"error": "temporary unavailable"})

    client = OpenAICompatibleLLMClient(transport=httpx.MockTransport(handler))
    result = asyncio.run(AIService(llm_client=client).analyze_emotion("Em mệt thôi."))

    assert attempts == 3
    assert result.overall_emotion == "mệt mỏi / né tránh nhẹ"


def test_llm_client_requires_api_configuration(monkeypatch):
    monkeypatch.setattr(settings, "llm_base_url", "http://localhost:20128/v1")
    monkeypatch.setattr(settings, "llm_api_key", "")
    monkeypatch.setattr(settings, "llm_model", "api_models_all")

    with pytest.raises(LLMClientError, match="LLM_API_KEY"):
        asyncio.run(OpenAICompatibleLLMClient().analyze_emotion("Tin nhắn cần phân tích."))


def test_llm_client_error_does_not_expose_api_key(monkeypatch):
    secret_key = "local-test-secret-key"
    monkeypatch.setattr(settings, "llm_base_url", "http://localhost:20128/v1")
    monkeypatch.setattr(settings, "llm_api_key", secret_key)
    monkeypatch.setattr(settings, "llm_model", "api_models_all")
    monkeypatch.setattr(settings, "llm_max_retries", 2)

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(401, json={"error": "unauthorized"})

    client = OpenAICompatibleLLMClient(transport=httpx.MockTransport(handler))

    with pytest.raises(LLMClientError) as exc_info:
        asyncio.run(client.analyze_emotion("Tin nhắn cần phân tích."))

    assert secret_key not in str(exc_info.value)
    assert "401" in str(exc_info.value)


def test_llm_client_normalizes_warning_from_provider():
    client = OpenAICompatibleLLMClient()
    result = client._parse_response(
        {
            "choices": [
                {
                    "message": {
                        "content": """
                        {
                          "overall_emotion": "trung lập",
                          "confidence": 1.4,
                          "emotion_distribution": {"trung_lập": 1.2},
                          "summary": "Tóm tắt an toàn.",
                          "context_note": "Không dùng dữ liệu ngoại hình để suy luận.",
                          "suggested_reply": "Mình nói chuyện thêm khi em sẵn sàng nhé.",
                          "warning": "missing"
                        }
                        """
                    }
                }
            ]
        }
    )

    assert result.confidence == 1.0
    assert result.emotion_distribution["trung_lập"] == 1.0
    assert result.warning == WARNING_MESSAGE


def _llm_success_response() -> httpx.Response:
    content = {
        "overall_emotion": "LLM result",
        "confidence": 0.8,
        "emotion_distribution": {"trung_lập": 1.0},
        "summary": "Tóm tắt an toàn.",
        "context_note": "Bối cảnh được dùng ở mức tham khảo.",
        "suggested_reply": "Mình nói chuyện thêm khi em sẵn sàng nhé.",
        "warning": WARNING_MESSAGE,
    }
    return httpx.Response(
        200,
        json={"choices": [{"message": {"content": json.dumps(content, ensure_ascii=False)}}]},
    )
