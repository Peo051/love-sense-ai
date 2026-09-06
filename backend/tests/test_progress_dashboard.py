from uuid import uuid4
import pytest
from fastapi.testclient import TestClient

from app.tutor.mastery import MasteryEvent


def register_and_login(client: TestClient, email: str | None = None) -> dict[str, str]:
    user_email = email or f"student-{uuid4()}@example.com"
    password = "StrongPassword123!"
    client.post("/api/register", json={"email": user_email, "password": password})
    token_res = client.post(
        "/api/token",
        data={"username": user_email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    token = token_res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


class TestStudentProgressDashboardApi:
    """Kiểm tra API /api/progress/dashboard và /api/mastery/dashboard (APT-023)."""

    def test_dashboard_requires_authentication(self, client: TestClient):
        """Endpoint yêu cầu người dùng phải đăng nhập (401 Unauthorized)."""
        res = client.get("/api/progress/dashboard")
        assert res.status_code == 401
        res_mastery = client.get("/api/mastery/dashboard")
        assert res_mastery.status_code == 401

    def test_new_user_empty_state(self, client: TestClient):
        """Học viên mới chưa có lần thử nào: trả về trạng thái trống (is_empty=True) và điểm khởi tạo 0.5."""
        headers = register_and_login(client)
        res = client.get("/api/progress/dashboard", headers=headers)
        assert res.status_code == 200
        data = res.json()

        assert data["is_empty"] is True
        assert data["practiced_skills"] == 0
        assert data["total_skills"] == 16
        assert data["current_mastery_estimate"] == 0.5
        assert data["total_attempts_count"] == 0
        assert data["independent_solution_rate"] is None
        assert data["average_hint_level"] is None
        assert data["strong_topics"] == []
        assert len(data["topics_needing_practice"]) >= 3
        assert len(data["all_skills"]) == 16
        assert len(data["recent_attempts"]) == 0

    def test_dashboard_reflects_actual_practice_and_mastery(self, client: TestClient):
        """Số liệu dashboard phản ánh chính xác từ bài làm thực tế, không dùng số liệu giả."""
        headers = register_and_login(client)

        # 1. Lần thử 1: Giải thành công độc lập (Independent Success) cho kỹ năng class_object
        payload_p1 = {
            "skill_ids": ["csharp.class_object"],
            "event": "independent_success",
            "hints_used": 0,
        }
        res_p1 = client.post("/api/mastery/practice", json=payload_p1, headers=headers)
        assert res_p1.status_code == 200

        # Kiểm tra dashboard sau lần thử 1
        res = client.get("/api/progress/dashboard", headers=headers)
        assert res.status_code == 200
        d1 = res.json()

        assert d1["is_empty"] is False
        assert d1["practiced_skills"] == 1
        assert d1["current_mastery_estimate"] == 0.65  # 0.5 + 0.15
        assert d1["total_attempts_count"] == 1
        assert d1["independent_solution_rate"] == 1.0  # 1 / 1
        assert d1["average_hint_level"] == 0.0
        assert len(d1["strong_topics"]) == 1
        assert d1["strong_topics"][0]["skill_id"] == "csharp.class_object"
        assert len(d1["recent_attempts"]) == 1

        # 2. Lần thử 2: Giải thành công qua gợi ý L1 (Hint L1 Success) cho kỹ năng property
        payload_p2 = {
            "skill_ids": ["csharp.property"],
            "event": "hint_l1_success",
            "hints_used": 1,
        }
        client.post("/api/mastery/practice", json=payload_p2, headers=headers)

        res2 = client.get("/api/progress/dashboard", headers=headers)
        d2 = res2.json()

        assert d2["practiced_skills"] == 2
        # class_object: 0.65, property: 0.60 -> trung bình = 0.625
        assert d2["current_mastery_estimate"] == 0.625
        assert d2["total_attempts_count"] == 2
        # 1 độc lập trên 2 bài thành công -> 50% = 0.5
        assert d2["independent_solution_rate"] == 0.5
        # Hint level: [0, 1] -> trung bình = 0.5
        assert d2["average_hint_level"] == 0.5

        # 3. Lần thử 3: Thất bại chưa sửa được (Unresolved) cho kỹ năng constructor
        payload_p3 = {
            "skill_ids": ["csharp.constructor"],
            "event": "unresolved_attempt",
            "hints_used": 2,
        }
        client.post("/api/mastery/practice", json=payload_p3, headers=headers)

        res3 = client.get("/api/progress/dashboard", headers=headers)
        d3 = res3.json()

        assert d3["practiced_skills"] == 3
        # constructor điểm giảm xuống 0.45 (0.5 - 0.05), xuất hiện trong topics_needing_practice
        needing_ids = [t["skill_id"] for t in d3["topics_needing_practice"]]
        assert "csharp.constructor" in needing_ids

    def test_strict_user_ownership_dashboard(self, client: TestClient):
        """User B không nhìn thấy bất kỳ dữ liệu bài làm nào của User A."""
        headers_a = register_and_login(client, email="user-a@example.com")
        headers_b = register_and_login(client, email="user-b@example.com")

        # User A thực hành bài tập
        client.post(
            "/api/mastery/practice",
            json={"skill_ids": ["csharp.inheritance"], "event": "independent_success", "hints_used": 0},
            headers=headers_a,
        )

        # User A có dữ liệu
        data_a = client.get("/api/progress/dashboard", headers=headers_a).json()
        assert data_a["is_empty"] is False
        assert data_a["practiced_skills"] == 1
        assert len(data_a["strong_topics"]) == 1

        # User B hoàn toàn trống
        data_b = client.get("/api/progress/dashboard", headers=headers_b).json()
        assert data_b["is_empty"] is True
        assert data_b["practiced_skills"] == 0
        assert len(data_b["strong_topics"]) == 0
        assert data_b["total_attempts_count"] == 0
