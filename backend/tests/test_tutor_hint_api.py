import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.routes.tutor import get_tutor_service
from app.tutor.provider import DeterministicMockTutorProvider
from app.tutor.service import TutorService


@pytest.fixture
def mock_tutor_service():
    provider = DeterministicMockTutorProvider()
    service = TutorService(llm_provider=provider)
    app.dependency_overrides[get_tutor_service] = lambda: service
    yield service
    app.dependency_overrides.pop(get_tutor_service, None)


def sample_analyze_payload():
    return {
        "problem_statement": "Xây dựng lớp Dog có thuộc tính Name và constructor Dog(string name).",
        "student_code": "public class Dog { string name; public Dog(string name) { name = name; } }",
        "programming_language": "csharp",
        "topic": "class_constructor",
        "hint_level": 1,
        "save_input": True,
        "save_result": True,
    }


class TestTutorHintGuestAPI:
    """Kiểm tra chế độ Stateless Guest với signed context token (zero persistence)."""

    def test_guest_hint_progression_sequential(self, client: TestClient, mock_tutor_service):
        """Acceptance: Hint progression works from Level 1 -> 2 -> 3 -> 4 for guest."""
        # 1. Bắt đầu phiên với /analyze
        analyze_res = client.post("/api/tutor/analyze", json=sample_analyze_payload())
        assert analyze_res.status_code == 200
        analyze_data = analyze_res.json()
        guest_token = analyze_data.get("guest_context_token")
        assert guest_token is not None
        assert analyze_data.get("session_id") is None  # Guest has zero persistence

        # 2. Advance 1 -> 2
        hint_res1 = client.post(
            "/api/tutor/hint",
            json={
                "current_hint_level": 1,
                "guest_context_token": guest_token,
            },
        )
        assert hint_res1.status_code == 200
        data1 = hint_res1.json()
        assert data1["hint_level"] == 2
        assert data1["highest_hint_level_used"] == 2
        assert data1["solution_revealed"] is False
        assert "tutor_response" in data1
        token2 = data1.get("guest_context_token")
        assert token2 is not None

        # 3. Advance 2 -> 3
        hint_res2 = client.post(
            "/api/tutor/hint",
            json={
                "current_hint_level": 2,
                "guest_context_token": token2,
            },
        )
        assert hint_res2.status_code == 200
        data2 = hint_res2.json()
        assert data2["hint_level"] == 3
        assert data2["highest_hint_level_used"] == 3
        assert data2["solution_revealed"] is False
        token3 = data2.get("guest_context_token")
        assert token3 is not None

        # 4. Advance 3 -> 4
        hint_res3 = client.post(
            "/api/tutor/hint",
            json={
                "current_hint_level": 3,
                "guest_context_token": token3,
            },
        )
        assert hint_res3.status_code == 200
        data3 = hint_res3.json()
        assert data3["hint_level"] == 4
        assert data3["highest_hint_level_used"] == 4
        assert data3["solution_revealed"] is True  # Level 4 reveals explicit solution

    def test_guest_tampered_token_rejected(self, client: TestClient, mock_tutor_service):
        """Acceptance: Tampered guest token is rejected with 400 Bad Request."""
        analyze_res = client.post("/api/tutor/analyze", json=sample_analyze_payload())
        guest_token = analyze_res.json()["guest_context_token"]

        # Giả mạo token bằng cách thay đổi ký tự
        tampered_token = guest_token[:-5] + "aaaaa"
        res = client.post(
            "/api/tutor/hint",
            json={
                "current_hint_level": 1,
                "guest_context_token": tampered_token,
            },
        )
        assert res.status_code == 400
        assert "can thiệp" in res.json()["detail"] or "không hợp lệ" in res.json()["detail"]

    def test_guest_invalid_level_transition_rejected(self, client: TestClient, mock_tutor_service):
        """Acceptance: Invalid level transitions are rejected."""
        analyze_res = client.post("/api/tutor/analyze", json=sample_analyze_payload())
        token1 = analyze_res.json()["guest_context_token"]

        # Advance lên level 2
        hint_res1 = client.post(
            "/api/tutor/hint",
            json={"current_hint_level": 1, "guest_context_token": token1},
        )
        token2 = hint_res1.json()["guest_context_token"]

        # Client cố tình gửi current_hint_level=1 với token đã ở level 2 (nhằm reset tracking)
        bad_reset = client.post(
            "/api/tutor/hint",
            json={"current_hint_level": 1, "guest_context_token": token2},
        )
        assert bad_reset.status_code == 400
        assert "Chuyển đổi cấp độ không hợp lệ" in bad_reset.json()["detail"]

        # Client cố tình nhảy cóc gửi current_hint_level=3 với token đang ở level 2
        bad_jump = client.post(
            "/api/tutor/hint",
            json={"current_hint_level": 3, "guest_context_token": token2},
        )
        assert bad_jump.status_code == 400
        assert "Chuyển đổi cấp độ không hợp lệ" in bad_jump.json()["detail"]


class TestTutorHintAuthenticatedAPI:
    """Kiểm tra chế độ Authenticated với phiên học lưu trong database."""

    def test_authenticated_hint_progression_from_db(
        self, client: TestClient, auth_headers: dict, mock_tutor_service
    ):
        """Acceptance: Authenticated sessions load state from database and advance."""
        # 1. Bật consent
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

        # 2. Tạo session qua /analyze
        analyze_res = client.post(
            "/api/tutor/analyze",
            headers=auth_headers,
            json=sample_analyze_payload(),
        )
        assert analyze_res.status_code == 200
        session_id = analyze_res.json().get("session_id")
        assert session_id is not None

        # 3. Yêu cầu gợi ý tiếp theo qua /hint
        hint_res = client.post(
            "/api/tutor/hint",
            headers=auth_headers,
            json={
                "session_id": session_id,
                "current_hint_level": 1,
            },
        )
        assert hint_res.status_code == 200
        data = hint_res.json()
        assert data["hint_level"] == 2
        assert data["highest_hint_level_used"] == 2
        assert data["solution_revealed"] is False
        assert data["session_id"] == session_id

        # 4. Tiếp tục lên Level 3
        hint_res2 = client.post(
            "/api/tutor/hint",
            headers=auth_headers,
            json={
                "session_id": session_id,
                "current_hint_level": 2,
            },
        )
        assert hint_res2.status_code == 200
        assert hint_res2.json()["hint_level"] == 3

    def test_authenticated_invalid_level_transition_rejected(
        self, client: TestClient, auth_headers: dict, mock_tutor_service
    ):
        """Acceptance: Invalid level transition for authenticated user is rejected."""
        # 1. Bật consent và tạo session
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
        analyze_res = client.post(
            "/api/tutor/analyze",
            headers=auth_headers,
            json=sample_analyze_payload(),
        )
        session_id = analyze_res.json()["session_id"]

        # Advance lên Level 2
        client.post(
            "/api/tutor/hint",
            headers=auth_headers,
            json={"session_id": session_id, "current_hint_level": 1},
        )

        # Cố tình gửi current_hint_level=1 khi DB đã ở Level 2
        res_reset = client.post(
            "/api/tutor/hint",
            headers=auth_headers,
            json={"session_id": session_id, "current_hint_level": 1},
        )
        assert res_reset.status_code == 400
        assert "Chuyển đổi cấp độ không hợp lệ" in res_reset.json()["detail"]

    def test_authenticated_nonexistent_session_returns_404(
        self, client: TestClient, auth_headers: dict, mock_tutor_service
    ):
        res = client.post(
            "/api/tutor/hint",
            headers=auth_headers,
            json={
                "session_id": "00000000-0000-0000-0000-000000000000",
                "current_hint_level": 1,
            },
        )
        assert res.status_code == 404
        assert "Không tìm thấy phiên học tập" in res.json()["detail"]

    def test_authenticated_missing_session_id_returns_400(
        self, client: TestClient, auth_headers: dict, mock_tutor_service
    ):
        res = client.post(
            "/api/tutor/hint",
            headers=auth_headers,
            json={"current_hint_level": 1},
        )
        assert res.status_code == 400
        assert "Yêu cầu session_id" in res.json()["detail"]
