from uuid import uuid4
import pytest
from fastapi.testclient import TestClient

from app.schemas.student_profile_schema import (
    PreferredExplanation,
    SolutionPreference,
    StudentProfileResponse,
)


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


class TestStudentProfileAPI:
    """Kiểm tra toàn diện hệ thống StudentProfile độc lập (APT-016)."""

    def test_get_student_profile_not_found_initially(self, client: TestClient):
        """Sinh viên mới chưa tạo hồ sơ gọi GET trả về 404 Not Found."""
        headers = register_and_login(client)
        res = client.get("/api/student-profile", headers=headers)
        assert res.status_code == 404
        assert "chưa được khởi tạo" in res.json()["detail"]

    def test_create_and_get_student_profile_minimal_defaults(self, client: TestClient):
        """
        Khởi tạo hồ sơ với các giá trị mặc định chuẩn C# OOP:
        programming_language='csharp', skill_level='beginner', preferred_explanation='step_by_step', solution_preference='hint_first'.
        """
        headers = register_and_login(client)
        res_post = client.post("/api/student-profile", json={}, headers=headers)
        assert res_post.status_code == 200
        data = res_post.json()
        assert data["programming_language"] == "csharp"
        assert data["skill_level"] == "beginner"
        assert data["preferred_explanation"] == "step_by_step"
        assert data["solution_preference"] == "hint_first"
        assert data["display_name"] is None
        assert data["current_course"] is None

        # Kiểm tra GET lấy đúng dữ liệu
        res_get = client.get("/api/student-profile", headers=headers)
        assert res_get.status_code == 200
        assert res_get.json()["id"] == data["id"]

    def test_create_and_update_student_profile_full(self, client: TestClient):
        """Tạo hồ sơ đầy đủ và cập nhật các tùy chọn sư phạm."""
        headers = register_and_login(client)
        initial_payload = {
            "display_name": "Tran Van An",
            "programming_language": "c#",  # Tự động chuẩn hóa về csharp
            "skill_level": "beginner",
            "current_course": "CS101 C# OOP",
            "preferred_explanation": "concise",
            "solution_preference": "balanced",
        }
        res_create = client.post("/api/student-profile", json=initial_payload, headers=headers)
        assert res_create.status_code == 200
        created = res_create.json()
        assert created["display_name"] == "Tran Van An"
        assert created["programming_language"] == "csharp"
        assert created["preferred_explanation"] == "concise"
        assert created["solution_preference"] == "balanced"

        # Cập nhật hồ sơ
        update_payload = {
            "display_name": "An Tran",
            "programming_language": "csharp",
            "skill_level": "beginner",
            "current_course": "CS102 Data Structures",
            "preferred_explanation": "example_first",
            "solution_preference": "hint_first",
        }
        res_update = client.post("/api/student-profile", json=update_payload, headers=headers)
        assert res_update.status_code == 200
        updated = res_update.json()
        assert updated["id"] == created["id"]
        assert updated["display_name"] == "An Tran"
        assert updated["preferred_explanation"] == "example_first"
        assert updated["current_course"] == "CS102 Data Structures"

    def test_delete_student_profile_success(self, client: TestClient):
        """
        Acceptance: Xóa hồ sơ sinh viên thành công.
        Sau khi xóa, GET trả về 404 Not Found.
        """
        headers = register_and_login(client)
        client.post(
            "/api/student-profile",
            json={"display_name": "Delete Me"},
            headers=headers,
        )

        # Xóa
        del_res = client.delete("/api/student-profile", headers=headers)
        assert del_res.status_code == 200
        assert del_res.json()["deleted"] is True

        # Đọc lại -> 404
        get_res = client.get("/api/student-profile", headers=headers)
        assert get_res.status_code == 404

    def test_validation_rejects_invalid_language(self, client: TestClient):
        """Từ chối các ngôn ngữ lập trình không được hỗ trợ trong V1."""
        headers = register_and_login(client)
        res = client.post(
            "/api/student-profile",
            json={"programming_language": "python"},
            headers=headers,
        )
        assert res.status_code == 422

    def test_validation_rejects_invalid_skill_level(self, client: TestClient):
        """Từ chối skill_level khác beginner trong V1."""
        headers = register_and_login(client)
        res = client.post(
            "/api/student-profile",
            json={"skill_level": "expert"},
            headers=headers,
        )
        assert res.status_code == 422

    def test_validation_rejects_invalid_preferred_explanation(self, client: TestClient):
        """Từ chối preferred_explanation không hợp lệ."""
        headers = register_and_login(client)
        res = client.post(
            "/api/student-profile",
            json={"preferred_explanation": "super_long_verbose"},
            headers=headers,
        )
        assert res.status_code == 422

    def test_validation_rejects_invalid_solution_preference(self, client: TestClient):
        """Từ chối solution_preference không hợp lệ."""
        headers = register_and_login(client)
        res = client.post(
            "/api/student-profile",
            json={"solution_preference": "give_solution_immediately"},
            headers=headers,
        )
        assert res.status_code == 422

    def test_schema_isolation_rejects_historical_relationship_fields(self, client: TestClient):
        """
        Acceptance: Student profile is isolated from historical relationship schema.
        Tuyệt đối không chấp nhận các trường cá nhân/tình cảm không liên quan.
        """
        headers = register_and_login(client)
        romantic_fields_payload = {
            "display_name": "Student A",
            "nickname": "Bé Yêu",
            "relationship_status": "dating",
            "partner_profile": {"nickname": "Người yêu"},
            "height_cm": 175,
            "likes": "Đi dạo",
        }
        res = client.post("/api/student-profile", json=romantic_fields_payload, headers=headers)
        assert res.status_code == 422  # extra="forbid" chặn đứng tất cả trường lạ

        # Xác nhận model response không chứa bất kỳ trường cũ nào
        allowed_keys = set(StudentProfileResponse.model_fields.keys())
        assert "nickname" not in allowed_keys
        assert "relationship_status" not in allowed_keys
        assert "partner_profile" not in allowed_keys
        assert "height_cm" not in allowed_keys
        assert "weight_kg" not in allowed_keys
        assert "likes" not in allowed_keys

    def test_strict_user_ownership(self, client: TestClient):
        """Hai người dùng độc lập hoàn toàn không ảnh hưởng hồ sơ của nhau."""
        headers_a = register_and_login(client)
        headers_b = register_and_login(client)

        client.post("/api/student-profile", json={"display_name": "Student A"}, headers=headers_a)
        client.post("/api/student-profile", json={"display_name": "Student B"}, headers=headers_b)

        assert client.get("/api/student-profile", headers=headers_a).json()["display_name"] == "Student A"
        assert client.get("/api/student-profile", headers=headers_b).json()["display_name"] == "Student B"

        # User B xóa profile của mình
        client.delete("/api/student-profile", headers=headers_b)
        assert client.get("/api/student-profile", headers=headers_b).status_code == 404

        # Profile của User A vẫn nguyên vẹn
        assert client.get("/api/student-profile", headers=headers_a).status_code == 200
        assert client.get("/api/student-profile", headers=headers_a).json()["display_name"] == "Student A"

    def test_unauthenticated_requests_rejected(self, client: TestClient):
        """Các yêu cầu không có header xác thực bị từ chối 401."""
        assert client.get("/api/student-profile").status_code == 401
        assert client.post("/api/student-profile", json={}).status_code == 401
        assert client.delete("/api/student-profile").status_code == 401

    def test_user_data_delete_cleans_student_profile(self, client: TestClient):
        """Khi gọi xóa toàn bộ tài khoản /api/user-data, student_profile cũng bị xóa sạch."""
        headers = register_and_login(client)
        client.post("/api/student-profile", json={"display_name": "To be wiped"}, headers=headers)
        assert client.get("/api/student-profile", headers=headers).status_code == 200

        # Xóa toàn bộ dữ liệu
        del_user_data = client.delete("/api/user-data", headers=headers)
        assert del_user_data.status_code == 200

        # Profile đã bị dọn dẹp
        assert client.get("/api/student-profile", headers=headers).status_code == 404
