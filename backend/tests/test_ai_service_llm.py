import asyncio
import json

import httpx
import pytest

from app.core.config import settings
from app.services.ai_service import AIService
from app.services.llm_client import LLMClientError, OpenAICompatibleLLMClient


def test_llm_client_chat_completion_success(monkeypatch):
    monkeypatch.setattr(settings, "llm_base_url", "http://localhost:20128/v1")
    monkeypatch.setattr(settings, "llm_api_key", "local-test-key")
    monkeypatch.setattr(settings, "llm_model", "api_models_all")

    def handler(request: httpx.Request) -> httpx.Response:
        data = json.loads(request.content)
        assert data["model"] == "api_models_all"
        assert len(data["messages"]) == 1
        return httpx.Response(
            200,
            json={"choices": [{"message": {"content": "Gợi ý: Hãy kiểm tra access modifier của thuộc tính."}}]},
        )

    client = OpenAICompatibleLLMClient(transport=httpx.MockTransport(handler))
    result = asyncio.run(
        client.chat_completion(
            [{"role": "user", "content": "Làm sao bảo vệ dữ liệu trong class C#?"}]
        )
    )

    assert "access modifier" in result


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
        return httpx.Response(
            200,
            json={"choices": [{"message": {"content": "Phản hồi thành công ở lần 2."}}]},
        )

    client = OpenAICompatibleLLMClient(transport=httpx.MockTransport(handler))
    result = asyncio.run(
        client.chat_completion([{"role": "user", "content": "Câu hỏi lập trình"}])
    )

    assert attempts == 2
    assert "lần 2" in result


def test_llm_client_requires_api_configuration(monkeypatch):
    monkeypatch.setattr(settings, "llm_base_url", "http://localhost:20128/v1")
    monkeypatch.setattr(settings, "llm_api_key", "")
    monkeypatch.setattr(settings, "llm_model", "api_models_all")

    with pytest.raises(LLMClientError, match="LLM_API_KEY"):
        asyncio.run(
            OpenAICompatibleLLMClient().chat_completion([{"role": "user", "content": "Test"}])
        )


def test_llm_client_error_does_not_expose_api_key(monkeypatch):
    secret_key = "local-test-secret-key"
    monkeypatch.setattr(settings, "llm_base_url", "http://localhost:20128/v1")
    monkeypatch.setattr(settings, "llm_api_key", secret_key)
    monkeypatch.setattr(settings, "llm_model", "api_models_all")
    monkeypatch.setattr(settings, "llm_max_retries", 1)

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(401, json={"error": "unauthorized"})

    client = OpenAICompatibleLLMClient(transport=httpx.MockTransport(handler))

    with pytest.raises(LLMClientError) as exc_info:
        asyncio.run(client.chat_completion([{"role": "user", "content": "Test"}]))

    assert secret_key not in str(exc_info.value)
    assert "401" in str(exc_info.value)


def test_llm_client_times_out(monkeypatch):
    monkeypatch.setattr(settings, "llm_base_url", "http://localhost:20128/v1")
    monkeypatch.setattr(settings, "llm_api_key", "local-test-key")
    monkeypatch.setattr(settings, "llm_model", "api_models_all")
    monkeypatch.setattr(settings, "llm_max_retries", 0)

    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("request timed out", request=request)

    client = OpenAICompatibleLLMClient(transport=httpx.MockTransport(handler))

    with pytest.raises(LLMClientError, match="thời gian chờ"):
        asyncio.run(client.chat_completion([{"role": "user", "content": "Test"}]))


def test_ai_service_generates_response():
    class MockClient:
        async def chat_completion(self, messages, **kwargs):
            return f"Echo: {messages[0]['content']}"

    service = AIService(llm_client=MockClient())
    response = asyncio.run(service.generate_response([{"role": "user", "content": "Hello"}]))
    assert response == "Echo: Hello"

