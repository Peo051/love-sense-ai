from uuid import uuid4
import pytest
from fastapi.testclient import TestClient

from app.models.learning_session import LearningSession, StudentAttempt, TutorMessage
from tests.conftest import TestingSessionLocal


def register_and_login(client: TestClient, email: str | None = None) -> dict[str, str]:
    user_email = email or f"user-{uuid4()}@example.com"
    password = "StrongPassword123!"
    client.post("/api/register", json={"email": user_email, "password": password})
    token_res = client.post(
        "/api/token",
        data={"username": user_email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    token = token_res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


class TestLearningSessionsAPI:
    """Kiểm tra toàn diện tính năng Multi-turn Learning Sessions (APT-015)."""

    def test_create_session_without_code_consent(self, client: TestClient):
        """
        Acceptance: Khởi tạo session khi save_input=False.
        Mã nguồn sinh viên tuyệt đối KHÔNG được lưu vào DB (bằng None).
        """
        headers = register_and_login(client)
        payload = {
            "title": "C# OOP Constructors",
            "language": "csharp",
            "topic": "constructors",
            "initial_problem": "Tạo lớp Cat có constructor nhận tên.",
            "initial_code": "public class Cat { string name; public Cat(string n) { name = n; } }",
            "save_input": False,
        }
        res = client.post("/api/sessions", json=payload, headers=headers)
        assert res.status_code == 201
        data = res.json()
        assert data["title"] == "C# OOP Constructors"
        assert data["language"] == "csharp"
        assert data["topic"] == "constructors"
        assert data["attempt_count"] == 1
        assert data["message_count"] == 1
        assert len(data["attempts"]) == 1

        # Privacy invariant: do save_input=False nên student_code bắt buộc là None
        attempt = data["attempts"][0]
        assert attempt["save_input"] is False
        assert attempt["student_code"] is None

    def test_create_session_with_code_consent(self, client: TestClient):
        """
        Acceptance: Khởi tạo session khi save_input=True.
        Mã nguồn sinh viên được lưu trữ an toàn khi có sự đồng thuận.
        """
        headers = register_and_login(client)
        sample_code = "public class Dog { string name; public Dog(string n) { this.name = n; } }"
        payload = {
            "title": "C# OOP Encapsulation",
            "language": "csharp",
            "topic": "encapsulation",
            "initial_problem": "Tạo lớp Dog có constructor gán name.",
            "initial_code": sample_code,
            "save_input": True,
        }
        res = client.post("/api/sessions", json=payload, headers=headers)
        assert res.status_code == 201
        data = res.json()
        assert data["attempt_count"] == 1
        attempt = data["attempts"][0]
        assert attempt["save_input"] is True
        assert attempt["student_code"] == sample_code

    def test_list_sessions_strictly_scoped_to_user(self, client: TestClient):
        """
        Acceptance: Phân định quyền sở hữu nghiêm ngặt giữa các người dùng.
        User A không bao giờ nhìn thấy session của User B.
        """
        headers_user_a = register_and_login(client)
        headers_user_b = register_and_login(client)

        # User A tạo 2 sessions
        client.post("/api/sessions", json={"title": "Session A1"}, headers=headers_user_a)
        client.post("/api/sessions", json={"title": "Session A2"}, headers=headers_user_a)

        # User B tạo 1 session
        client.post("/api/sessions", json={"title": "Session B1"}, headers=headers_user_b)

        # User A list
        res_a = client.get("/api/sessions", headers=headers_user_a)
        assert res_a.status_code == 200
        titles_a = [s["title"] for s in res_a.json()]
        assert len(titles_a) == 2
        assert "Session A1" in titles_a
        assert "Session A2" in titles_a
        assert "Session B1" not in titles_a

        # User B list
        res_b = client.get("/api/sessions", headers=headers_user_b)
        assert res_b.status_code == 200
        titles_b = [s["title"] for s in res_b.json()]
        assert len(titles_b) == 1
        assert "Session B1" in titles_b
        assert "Session A1" not in titles_b

    def test_get_session_by_id_owner_success(self, client: TestClient):
        """Người dùng xem thành công session của chính mình."""
        headers = register_and_login(client)
        create_res = client.post(
            "/api/sessions",
            json={"title": "Session Test Detail", "topic": "inheritance"},
            headers=headers,
        )
        session_id = create_res.json()["id"]

        get_res = client.get(f"/api/sessions/{session_id}", headers=headers)
        assert get_res.status_code == 200
        data = get_res.json()
        assert data["id"] == session_id
        assert data["title"] == "Session Test Detail"

    def test_get_session_by_id_another_user_returns_404(self, client: TestClient):
        """
        Acceptance: Users cannot read another user's session.
        Khi User B cố đọc session của User A -> Trả về 404 Not Found.
        """
        headers_user_a = register_and_login(client)
        headers_user_b = register_and_login(client)

        create_res = client.post(
            "/api/sessions",
            json={"title": "Private Session of User A"},
            headers=headers_user_a,
        )
        session_id_a = create_res.json()["id"]

        # User B truy cập session của User A
        res = client.get(f"/api/sessions/{session_id_a}", headers=headers_user_b)
        assert res.status_code == 404
        assert "Không tìm thấy" in res.json()["detail"]

    def test_delete_session_owner_success(self, client: TestClient):
        """
        Acceptance: Data deletion works.
        Chủ sở hữu xóa session thành công và cascade các attempts, messages liên quan.
        """
        headers = register_and_login(client)
        create_res = client.post(
            "/api/sessions",
            json={
                "title": "Session To Delete",
                "initial_problem": "Bài toán cần xóa",
                "initial_code": "int a = 1;",
                "save_input": True,
            },
            headers=headers,
        )
        session_id = create_res.json()["id"]

        # Xóa session
        del_res = client.delete(f"/api/sessions/{session_id}", headers=headers)
        assert del_res.status_code == 200
        assert del_res.json()["deleted"] is True
        assert del_res.json()["id"] == session_id

        # Kiểm tra đọc lại -> 404
        get_res = client.get(f"/api/sessions/{session_id}", headers=headers)
        assert get_res.status_code == 404

    def test_delete_session_another_user_returns_404_and_keeps_data(self, client: TestClient):
        """
        Acceptance: User B không thể xóa session của User A. Dữ liệu của User A không bị ảnh hưởng.
        """
        headers_user_a = register_and_login(client)
        headers_user_b = register_and_login(client)

        create_res = client.post(
            "/api/sessions",
            json={"title": "Session Protected from B"},
            headers=headers_user_a,
        )
        session_id_a = create_res.json()["id"]

        # User B cố xóa session của User A
        del_res = client.delete(f"/api/sessions/{session_id_a}", headers=headers_user_b)
        assert del_res.status_code == 404

        # Dữ liệu của User A vẫn tồn tại bình thường
        get_res = client.get(f"/api/sessions/{session_id_a}", headers=headers_user_a)
        assert get_res.status_code == 200
        assert get_res.json()["title"] == "Session Protected from B"

    def test_unauthenticated_requests_rejected(self, client: TestClient):
        """Các yêu cầu không đăng nhập bị từ chối 401."""
        assert client.post("/api/sessions", json={"title": "Test"}).status_code == 401
        assert client.get("/api/sessions").status_code == 401
        assert client.get("/api/sessions/some-id").status_code == 401
        assert client.delete("/api/sessions/some-id").status_code == 401

    def test_add_attempt_and_message_to_session(self, client: TestClient):
        """Kiểm tra thêm attempt và message vào session đa lượt."""
        headers = register_and_login(client)
        session_id = client.post(
            "/api/sessions",
            json={"title": "Multi-turn Session"},
            headers=headers,
        ).json()["id"]

        # 1. Thêm attempt mới (save_input = False)
        att_res = client.post(
            f"/api/sessions/{session_id}/attempts",
            json={
                "problem_reference": "Thử thách 1",
                "student_code": "secret code",
                "save_input": False,
                "success_state": "in_progress",
            },
            headers=headers,
        )
        assert att_res.status_code == 201
        att_data = att_res.json()
        assert att_data["student_code"] is None  # Privacy invariant

        # 2. Thêm message mới
        msg_res = client.post(
            f"/api/sessions/{session_id}/messages",
            json={
                "role": "student",
                "content": "Em chưa hiểu cách gọi base constructor ạ.",
                "attempt_id": att_data["id"],
            },
            headers=headers,
        )
        assert msg_res.status_code == 201
        assert msg_res.json()["role"] == "student"

        # 3. Lấy lại chi tiết session
        detail = client.get(f"/api/sessions/{session_id}", headers=headers).json()
        assert len(detail["attempts"]) == 1
        assert len(detail["messages"]) == 1
        assert detail["messages"][0]["sanitized_textual_message"] == "Em chưa hiểu cách gọi base constructor ạ."

    def test_user_data_delete_cleans_all_sessions(self, client: TestClient):
        """Xóa toàn bộ dữ liệu người dùng qua /api/user-data cũng xóa sạch tất cả sessions."""
        headers = register_and_login(client)
        client.post("/api/sessions", json={"title": "Session to be wiped 1"}, headers=headers)
        client.post("/api/sessions", json={"title": "Session to be wiped 2"}, headers=headers)

        assert len(client.get("/api/sessions", headers=headers).json()) == 2

        # Gọi xóa toàn bộ dữ liệu
        del_res = client.delete("/api/user-data", headers=headers)
        assert del_res.status_code == 200

        # Danh sách session phải hoàn toàn trống
        assert len(client.get("/api/sessions", headers=headers).json()) == 0
