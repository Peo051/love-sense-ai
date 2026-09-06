"""
Unit & Integration Tests for Connecting Attempts to Mastery Updates (APT-019).

Verifies:
1. Unverified model diagnosis alone does not update mastery.
2. Actual student interaction outcome updates mastery for related knowledge components.
3. Independent successful correction increases mastery more than success after explicit solution.
4. Repeated failures reduce mastery modestly without erratic large jumps.
5. Record why update occurred (audit metadata: previous_score, new_score, event_type, attempt_id, reason).
6. Transactional integrity: rollback on error preserves both attempt and mastery state.
7. Acceptance Criteria: Replaying the same event cannot double-update mastery (Idempotency protection).
8. Strict user isolation and cascade cleanup on user data deletion.
"""

from unittest.mock import patch
from uuid import uuid4
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.main import app
from app.models.learning_session import LearningSession, StudentAttempt
from app.models.mastery_audit import StudentMasteryAudit
from app.models.student_skill_mastery import StudentSkillMastery
from app.routes.tutor import get_tutor_service
from app.services.attempt_mastery_coordinator import AttemptMasteryCoordinator
from app.tutor.mastery import DeterministicMasteryModel, MasteryEvent
from app.tutor.provider import DeterministicMockTutorProvider
from app.tutor.service import TutorService


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


def create_session_and_attempt(
    client: TestClient,
    headers: dict[str, str],
    *,
    problem: str = "Tạo thuộc tính Age trong lớp Person",
    knowledge_components: list[str] | None = None,
) -> tuple[str, str]:
    """Helper tạo phiên học và lần thử bài với diagnosis mẫu."""
    res_session = client.post(
        "/api/sessions",
        json={"title": "Luyện tập C# OOP", "topic": "Properties"},
        headers=headers,
    )
    session_id = res_session.json()["id"]

    kc = knowledge_components or ["csharp.property", "csharp.encapsulation"]
    res_attempt = client.post(
        f"/api/sessions/{session_id}/attempts",
        json={
            "problem_reference": problem,
            "save_input": False,
            "diagnosis": {
                "category": "logic_error",
                "issue_type": "invalid_setter_validation",
                "knowledge_components": kc,
            },
            "success_state": "in_progress",
        },
        headers=headers,
    )
    attempt_id = res_attempt.json()["id"]
    return session_id, attempt_id


@pytest.fixture
def mock_tutor_service():
    provider = DeterministicMockTutorProvider()
    service = TutorService(llm_provider=provider)
    app.dependency_overrides[get_tutor_service] = lambda: service
    yield service
    app.dependency_overrides.pop(get_tutor_service, None)


class TestUnverifiedDiagnosisAloneDoesNotUpdateMastery:
    """Quy tắc 1: Không cập nhật điểm chỉ từ một chẩn đoán chưa được xác minh."""

    def test_analyzing_or_creating_attempt_does_not_alter_mastery(self, client: TestClient, mock_tutor_service):
        headers = register_and_login(client)

        # 1. Gọi phân tích (/api/tutor/analyze) với mock provider
        analyze_payload = {
            "problem_statement": "Xây dựng lớp Car với thuộc tính Speed.",
            "student_code": "class Car { public int Speed { get; set; } }",
            "language": "csharp",
        }
        res_analyze = client.post("/api/tutor/analyze", json=analyze_payload, headers=headers)
        assert res_analyze.status_code == 200

        # 2. Tạo session và attempt ở trạng thái 'in_progress'
        session_id, attempt_id = create_session_and_attempt(client, headers)

        # 3. Kiểm tra: Chưa có bất kỳ bản ghi audit nào và điểm mastery vẫn giữ 0.5 (neutral)
        res_audits = client.get("/api/mastery/audit", headers=headers)
        assert res_audits.status_code == 200
        assert len(res_audits.json()) == 0

        # Kiểm tra điểm các kỹ năng vẫn là 0.5 với success_count = 0
        res_prop = client.get("/api/mastery/csharp.property", headers=headers)
        assert res_prop.status_code == 200
        assert res_prop.json()["mastery_score"] == 0.5
        assert res_prop.json()["success_count"] == 0
        assert res_prop.json()["failure_count"] == 0


class TestAttemptMasteryResolutionAndAuditing:
    """Kiểm tra giải quyết lần thử thực tế, audit metadata và các mức biến động điểm."""

    def test_independent_successful_resolution_updates_mastery_and_records_audit(self, client: TestClient):
        """Sinh viên tự sửa thành công độc lập (0 hints) tăng +0.15 điểm kèm đầy đủ audit metadata."""
        headers = register_and_login(client)
        session_id, attempt_id = create_session_and_attempt(
            client,
            headers,
            knowledge_components=["csharp.property"],
        )

        resolve_payload = {
            "outcome": "resolved",
            "highest_hint_level": 0,
            "solution_revealed": False,
            "hints_used": 0,
            "custom_reason": "Sinh viên tự sửa đúng lỗi setter sau lần xem lại đề.",
        }
        res = client.post(
            f"/api/sessions/{session_id}/attempts/{attempt_id}/resolve",
            json=resolve_payload,
            headers=headers,
        )
        assert res.status_code == 200
        data = res.json()
        assert data["attempt_id"] == attempt_id
        assert data["success_state"] == "resolved"
        assert len(data["audit_records"]) == 1

        audit = data["audit_records"][0]
        assert audit["skill_id"] == "csharp.property"
        assert audit["event_type"] == "independent_success"
        assert audit["previous_score"] == 0.50
        assert audit["new_score"] == 0.65
        assert "Sinh viên tự sửa đúng" in audit["reason"]
        assert audit["attempt_id"] == attempt_id

        # Kiểm tra endpoint audit
        res_audit_list = client.get(f"/api/mastery/audit/{attempt_id}", headers=headers)
        assert res_audit_list.status_code == 200
        assert len(res_audit_list.json()) == 1

    def test_independent_success_increases_more_than_explicit_solution(self, client: TestClient):
        """
        Quy tắc:
        'Independent successful correction should increase mastery more than success after explicit solution.'
        """
        headers_a = register_and_login(client)
        s_a, att_a = create_session_and_attempt(client, headers_a, knowledge_components=["csharp.getter"])

        # Học viên A: Làm đúng độc lập
        res_a = client.post(
            f"/api/sessions/{s_a}/attempts/{att_a}/resolve",
            json={"outcome": "resolved", "highest_hint_level": 0, "solution_revealed": False},
            headers=headers_a,
        )
        audit_a = res_a.json()["audit_records"][0]
        delta_a = audit_a["new_score"] - audit_a["previous_score"]

        # Học viên B: Xem lời giải chi tiết Level 4
        headers_b = register_and_login(client)
        s_b, att_b = create_session_and_attempt(client, headers_b, knowledge_components=["csharp.getter"])
        res_b = client.post(
            f"/api/sessions/{s_b}/attempts/{att_b}/resolve",
            json={"outcome": "solution_revealed", "highest_hint_level": 4, "solution_revealed": True},
            headers=headers_b,
        )
        audit_b = res_b.json()["audit_records"][0]
        delta_b = audit_b["new_score"] - audit_b["previous_score"]

        # delta_a (+0.15) > delta_b (-0.05)
        assert round(delta_a, 4) == 0.15
        assert round(delta_b, 4) == -0.05
        assert delta_a > delta_b

    def test_repeated_failures_reduce_modestly_and_avoid_large_jumps(self, client: TestClient):
        """
        Quy tắc:
        'Repeated failures may reduce mastery modestly. Avoid large jumps from a single attempt.'
        """
        headers = register_and_login(client)

        score = 0.5
        for i in range(3):
            s_id, att_id = create_session_and_attempt(client, headers, knowledge_components=["csharp.validation"])
            res = client.post(
                f"/api/sessions/{s_id}/attempts/{att_id}/resolve",
                json={"outcome": "failed", "highest_hint_level": 1, "solution_revealed": False},
                headers=headers,
            )
            audit = res.json()["audit_records"][0]
            jump = abs(audit["new_score"] - audit["previous_score"])
            assert round(jump, 4) <= 0.15, "Bước nhảy của 1 lần thử vượt quá giới hạn an toàn 0.15"
            score = audit["new_score"]

        # 0.5 - 0.15 - 0.15 - 0.15 = 0.05 (giảm có kiểm soát)
        assert round(score, 2) == 0.05


class TestDuplicateEventReplayProtection:
    """
    Acceptance Criteria:
    'Replaying the same event cannot double-update mastery.'
    """

    def test_duplicate_event_replay_cannot_double_update_mastery(self, client: TestClient):
        headers = register_and_login(client)
        session_id, attempt_id = create_session_and_attempt(
            client,
            headers,
            knowledge_components=["csharp.property"],
        )

        resolve_payload = {
            "outcome": "resolved",
            "highest_hint_level": 0,
            "solution_revealed": False,
            "hints_used": 0,
        }

        # Lần gọi 1: Áp dụng thành công
        res1 = client.post(
            f"/api/sessions/{session_id}/attempts/{attempt_id}/resolve",
            json=resolve_payload,
            headers=headers,
        )
        assert res1.status_code == 200
        data1 = res1.json()
        assert data1["audit_records"][0]["new_score"] == 0.65

        # Kiểm tra điểm mastery hiện tại
        res_m1 = client.get("/api/mastery/csharp.property", headers=headers)
        assert res_m1.json()["mastery_score"] == 0.65
        assert res_m1.json()["success_count"] == 1

        # LẦN GỌI 2: REPLAY CÙNG MỘT EVENT TRÊN CÙNG ATTEMPT_ID
        res2 = client.post(
            f"/api/sessions/{session_id}/attempts/{attempt_id}/resolve",
            json=resolve_payload,
            headers=headers,
        )
        assert res2.status_code == 200
        data2 = res2.json()

        # Tuyệt đối không double-update: Điểm số vẫn giữ nguyên 0.65 (không bị cộng thành 0.80)!
        res_m2 = client.get("/api/mastery/csharp.property", headers=headers)
        assert res_m2.json()["mastery_score"] == 0.65
        assert res_m2.json()["success_count"] == 1  # Không bị cộng 2 lần

        # Số bản ghi audit vẫn chỉ có 1
        res_audits = client.get(f"/api/mastery/audit/{attempt_id}", headers=headers)
        assert len(res_audits.json()) == 1


class TestTransactionalRollbackAndUserIsolation:
    """Kiểm tra tính toàn vẹn giao dịch (rollback) và cách ly người dùng."""

    def test_unauthorized_user_cannot_resolve_other_user_attempt(self, client: TestClient):
        headers_a = register_and_login(client)
        headers_b = register_and_login(client)

        s_a, att_a = create_session_and_attempt(client, headers_a)

        # User B cố tình resolve attempt của User A
        res = client.post(
            f"/api/sessions/{s_a}/attempts/{att_a}/resolve",
            json={"outcome": "resolved"},
            headers=headers_b,
        )
        assert res.status_code == 404

    def test_transactional_rollback_preserves_state_on_failure(self, client: TestClient):
        """Nếu quá trình commit gặp lỗi, giao dịch rollback bảo toàn cả attempt và mastery."""
        headers = register_and_login(client)
        s_id, att_id = create_session_and_attempt(client, headers, knowledge_components=["csharp.method"])

        # Giả lập lỗi ném ra trước khi hoàn thành commit
        with patch.object(AsyncSession, "commit", side_effect=RuntimeError("Database failure simulated")):
            try:
                client.post(
                    f"/api/sessions/{s_id}/attempts/{att_id}/resolve",
                    json={"outcome": "resolved"},
                    headers=headers,
                )
            except Exception:
                pass

        # Sau sự cố rollback: Điểm mastery của kỹ năng csharp.method vẫn ở mức ban đầu (0.50)
        res_m = client.get("/api/mastery/csharp.method", headers=headers)
        assert res_m.json()["mastery_score"] == 0.50
        assert res_m.json()["success_count"] == 0

    def test_user_data_purge_cleans_audits(self, client: TestClient):
        """Xóa toàn bộ dữ liệu người dùng dọn sạch cả student_mastery_audit."""
        headers = register_and_login(client)
        s_id, att_id = create_session_and_attempt(client, headers)
        client.post(
            f"/api/sessions/{s_id}/attempts/{att_id}/resolve",
            json={"outcome": "resolved"},
            headers=headers,
        )

        res_check = client.get("/api/mastery/audit", headers=headers)
        assert len(res_check.json()) > 0

        # Xóa dữ liệu người dùng
        res_del = client.delete("/api/user-data", headers=headers)
        assert res_del.status_code == 200

        # Kiểm tra lại: audit history rỗng hoàn toàn
        res_after = client.get("/api/mastery/audit", headers=headers)
        assert res_after.status_code == 200
        assert len(res_after.json()) == 0
