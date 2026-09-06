import pytest
from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import app
from app.routes.tutor import get_tutor_service
from app.tutor.provider import DeterministicMockTutorProvider, TutorProviderError
from app.tutor.service import TutorService


def sample_request_payload(hint_level: int = 1, save_input: bool = False, save_result: bool = True):
    return {
        "problem_statement": "Xây dựng lớp Rectangle có chiều dài, chiều rộng và hàm tính diện tích Area().",
        "student_code": "public class Rectangle { public int W; public int H; public int Area() { return W * H; } }",
        "programming_language": "csharp",
        "compiler_error": None,
        "student_question": "Em viết hàm Area() như vậy đã chuẩn OOP chưa?",
        "topic": "encapsulation",
        "hint_level": hint_level,
        "save_input": save_input,
        "save_result": save_result,
    }


@pytest.fixture
def mock_tutor_service():
    provider = DeterministicMockTutorProvider()
    service = TutorService(llm_provider=provider)
    app.dependency_overrides[get_tutor_service] = lambda: service
    yield service
    app.dependency_overrides.pop(get_tutor_service, None)


class TestTutorAnalyzeAPI:
    def test_successful_analysis_with_mocked_llm(self, client: TestClient, mock_tutor_service):
        """Acceptance: Endpoint works with a mocked LLM."""
        payload = sample_request_payload(hint_level=1)
        response = client.post("/api/tutor/analyze", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["diagnosis"]["issue_type"] == "semantic_error"
        assert data["hint_level"] == 1
        assert data["solution_revealed"] is False
        assert "tutor_response" in data
        assert data["prompt_version"] == "v1"

    def test_guest_analysis_works_and_is_never_persisted(self, client: TestClient, mock_tutor_service):
        """Acceptance: Guest analysis works and guest input is never persisted."""
        payload = sample_request_payload(save_input=True, save_result=True)
        # Gửi request không kèm Authorization header (Guest)
        response = client.post("/api/tutor/analyze", json=payload)

        assert response.status_code == 200
        data = response.json()
        # Guest không bao giờ có session_id được lưu
        assert data.get("session_id") is None

    def test_authenticated_persistence_respects_consent_and_save_input(
        self, client: TestClient, auth_headers: dict, mock_tutor_service
    ):
        """Acceptance: Authenticated persistence respects consent."""
        # 1. Bật consent cho phép lưu
        client.post(
            "/api/consent",
            headers=auth_headers,
            json={
                "history_enabled": True,
                "save_input": True,
                "save_result": True,
                "consent_type": "privacy_settings",
                "is_accepted": True,
            },
        )

        # 2. Phân tích với save_input=True
        payload = sample_request_payload(save_input=True, save_result=True)
        response = client.post("/api/tutor/analyze", headers=auth_headers, json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data.get("session_id") is not None

        # 3. Kiểm tra lịch sử có lưu cả code
        history_res = client.get("/api/history", headers=auth_headers)
        assert history_res.status_code == 200
        items = history_res.json()["items"]
        assert len(items) >= 1
        saved_item = items[0]
        assert saved_item["save_input"] is True
        assert saved_item["chat_text"] is not None

    def test_authenticated_persistence_without_code_when_save_input_is_false(
        self, client: TestClient, auth_headers: dict, mock_tutor_service
    ):
        # Phân tích với save_input=False, save_result=True
        payload = sample_request_payload(save_input=False, save_result=True)
        response = client.post("/api/tutor/analyze", headers=auth_headers, json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data.get("session_id") is not None

        # Lịch sử có kết quả nhưng chat_text (mã nguồn) là null
        history_res = client.get("/api/history", headers=auth_headers)
        items = history_res.json()["items"]
        assert len(items) >= 1
        assert items[0]["chat_text"] is None
        assert items[0]["save_input"] is False

    def test_authenticated_persistence_skipped_when_history_disabled(
        self, client: TestClient, auth_headers: dict, mock_tutor_service
    ):
        # Tắt lịch sử trong consent
        client.post(
            "/api/consent",
            headers=auth_headers,
            json={
                "history_enabled": False,
                "save_input": False,
                "save_result": False,
                "consent_type": "privacy_settings",
                "is_accepted": False,
            },
        )

        payload = sample_request_payload(save_input=True, save_result=True)
        response = client.post("/api/tutor/analyze", headers=auth_headers, json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data.get("session_id") is None

    def test_unsupported_language_returns_clear_error(self, client: TestClient, mock_tutor_service):
        payload = sample_request_payload()
        payload["programming_language"] = "python"

        response = client.post("/api/tutor/analyze", json=payload)
        assert response.status_code == 422
        content = response.text
        assert "Unsupported programming language" in content
        assert "csharp" in content

    def test_invalid_request_returns_clear_error(self, client: TestClient, mock_tutor_service):
        # 1. Đề bài rỗng
        payload = sample_request_payload()
        payload["problem_statement"] = "   "
        response = client.post("/api/tutor/analyze", json=payload)
        assert response.status_code == 422

        # 2. Hint level ngoài 1..4
        payload = sample_request_payload()
        payload["hint_level"] = 5
        response = client.post("/api/tutor/analyze", json=payload)
        assert response.status_code == 422

    def test_provider_unavailable_returns_502_error(self, client: TestClient):
        # Giả lập LLM Provider bị lỗi mạng / timeout
        broken_provider = DeterministicMockTutorProvider(
            error_to_raise=TutorProviderError("504 Gateway Timeout từ nhà cung cấp LLM", retryable=True)
        )
        service = TutorService(llm_provider=broken_provider)
        app.dependency_overrides[get_tutor_service] = lambda: service

        try:
            payload = sample_request_payload()
            response = client.post("/api/tutor/analyze", json=payload)
            assert response.status_code == 502
            assert "hiện không thể phản hồi" in response.json()["detail"]
        finally:
            app.dependency_overrides.pop(get_tutor_service, None)

    def test_malformed_model_response_returns_502_error(self, client: TestClient):
        # Giả lập LLM trả về chuỗi hỏng không parse được JSON
        broken_provider = DeterministicMockTutorProvider(canned_response="Random AI text without valid JSON...")
        service = TutorService(llm_provider=broken_provider)
        app.dependency_overrides[get_tutor_service] = lambda: service

        try:
            payload = sample_request_payload()
            response = client.post("/api/tutor/analyze", json=payload)
            assert response.status_code == 502
            assert "json" in response.json()["detail"].lower()
        finally:
            app.dependency_overrides.pop(get_tutor_service, None)

    def test_rate_limit_returns_429_with_retry_after(self, client: TestClient, monkeypatch, mock_tutor_service):
        monkeypatch.setattr(settings, "analyze_rate_limit_requests", 2)
        monkeypatch.setattr(settings, "analyze_rate_limit_window_seconds", 60)

        payload = sample_request_payload()

        # Request 1: thành công
        res1 = client.post("/api/tutor/analyze", json=payload)
        assert res1.status_code == 200

        # Request 2: thành công
        res2 = client.post("/api/tutor/analyze", json=payload)
        assert res2.status_code == 200

        # Request 3: vượt hạn mức -> 429
        res3 = client.post("/api/tutor/analyze", json=payload)
        assert res3.status_code == 429
        assert "Retry-After" in res3.headers
        assert "quá nhanh" in res3.json()["detail"]
