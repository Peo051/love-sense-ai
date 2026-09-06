"""
Comprehensive Unit & Integration Tests for Student Skill Mastery Model (APT-018).

Verifies:
1. Initial mastery score is neutral/unknown (0.5), counters initialized to 0.
2. Deterministic update behavior: same sequence of events always produces identical updates.
3. Score clamping strictly bounded within [0.0, 1.0].
4. Distinct accurate updates for all 5 events:
   - successful independent solution (+0.15)
   - solution after hint level 1 (+0.10)
   - solution after hint level 2/3 (+0.05)
   - explicit solution level 4 (-0.05)
   - unresolved attempt (-0.15)
5. Event classification from practice attempts.
6. Formula documentation is transparent, inspectable, and complete.
7. API endpoints: /api/mastery/formula, /api/mastery, /api/mastery/{skill_id}, /api/mastery/practice.
8. Strict user isolation and cascade deletion on user data purge.
"""

from datetime import datetime, timezone
from uuid import uuid4
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.models.skill import SkillModel
from app.models.student_skill_mastery import StudentSkillMastery
from app.services.db_store import UserDataRepository
from app.services.mastery_store import MasteryRepository
from app.tutor.mastery import DeterministicMasteryModel, MasteryEvent
from app.tutor.skill_taxonomy import CSHARP_OOP_SKILLS_V1, SkillTaxonomy


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


class TestDeterministicMasteryFormulaUnit:
    """Kiểm tra các đặc tính toán học và sư phạm của công thức tất định V1."""

    def test_initial_mastery_is_neutral_unknown(self):
        """Khởi tạo phải ở mức 0.5 (neutral/unknown) thay vì giả định chắc chắn 0.0 hay 1.0."""
        assert DeterministicMasteryModel.INITIAL_MASTERY == 0.5
        assert DeterministicMasteryModel.MIN_SCORE == 0.0
        assert DeterministicMasteryModel.MAX_SCORE == 1.0

    def test_all_five_event_types_update_accurately(self):
        """Kiểm tra độ dịch chuyển điểm (delta) chính xác cho 5 sự kiện."""
        m = DeterministicMasteryModel

        # 1. Independent success: +0.15
        s1 = m.calculate_next_mastery(0.5, MasteryEvent.INDEPENDENT_SUCCESS)
        assert s1 == 0.65

        # 2. Hint L1 success: +0.10
        s2 = m.calculate_next_mastery(0.5, MasteryEvent.HINT_L1_SUCCESS)
        assert s2 == 0.60

        # 3. Hint L2/L3 success: +0.05
        s3 = m.calculate_next_mastery(0.5, MasteryEvent.HINT_L2_L3_SUCCESS)
        assert s3 == 0.55

        # 4. Explicit solution L4: -0.05
        s4 = m.calculate_next_mastery(0.5, MasteryEvent.EXPLICIT_SOLUTION_L4)
        assert s4 == 0.45

        # 5. Unresolved attempt: -0.15
        s5 = m.calculate_next_mastery(0.5, MasteryEvent.UNRESOLVED_ATTEMPT)
        assert s5 == 0.35

    def test_deterministic_guarantee_same_events_produce_same_mastery(self):
        """
        Acceptance Criteria:
        'Same events always produce same mastery updates.'
        """
        event_sequence = [
            MasteryEvent.INDEPENDENT_SUCCESS,
            MasteryEvent.HINT_L1_SUCCESS,
            MasteryEvent.UNRESOLVED_ATTEMPT,
            MasteryEvent.HINT_L2_L3_SUCCESS,
            MasteryEvent.EXPLICIT_SOLUTION_L4,
            MasteryEvent.INDEPENDENT_SUCCESS,
        ]

        def run_simulation():
            score = DeterministicMasteryModel.INITIAL_MASTERY
            history = [score]
            for ev in event_sequence:
                score = DeterministicMasteryModel.calculate_next_mastery(score, ev)
                history.append(score)
            return history

        result1 = run_simulation()
        result2 = run_simulation()
        result3 = run_simulation()

        assert result1 == result2 == result3
        # 0.5 -> 0.65 -> 0.75 -> 0.60 -> 0.65 -> 0.60 -> 0.75
        assert result1 == [0.5, 0.65, 0.75, 0.60, 0.65, 0.60, 0.75]

    def test_clamping_to_zero_and_one_boundaries(self):
        """Điểm số không bao giờ vượt quá [0.0, 1.0]."""
        m = DeterministicMasteryModel

        # Kiểm tra chặn trên (upper bound)
        score = 0.95
        score = m.calculate_next_mastery(score, MasteryEvent.INDEPENDENT_SUCCESS)
        assert score == 1.0
        # Thêm nhiều lần thành công liên tiếp vẫn kẹp 1.0
        for _ in range(5):
            score = m.calculate_next_mastery(score, MasteryEvent.INDEPENDENT_SUCCESS)
            assert score == 1.0

        # Kiểm tra chặn dưới (lower bound)
        score = 0.08
        score = m.calculate_next_mastery(score, MasteryEvent.UNRESOLVED_ATTEMPT)
        assert score == 0.0
        # Thêm nhiều lần thất bại liên tiếp vẫn kẹp 0.0
        for _ in range(5):
            score = m.calculate_next_mastery(score, MasteryEvent.UNRESOLVED_ATTEMPT)
            assert score == 0.0

    def test_classify_attempt_event(self):
        """Kiểm tra hàm phân loại kết quả lần thử của sinh viên."""
        classify = DeterministicMasteryModel.classify_attempt_event

        # 1. Giải thành công độc lập (0 hints, không mở đáp án)
        assert classify(resolved=True, highest_hint_level_used=0, solution_revealed=False) == MasteryEvent.INDEPENDENT_SUCCESS

        # 2. Giải thành công sau Hint Level 1
        assert classify(resolved=True, highest_hint_level_used=1, solution_revealed=False) == MasteryEvent.HINT_L1_SUCCESS

        # 3. Giải thành công sau Hint Level 2 hoặc 3
        assert classify(resolved=True, highest_hint_level_used=2, solution_revealed=False) == MasteryEvent.HINT_L2_L3_SUCCESS
        assert classify(resolved=True, highest_hint_level_used=3, solution_revealed=False) == MasteryEvent.HINT_L2_L3_SUCCESS

        # 4. Mở lời giải Level 4 (solution_revealed = True hoặc level >= 4)
        assert classify(resolved=True, highest_hint_level_used=4, solution_revealed=True) == MasteryEvent.EXPLICIT_SOLUTION_L4
        assert classify(resolved=False, highest_hint_level_used=4, solution_revealed=True) == MasteryEvent.EXPLICIT_SOLUTION_L4
        assert classify(resolved=False, highest_hint_level_used=3, solution_revealed=True) == MasteryEvent.EXPLICIT_SOLUTION_L4

        # 5. Bài chưa giải quyết được (resolved = False và chưa xem solution)
        assert classify(resolved=False, highest_hint_level_used=1, solution_revealed=False) == MasteryEvent.UNRESOLVED_ATTEMPT
        assert classify(resolved=False, highest_hint_level_used=0, solution_revealed=False) == MasteryEvent.UNRESOLVED_ATTEMPT

    def test_apply_event_to_state_updates_counters_and_timestamp(self):
        """apply_event_to_state cập nhật đúng các bộ đếm success, failure, hints và last_practiced_at."""
        now = datetime(2026, 9, 6, 12, 0, 0, tzinfo=timezone.utc)
        state1 = DeterministicMasteryModel.apply_event_to_state(
            current_score=0.5,
            success_count=2,
            failure_count=1,
            hint_count=3,
            event=MasteryEvent.INDEPENDENT_SUCCESS,
            hints_used_in_attempt=0,
            practice_time=now,
        )
        assert state1["mastery_score"] == 0.65
        assert state1["success_count"] == 3
        assert state1["failure_count"] == 1
        assert state1["hint_count"] == 3
        assert state1["last_practiced_at"] == now

        # Thất bại với 2 hints
        state2 = DeterministicMasteryModel.apply_event_to_state(
            current_score=state1["mastery_score"],
            success_count=state1["success_count"],
            failure_count=state1["failure_count"],
            hint_count=state1["hint_count"],
            event=MasteryEvent.UNRESOLVED_ATTEMPT,
            hints_used_in_attempt=2,
            practice_time=now,
        )
        assert state2["mastery_score"] == 0.50
        assert state2["success_count"] == 3
        assert state2["failure_count"] == 2
        assert state2["hint_count"] == 5

    def test_inspectable_formula_documentation(self):
        """
        Acceptance Criteria:
        'Formula is documented and inspectable.'
        """
        doc = DeterministicMasteryModel.get_formula_documentation()
        assert "formula_name" in doc
        assert doc["version"] == "v1"
        assert doc["initial_mastery"] == 0.5
        assert doc["score_bounds"] == [0.0, 1.0]
        assert "mathematical_formula" in doc
        assert "description" in doc
        assert "initial_state_explanation" in doc
        assert "clamping_rule" in doc

        # Đảm bảo đủ 5 sự kiện trong tài liệu
        for ev in MasteryEvent:
            assert ev.value in doc["event_deltas"]
            info = doc["event_deltas"][ev.value]
            assert "delta" in info
            assert "description" in info
            assert "pedagogical_rationale" in info


class TestMasteryAPIAndPersistence:
    """Kiểm tra API /api/mastery và tính toàn vẹn lưu trữ DB."""

    def test_get_mastery_formula_endpoint(self, client: TestClient):
        """Endpoint công khai /api/mastery/formula trả về tài liệu công thức đầy đủ."""
        res = client.get("/api/mastery/formula")
        assert res.status_code == 200
        data = res.json()
        assert data["formula_name"] == "Deterministic Piecewise Additive Mastery Rule"
        assert data["version"] == "v1"
        assert data["initial_mastery"] == 0.5
        assert len(data["event_deltas"]) == 5

    def test_get_masteries_initially_neutral_0_5(self, client: TestClient):
        """Sinh viên mới nhận danh sách kỹ năng ở mức trung tính 0.5 và counts = 0."""
        headers = register_and_login(client)
        res = client.get("/api/mastery", headers=headers)
        assert res.status_code == 200
        data = res.json()
        assert data["total_skills"] == len(CSHARP_OOP_SKILLS_V1)
        assert data["practiced_skills"] == 0
        assert data["average_mastery"] == 0.5
        for s in data["skills"]:
            assert s["mastery_score"] == 0.5
            assert s["success_count"] == 0
            assert s["failure_count"] == 0
            assert s["hint_count"] == 0
            assert s["last_practiced_at"] is None

    def test_record_practice_attempt_updates_mastery(self, client: TestClient):
        """Ghi nhận lần làm bài thành công làm tăng điểm và các bộ đếm."""
        headers = register_and_login(client)
        payload = {
            "skill_ids": ["csharp.property", "csharp.getter"],
            "event": "independent_success",
            "hints_used": 0,
        }
        res = client.post("/api/mastery/practice", json=payload, headers=headers)
        assert res.status_code == 200
        data = res.json()
        assert len(data) == 2
        for item in data:
            assert item["mastery_score"] == 0.65
            assert item["success_count"] == 1
            assert item["failure_count"] == 0
            assert item["hint_count"] == 0
            assert item["last_practiced_at"] is not None

        # Kiểm tra GET lại một kỹ năng cụ thể
        res_single = client.get("/api/mastery/csharp.property", headers=headers)
        assert res_single.status_code == 200
        single_data = res_single.json()
        assert single_data["skill_id"] == "csharp.property"
        assert single_data["mastery_score"] == 0.65
        assert single_data["success_count"] == 1

        # Lần 2: Sinh viên gặp khó khăn và cần gợi ý Level 1
        res_p2 = client.post(
            "/api/mastery/practice",
            json={
                "skill_ids": ["csharp.property"],
                "event": "hint_l1_success",
                "hints_used": 1,
            },
            headers=headers,
        )
        assert res_p2.status_code == 200
        data_p2 = res_p2.json()
        assert data_p2[0]["mastery_score"] == 0.75  # 0.65 + 0.10
        assert data_p2[0]["success_count"] == 2
        assert data_p2[0]["hint_count"] == 1

    def test_unsupported_skill_returns_404(self, client: TestClient):
        headers = register_and_login(client)
        res = client.get("/api/mastery/completely_invalid_skill_code", headers=headers)
        assert res.status_code == 404
        assert "không tồn tại" in res.json()["detail"]

    def test_unauthenticated_requests_rejected(self, client: TestClient):
        res = client.get("/api/mastery")
        assert res.status_code == 401

        res_post = client.post(
            "/api/mastery/practice",
            json={"skill_ids": ["csharp.property"], "event": "independent_success"},
        )
        assert res_post.status_code == 401

    def test_strict_user_ownership_mastery(self, client: TestClient):
        """Sinh viên A cập nhật bài làm không làm ảnh hưởng tới sinh viên B."""
        headers_a = register_and_login(client)
        headers_b = register_and_login(client)

        # Sinh viên A làm bài thành công
        client.post(
            "/api/mastery/practice",
            json={"skill_ids": ["csharp.constructor"], "event": "independent_success"},
            headers=headers_a,
        )

        # Kiểm tra A có điểm 0.65
        res_a = client.get("/api/mastery/csharp.constructor", headers=headers_a)
        assert res_a.json()["mastery_score"] == 0.65

        # Kiểm tra B vẫn giữ điểm trung tính ban đầu 0.50
        res_b = client.get("/api/mastery/csharp.constructor", headers=headers_b)
        assert res_b.json()["mastery_score"] == 0.50
        assert res_b.json()["success_count"] == 0

    def test_delete_user_data_cleans_masteries(self, client: TestClient):
        """Xóa toàn bộ dữ liệu người dùng dọn sạch cả bản ghi student_skill_mastery."""
        headers = register_and_login(client)
        client.post(
            "/api/mastery/practice",
            json={"skill_ids": ["csharp.static"], "event": "independent_success"},
            headers=headers,
        )

        res_check = client.get("/api/mastery/csharp.static", headers=headers)
        assert res_check.json()["mastery_score"] == 0.65
        assert res_check.json()["success_count"] == 1

        # Xóa dữ liệu
        res_del = client.delete("/api/user-data", headers=headers)
        assert res_del.status_code == 200

        # Kiểm tra lại: bản ghi đã bị xóa, fallback trạng thái trung tính 0.5
        res_after = client.get("/api/mastery/csharp.static", headers=headers)
        assert res_after.json()["mastery_score"] == 0.5
        assert res_after.json()["success_count"] == 0
