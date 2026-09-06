import asyncio
from uuid import uuid4
import pytest
from sqlalchemy import select

from app.models.analysis_session import AnalysisSession
from app.models.consent import Consent
from app.models.learning_session import LearningSession, StudentAttempt, TutorMessage
from app.models.mastery_audit import StudentMasteryAudit
from app.models.student_profile import StudentProfile
from app.models.student_skill_mastery import StudentSkillMastery
from app.schemas.tutor_schema import DiagnosisCategory, TutorDiagnosis, TutorResponse
from app.services.db_store import HistoryRepository
from tests.conftest import TestingSessionLocal


def register_and_login(client, email: str | None = None):
    email = email or f"student-{uuid4()}@example.com"
    password = "StrongPassword123!"
    client.post("/api/register", json={"email": email, "password": password})
    token_response = client.post(
        "/api/token",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    token = token_response.json()["access_token"]
    user_id = client.get("/api/me", headers={"Authorization": f"Bearer {token}"}).json()["id"]
    return {"Authorization": f"Bearer {token}"}, user_id


def create_sample_tutor_result(issue_type="encapsulation_break", hint_level=1):
    diagnosis = TutorDiagnosis(
        issue_type=issue_type,
        category=DiagnosisCategory.CONCEPTUAL_MISUSE,
        severity="error",
        confidence=0.92,
        explanation="Field public vi phạm tính đóng gói.",
    )
    return TutorResponse(
        diagnosis=diagnosis,
        knowledge_components=["oop.encapsulation.access_modifiers"],
        hint_level=hint_level,
        highest_hint_level_used=hint_level,
        solution_revealed=False,
        tutor_response="Hãy dùng private field và public property.",
        teaching_strategy="socratic",
        next_action="Thử sửa lại phạm vi truy cập.",
    )


def test_delete_all_user_data_removes_tutoring_models_and_preserves_vision_consent(client):
    """
    Xác minh một thao tác DELETE /api/user-data xóa sạch:
    - student profile
    - sessions
    - attempts
    - messages
    - mastery
    - audit logs
    - stored inputs
    - general consent
    Và BẢO LƯU Vision-specific consent.
    """
    headers, user_id = register_and_login(client)

    # 1. Tạo StudentProfile
    prof_res = client.post(
        "/api/student-profile",
        headers=headers,
        json={
            "display_name": "Nguyen Van A",
            "programming_language": "csharp",
            "skill_level": "beginner",
            "current_course": "CS101 OOP",
            "preferred_explanation": "step_by_step",
            "solution_preference": "hint_first",
        },
    )
    assert prof_res.status_code == 200

    # 2. Tạo LearningSession + StudentAttempt + TutorMessage
    session_res = client.post(
        "/api/sessions",
        headers=headers,
        json={
            "title": "Buổi học Encapsulation",
            "language": "csharp",
            "topic": "Encapsulation",
            "initial_problem": "Đề bài ẩn",
            "initial_code": "public class BankAccount { public double balance; }",
            "save_input": True,
        },
    )
    assert session_res.status_code == 201
    created_session_id = session_res.json()["id"]
    created_attempt_id = session_res.json()["attempts"][0]["id"]

    # Thêm message
    msg_res = client.post(
        f"/api/sessions/{created_session_id}/messages",
        headers=headers,
        json={
            "role": "student",
            "content": "Làm sao để sửa field này thành property?",
        },
    )
    assert msg_res.status_code == 201

    # 3. Tạo StudentSkillMastery & StudentMasteryAudit
    async def seed_mastery_and_consents():
        async with TestingSessionLocal() as db:
            mastery = StudentSkillMastery(
                user_id=user_id,
                skill_id="oop.encapsulation.access_modifiers",
                mastery_score=0.75,
                success_count=3,
                failure_count=1,
                hint_count=2,
            )
            db.add(mastery)

            # Audit
            audit = StudentMasteryAudit(
                user_id=user_id,
                skill_id="oop.encapsulation.access_modifiers",
                previous_score=0.5,
                new_score=0.75,
                event_type="independent_success",
                attempt_id=created_attempt_id,
                reason="Học viên giải độc lập thành công.",
            )
            db.add(audit)

            # Consents
            consent_general = Consent(
                user_id=user_id,
                consent_type="privacy_settings",
                history_enabled=True,
                save_input=True,
                save_result=True,
                is_accepted=True,
            )
            consent_analysis = Consent(
                user_id=user_id,
                consent_type="analysis_submission",
                history_enabled=True,
                save_input=True,
                save_result=True,
                is_accepted=True,
            )
            consent_vision = Consent(
                user_id=user_id,
                consent_type="vision",
                history_enabled=True,
                save_input=False,
                save_result=False,
                is_accepted=True,
            )
            db.add_all([consent_general, consent_analysis, consent_vision])
            await db.commit()

    asyncio.run(seed_mastery_and_consents())

    # 4. Tạo AnalysisSession (tutor session có stored input)
    async def seed_analysis_session():
        async with TestingSessionLocal() as db:
            await HistoryRepository.save_tutor_session(
                db,
                user_id,
                problem_statement="Xây dựng class bảo vệ số dư",
                student_code="public double balance;",
                compiler_error="CS0169: The field is never used",
                topic="Encapsulation",
                result=create_sample_tutor_result(),
                save_input=True,
                save_result=True,
            )

    asyncio.run(seed_analysis_session())

    # Kiểm tra trước khi xóa: các bảng đều có dữ liệu
    async def verify_before():
        async with TestingSessionLocal() as db:
            prof = (await db.execute(select(StudentProfile).where(StudentProfile.user_id == user_id))).scalars().all()
            sess = (await db.execute(select(LearningSession).where(LearningSession.user_id == user_id))).scalars().all()
            att = (await db.execute(select(StudentAttempt).where(StudentAttempt.session_id == created_session_id))).scalars().all()
            msgs = (await db.execute(select(TutorMessage).where(TutorMessage.session_id == created_session_id))).scalars().all()
            mst = (await db.execute(select(StudentSkillMastery).where(StudentSkillMastery.user_id == user_id))).scalars().all()
            aud = (await db.execute(select(StudentMasteryAudit).where(StudentMasteryAudit.user_id == user_id))).scalars().all()
            ana = (await db.execute(select(AnalysisSession).where(AnalysisSession.user_id == user_id))).scalars().all()
            cons = (await db.execute(select(Consent).where(Consent.user_id == user_id))).scalars().all()

            assert len(prof) == 1
            assert len(sess) == 1
            assert len(att) == 1
            assert len(msgs) >= 1
            assert len(mst) == 1
            assert len(aud) == 1
            assert len(ana) == 1
            assert len(cons) == 3

    asyncio.run(verify_before())

    # 5. Gọi một thao tác xóa duy nhất: DELETE /api/user-data
    del_res = client.delete("/api/user-data", headers=headers)
    assert del_res.status_code == 200
    assert del_res.json() == {"deleted": True}

    # 6. Xác nhận toàn bộ dữ liệu học tập đã bị xóa sạch, DUY NHẤT Vision consent được giữ lại
    async def verify_after():
        async with TestingSessionLocal() as db:
            prof = (await db.execute(select(StudentProfile).where(StudentProfile.user_id == user_id))).scalars().all()
            sess = (await db.execute(select(LearningSession).where(LearningSession.user_id == user_id))).scalars().all()
            att = (await db.execute(select(StudentAttempt).where(StudentAttempt.session_id == created_session_id))).scalars().all()
            msgs = (await db.execute(select(TutorMessage).where(TutorMessage.session_id == created_session_id))).scalars().all()
            mst = (await db.execute(select(StudentSkillMastery).where(StudentSkillMastery.user_id == user_id))).scalars().all()
            aud = (await db.execute(select(StudentMasteryAudit).where(StudentMasteryAudit.user_id == user_id))).scalars().all()
            ana = (await db.execute(select(AnalysisSession).where(AnalysisSession.user_id == user_id))).scalars().all()
            cons = (await db.execute(select(Consent).where(Consent.user_id == user_id))).scalars().all()

            assert len(prof) == 0, "StudentProfile phải bị xóa sạch"
            assert len(sess) == 0, "LearningSession phải bị xóa sạch"
            assert len(att) == 0, "StudentAttempt phải bị xóa sạch"
            assert len(msgs) == 0, "TutorMessage phải bị xóa sạch"
            assert len(mst) == 0, "StudentSkillMastery phải bị xóa sạch"
            assert len(aud) == 0, "StudentMasteryAudit phải bị xóa sạch"
            assert len(ana) == 0, "AnalysisSession phải bị xóa sạch"

            # Chỉ giữ lại duy nhất consent 'vision'
            assert len(cons) == 1, "Chỉ duy nhất Vision consent được bảo lưu"
            assert cons[0].consent_type == "vision"
            assert cons[0].is_accepted is True

    asyncio.run(verify_after())


def test_save_input_vs_save_result_storage_invariants(client):
    """
    Xác minh các quy tắc bất biến về quyền riêng tư:
    1. Default / save_input=False: student code KHÔNG được lưu (chat_text=None, không có trong JSON metadata).
       Đề bài không bị rò rỉ vào context_note hay JSON metadata.
       Lỗi biên dịch không được lưu vào JSON metadata.
    2. save_result=True: lưu chẩn đoán lỗi, kỹ năng, hint usage, success state, summary.
    3. save_input=True: cho phép lưu tường minh problem statement, student code, compiler error.
    """
    headers, user_id = register_and_login(client)

    async def run_cases():
        async with TestingSessionLocal() as db:
            # Case 1: save_result=True, save_input=False (Default)
            saved_default = await HistoryRepository.save_tutor_session(
                db,
                user_id,
                problem_statement="Đề bài bí mật không được lưu",
                student_code="private int secretNumber = 42;",
                compiler_error="CS0103: The name 'secretNumber' does not exist",
                topic="Access Modifiers",
                result=create_sample_tutor_result(),
                save_input=False,
                save_result=True,
            )
            assert saved_default is not None
            # Student code KHÔNG được lưu
            assert saved_default.chat_text is None
            assert saved_default.emotion_distribution.get("student_code") is None
            # Đề bài và lỗi biên dịch KHÔNG được lưu
            assert saved_default.emotion_distribution.get("problem_statement") is None
            assert saved_default.emotion_distribution.get("compiler_error") is None
            # context_note KHÔNG được chứa đề bài
            assert "Đề bài bí mật" not in saved_default.context_note
            assert saved_default.context_note == "Chủ đề: Access Modifiers"
            # save_result lưu đầy đủ thông tin sư phạm
            assert saved_default.summary.startswith("Chẩn đoán OOP:")
            assert saved_default.emotion_distribution["knowledge_components"] == ["oop.encapsulation.access_modifiers"]
            assert saved_default.emotion_distribution["hint_level"] == 1
            assert saved_default.emotion_distribution["success_state"] == "in_progress"
            assert saved_default.emotion_distribution["diagnosis"]["issue_type"] == "encapsulation_break"

            # Case 2: save_result=True, save_input=True (Explicit Consent)
            saved_explicit = await HistoryRepository.save_tutor_session(
                db,
                user_id,
                problem_statement="Viết class quản lý xe hơi với CarId",
                student_code="public class Car { public int CarId { get; set; } }",
                compiler_error="No compiler errors",
                topic="Properties",
                result=create_sample_tutor_result(issue_type="property_best_practice", hint_level=2),
                save_input=True,
                save_result=True,
            )
            assert saved_explicit is not None
            # Student code ĐƯỢC LƯU
            assert saved_explicit.chat_text == "public class Car { public int CarId { get; set; } }"
            assert saved_explicit.emotion_distribution["student_code"] == "public class Car { public int CarId { get; set; } }"
            # Đề bài và lỗi biên dịch ĐƯỢC LƯU
            assert saved_explicit.emotion_distribution["problem_statement"] == "Viết class quản lý xe hơi với CarId"
            assert saved_explicit.emotion_distribution["compiler_error"] == "No compiler errors"
            assert "Viết class quản lý xe hơi" in saved_explicit.context_note

    asyncio.run(run_cases())


def test_delete_all_user_data_is_strictly_scoped_to_requesting_user(client):
    """
    Xác minh việc xóa dữ liệu người dùng A hoàn toàn không ảnh hưởng đến người dùng B.
    """
    headers_a, user_a_id = register_and_login(client)
    headers_b, user_b_id = register_and_login(client)

    # User A và User B cùng tạo session
    res_a = client.post(
        "/api/sessions",
        headers=headers_a,
        json={"title": "Session của A", "language": "csharp", "topic": "OOP A"},
    )
    res_b = client.post(
        "/api/sessions",
        headers=headers_b,
        json={"title": "Session của B", "language": "csharp", "topic": "OOP B"},
    )
    assert res_a.status_code == 201
    assert res_b.status_code == 201
    session_b_id = res_b.json()["id"]

    # Thêm mastery và consent cho cả 2
    async def seed_both():
        async with TestingSessionLocal() as db:
            db.add(StudentSkillMastery(user_id=user_a_id, skill_id="oop.a", mastery_score=0.5))
            db.add(StudentSkillMastery(user_id=user_b_id, skill_id="oop.b", mastery_score=0.9))
            db.add(Consent(user_id=user_a_id, consent_type="privacy_settings", is_accepted=True))
            db.add(Consent(user_id=user_b_id, consent_type="privacy_settings", is_accepted=True))
            db.add(Consent(user_id=user_b_id, consent_type="vision", is_accepted=True))
            await db.commit()

    asyncio.run(seed_both())

    # User A thực hiện xóa
    del_a = client.delete("/api/user-data", headers=headers_a)
    assert del_a.status_code == 200

    # Dữ liệu của User B phải hoàn toàn nguyên vẹn
    async def verify_user_b():
        async with TestingSessionLocal() as db:
            sess_b = (await db.execute(select(LearningSession).where(LearningSession.user_id == user_b_id))).scalars().all()
            mst_b = (await db.execute(select(StudentSkillMastery).where(StudentSkillMastery.user_id == user_b_id))).scalars().all()
            cons_b = (await db.execute(select(Consent).where(Consent.user_id == user_b_id))).scalars().all()

            assert len(sess_b) == 1
            assert sess_b[0].id == session_b_id
            assert len(mst_b) == 1
            assert mst_b[0].skill_id == "oop.b"
            assert mst_b[0].mastery_score == 0.9
            assert len(cons_b) == 2  # cả privacy_settings và vision của B còn nguyên

    asyncio.run(verify_user_b())
