import unittest.mock as mock
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.routes.tutor import get_tutor_service
from app.schemas.tutor_schema import VerificationStatus
from app.tutor.provider import DeterministicMockTutorProvider
from app.tutor.service import TutorService
from app.tutor.verification import (
    SECURITY_BOUNDARY_NOTE,
    SandboxedCompilerBackend,
    StaticAndPatternExecutionBackend,
    VerificationService,
)


@pytest.fixture
def mock_tutor_service():
    provider = DeterministicMockTutorProvider()
    service = TutorService(llm_provider=provider)
    app.dependency_overrides[get_tutor_service] = lambda: service
    yield service
    app.dependency_overrides.pop(get_tutor_service, None)


class TestTutorVerifyAPI:
    """Kiểm tra endpoint POST /api/tutor/verify và VerificationService (APT-014)."""

    def test_verify_likely_resolved(self, client: TestClient):
        """
        Acceptance: Sinh viên sửa thành công lỗi field shadowing (name = name -> this.name = name).
        Hệ thống trả về likely_resolved, resolved=True.
        """
        payload = {
            "problem_statement": "Xây dựng lớp Dog có constructor nhận name và gán vào thuộc tính.",
            "previous_code": "public class Dog { string name; public Dog(string name) { name = name; } }",
            "revised_student_code": "public class Dog { string name; public Dog(string name) { this.name = name; } }",
        }
        res = client.post("/api/tutor/verify", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["verification_status"] == VerificationStatus.LIKELY_RESOLVED.value
        assert data["resolved"] is True
        assert len(data["remaining_issues"]) == 0
        assert len(data["new_issues"]) == 0
        assert "Rất tốt" in data["feedback"] or "giải quyết" in data["feedback"]
        assert data["security_boundary_note"] == SECURITY_BOUNDARY_NOTE

    def test_verify_still_present(self, client: TestClient):
        """
        Acceptance: Lỗi cũ vẫn còn tồn tại trong mã nguồn mới.
        Hệ thống trả về still_present, resolved=False.
        """
        payload = {
            "problem_statement": "Xây dựng lớp Dog có constructor nhận name và gán vào thuộc tính.",
            "previous_code": "public class Dog { string name; public Dog(string name) { name = name; } }",
            "revised_student_code": "public class Dog { string name; public Dog(string name) { name = name; } }",
        }
        res = client.post("/api/tutor/verify", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["verification_status"] == VerificationStatus.STILL_PRESENT.value
        assert data["resolved"] is False
        assert len(data["remaining_issues"]) > 0
        assert "chưa được khắc phục" in data["remaining_issues"][0] or "vẫn còn xuất hiện" in data["feedback"]

    def test_verify_new_issue(self, client: TestClient):
        """
        Acceptance: Sinh viên sửa lỗi cũ nhưng làm phát sinh lỗi mới (ví dụ recursive property).
        Hệ thống trả về new_issue, resolved=False.
        """
        payload = {
            "problem_statement": "Xây dựng lớp Student có thuộc tính Name hợp lệ.",
            "previous_code": "public class Student { string name; public Student(string name) { name = name; } }",
            "revised_student_code": "public class Student { public string Name { get { return Name; } set { Name = value; } } }",
        }
        res = client.post("/api/tutor/verify", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["verification_status"] == VerificationStatus.NEW_ISSUE.value
        assert data["resolved"] is False
        assert len(data["new_issues"]) > 0
        assert "vấn đề mới phát sinh" in data["feedback"]

    def test_verify_needs_execution_to_confirm(self, client: TestClient):
        """
        Acceptance: Mã nguồn chứa vòng lặp phức tạp (runtime algorithm),
        cần kiểm thử thực tế trên máy để khẳng định -> needs_execution_to_confirm.
        """
        payload = {
            "problem_statement": "Viết lớp Counter đếm ngược.",
            "previous_code": "public class Counter { int count; public Counter(int count) { count = count; } }",
            "revised_student_code": "public class Counter { int count; public Counter(int count) { this.count = count; while (this.count > 0) { this.count--; } } }",
        }
        res = client.post("/api/tutor/verify", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["verification_status"] == VerificationStatus.NEEDS_EXECUTION_TO_CONFIRM.value
        assert data["resolved"] is True
        assert "chạy thử nghiệm thực tế" in data["feedback"]

    def test_security_boundary_explicit_and_no_untrusted_exec(self, client: TestClient):
        """
        Acceptance:
        - Security boundary được phân định rõ ràng trong mọi phản hồi.
        - Tuyệt đối KHÔNG gọi subprocess/shell để thực thi mã nguồn tùy ý trên production.
        """
        with mock.patch("subprocess.run") as mock_subproc, mock.patch("os.system") as mock_system:
            payload = {
                "problem_statement": "Bài tập C# căn bản.",
                "revised_student_code": "public class Test { public static void Main() { System.Diagnostics.Process.Start(\"calc\"); } }",
            }
            res = client.post("/api/tutor/verify", json=payload)
            assert res.status_code == 200
            data = res.json()

            # Phân tích tĩnh, không thực thi mã
            assert mock_subproc.call_count == 0
            assert mock_system.call_count == 0
            assert data["security_boundary_note"] == SECURITY_BOUNDARY_NOTE
            assert "chưa qua môi trường thực thi hộp cát" in data["security_boundary_note"]

    def test_verify_with_guest_context_token(self, client: TestClient, mock_tutor_service):
        """
        Kiểm tra guest flow: /analyze tạo guest_context_token -> /verify sử dụng token mà không cần truyền lại previous_code.
        """
        analyze_res = client.post(
            "/api/tutor/analyze",
            json={
                "problem_statement": "Tạo lớp Dog có constructor.",
                "student_code": "public class Dog { string name; public Dog(string name) { name = name; } }",
                "programming_language": "csharp",
                "hint_level": 1,
            },
        )
        assert analyze_res.status_code == 200
        guest_token = analyze_res.json().get("guest_context_token")
        assert guest_token is not None

        # Gửi verify kèm token
        verify_res = client.post(
            "/api/tutor/verify",
            json={
                "problem_statement": "Tạo lớp Dog có constructor.",
                "revised_student_code": "public class Dog { string name; public Dog(string name) { this.name = name; } }",
                "guest_context_token": guest_token,
            },
        )
        assert verify_res.status_code == 200
        data = verify_res.json()
        assert data["verification_status"] == VerificationStatus.LIKELY_RESOLVED.value
        assert data["resolved"] is True

    def test_verify_validation_errors(self, client: TestClient):
        """Kiểm tra ràng buộc đầu vào theo Pydantic schema."""
        # Thiếu revised_student_code
        res1 = client.post("/api/tutor/verify", json={"problem_statement": "Hợp lệ"})
        assert res1.status_code == 422

        # revised_student_code chỉ toàn khoảng trắng
        res2 = client.post(
            "/api/tutor/verify",
            json={"problem_statement": "Hợp lệ", "revised_student_code": "   "},
        )
        assert res2.status_code == 422


class TestVerificationServiceUnit:
    """Unit tests trực tiếp cho VerificationService và các ExecutionBackend."""

    @pytest.mark.anyio
    async def test_static_backend_diagnoses_cleanly(self):
        backend = StaticAndPatternExecutionBackend()
        diag = await backend.inspect_or_execute("public class Valid { public int X { get; set; } }")
        assert diag.category.value == "no_bug"

    @pytest.mark.anyio
    async def test_sandboxed_backend_placeholder_raises_not_implemented(self):
        backend = SandboxedCompilerBackend()
        with pytest.raises(NotImplementedError):
            await backend.inspect_or_execute("public class Test {}")
