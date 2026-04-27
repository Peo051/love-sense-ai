import asyncio
import json

import httpx
import pytest

from app.core.config import settings
from app.schemas.ocr_schema import VisionOcrResponse
from app.services.llm_client import LLMClientError, OpenAICompatibleLLMClient
from app.services.vision_ocr_service import VisionOcrService, VisionOcrServiceError


def test_vision_ocr_requires_consent(client):
    response = client.post(
        "/api/ocr/vision",
        files={"image": ("chat.png", b"fake-image", "image/png")},
        data={"is_accepted": "false"},
    )

    assert response.status_code == 400
    assert "đồng ý" in response.json()["detail"].lower()


def test_vision_ocr_rejects_non_image_file(client):
    response = client.post(
        "/api/ocr/vision",
        files={"image": ("notes.txt", b"not-image", "text/plain")},
        data={"is_accepted": "true"},
    )

    assert response.status_code == 400
    assert "png" in response.json()["detail"].lower()


def test_vision_ocr_returns_text_without_persisting_image(client, monkeypatch):
    captured = {}

    async def fake_extract(self, image_bytes: bytes, mime_type: str) -> VisionOcrResponse:
        captured["image_bytes"] = image_bytes
        captured["mime_type"] = mime_type
        return VisionOcrResponse(
            text="A: anh iu ngủ ngon nhó\nB: yeuemm",
            confidence=91,
            warnings=[],
            provider="vision",
        )

    monkeypatch.setattr(VisionOcrService, "extract_chat_text_from_image", fake_extract)

    response = client.post(
        "/api/ocr/vision",
        files={"image": ("chat.png", b"fake-image", "image/png")},
        data={"is_accepted": "true"},
    )

    assert response.status_code == 200
    assert response.json()["text"] == "A: anh iu ngủ ngon nhó\nB: yeuemm"
    assert captured == {"image_bytes": b"fake-image", "mime_type": "image/png"}


def test_vision_ocr_mock_mode_returns_clear_unavailable_reason(client, monkeypatch):
    monkeypatch.setattr(settings, "llm_mock_mode", True)
    monkeypatch.setattr(settings, "llm_provider", "openai")

    response = client.post(
        "/api/ocr/vision",
        files={"image": ("chat.png", b"fake-image", "image/png")},
        data={"is_accepted": "true"},
    )

    assert response.status_code == 503
    assert response.json()["detail"] == "AI Vision đang tắt trong cấu hình backend."


def test_vision_ocr_missing_api_key_returns_clear_configuration_error(client, monkeypatch):
    monkeypatch.setattr(settings, "llm_mock_mode", False)
    monkeypatch.setattr(settings, "llm_provider", "openai")
    monkeypatch.setattr(settings, "llm_base_url", "https://openrouter.ai/api/v1")
    monkeypatch.setattr(settings, "llm_api_key", "")
    monkeypatch.setattr(settings, "llm_model", "openai/gpt-4o-mini")
    monkeypatch.setattr(settings, "vision_ocr_model", "openai/gpt-4o-mini")

    response = client.post(
        "/api/ocr/vision",
        files={"image": ("chat.png", b"fake-image", "image/png")},
        data={"is_accepted": "true"},
    )

    assert response.status_code == 503
    assert response.json()["detail"] == "Missing LLM_API_KEY for AI Vision."


def test_vision_ocr_provider_error_is_friendly(client, monkeypatch):
    async def fake_extract(self, image_bytes: bytes, mime_type: str) -> VisionOcrResponse:
        raise VisionOcrServiceError("Vision AI chưa sẵn sàng. Vui lòng dùng OCR local hoặc nhập thủ công.")

    monkeypatch.setattr(VisionOcrService, "extract_chat_text_from_image", fake_extract)

    response = client.post(
        "/api/ocr/vision",
        files={"image": ("chat.png", b"fake-image", "image/png")},
        data={"is_accepted": "true"},
    )

    assert response.status_code == 502
    assert "OCR local" in response.json()["detail"]


def test_llm_client_vision_provider_error_is_safe(monkeypatch):
    monkeypatch.setattr(settings, "llm_mock_mode", False)
    monkeypatch.setattr(settings, "llm_provider", "openai")
    monkeypatch.setattr(settings, "llm_base_url", "https://openrouter.ai/api/v1")
    monkeypatch.setattr(settings, "llm_api_key", "test-key")
    monkeypatch.setattr(settings, "llm_model", "openai/gpt-4o-mini")
    monkeypatch.setattr(settings, "vision_ocr_model", "openai/gpt-4o-mini")
    monkeypatch.setattr(settings, "llm_max_retries", 0)

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, json={"error": {"message": "temporary provider outage"}})

    client = OpenAICompatibleLLMClient(transport=httpx.MockTransport(handler))

    with pytest.raises(LLMClientError) as exc_info:
        asyncio.run(client.extract_chat_text_from_image(b"fake-image", "image/png"))

    assert str(exc_info.value) == "LLM provider trả lỗi HTTP 500."
    assert exc_info.value.status_code == 502


def test_llm_client_vision_unsupported_model_error_is_clear(monkeypatch):
    monkeypatch.setattr(settings, "llm_mock_mode", False)
    monkeypatch.setattr(settings, "llm_provider", "openai")
    monkeypatch.setattr(settings, "llm_base_url", "https://openrouter.ai/api/v1")
    monkeypatch.setattr(settings, "llm_api_key", "test-key")
    monkeypatch.setattr(settings, "llm_model", "text-only-model")
    monkeypatch.setattr(settings, "vision_ocr_model", "text-only-model")
    monkeypatch.setattr(settings, "llm_max_retries", 0)

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(400, json={"error": {"message": "This model does not support image input."}})

    client = OpenAICompatibleLLMClient(transport=httpx.MockTransport(handler))

    with pytest.raises(LLMClientError) as exc_info:
        asyncio.run(client.extract_chat_text_from_image(b"fake-image", "image/png"))

    assert str(exc_info.value) == "Current model does not support image input."
    assert exc_info.value.status_code == 502


def test_llm_client_parses_vision_response():
    client = OpenAICompatibleLLMClient()
    result = client._parse_vision_response(
        {
            "choices": [
                {
                    "message": {
                        "content": json.dumps(
                            {
                                "text": "A: anh iu ngủ ngon nhó\nB: yeuemm",
                                "confidence": 121,
                                "warnings": [],
                            },
                            ensure_ascii=False,
                        )
                    }
                }
            ]
        }
    )

    assert result.text == "A: anh iu ngủ ngon nhó\nB: yeuemm"
    assert result.confidence == 100
    assert result.provider == "vision"


def test_llm_client_sends_vision_payload_without_exposing_key(monkeypatch):
    monkeypatch.setattr(settings, "llm_base_url", "http://localhost:20128/v1")
    monkeypatch.setattr(settings, "llm_api_key", "local-test-key")
    monkeypatch.setattr(settings, "llm_model", "api_models_all")
    monkeypatch.setattr(settings, "vision_ocr_model", "")
    monkeypatch.setattr(settings, "llm_max_retries", 0)
    captured_payload = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured_payload.update(json.loads(request.content.decode("utf-8")))
        return httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "message": {
                            "content": json.dumps(
                                {"text": "A: hello\nB: hi", "confidence": 80, "warnings": []},
                                ensure_ascii=False,
                            )
                        }
                    }
                ]
            },
        )

    client = OpenAICompatibleLLMClient(transport=httpx.MockTransport(handler))
    result = asyncio.run(client.extract_chat_text_from_image(b"fake-image", "image/png"))

    assert result.text == "A: hello\nB: hi"
    assert captured_payload["model"] == "api_models_all"
    content = captured_payload["messages"][1]["content"]
    assert content[1]["image_url"]["url"].startswith("data:image/png;base64,")
    assert "local-test-key" not in json.dumps(captured_payload)
