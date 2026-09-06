import pytest

from tests.conftest import TestingSessionLocal
from app.models.learning_session import LearningSession, StudentAttempt
from app.models.mastery_audit import StudentMasteryAudit
from app.models.student_profile import StudentProfile
from app.models.student_skill_mastery import StudentSkillMastery
from app.models.user import User
from app.tutor.context_builder import (
    CodeSubmissionContext,
    LearnerPersonalizationContext,
    StudentContextBuilder,
    TokenBudgetConfig,
    truncate_text,
)
from app.tutor.prompts import SYSTEM_POLICY_V1, build_tutor_user_prompt
from app.tutor.service import TutorService


@pytest.fixture
def anyio_backend():
    return "asyncio"


class TestStudentContextBuilderSeparationAndBoundaries:
    """Kiểm tra phân tách ranh giới nghiêm ngặt giữa bằng chứng mã nguồn và cá nhân hóa người học."""

    def test_separation_of_code_evidence_and_learner_context(self):
        builder = StudentContextBuilder()

        submission = CodeSubmissionContext(
            problem_statement="Tạo lớp Car có thuộc tính Model.",
            student_code="public class Car { public string Model { get; set; } }",
            compiler_error=None,
            student_question="Thuộc tính này viết đúng chưa?",
            topic="csharp.property",
        )

        personalization = LearnerPersonalizationContext(
            student_profile={
                "display_name": "Nguyen Van A",
                "skill_level": "beginner",
                "preferred_explanation": "step_by_step",
                "solution_preference": "hint_first",
            },
            relevant_skill_mastery=[
                {"skill_id": "csharp.property", "skill_name": "Thuộc tính C#", "mastery_score": 0.35}
            ],
            recent_related_mistakes=[
                {"skill_id": "csharp.property", "reason": "Nhầm lẫn giữa field và property", "event_type": "unresolved_attempt"}
            ],
        )

        prompt = builder.build_user_prompt(submission, personalization, hint_level=1)

        # 1. Kiểm tra 2 khối phân định ranh giới
        assert "<submitted_code_evidence>" in prompt
        assert "</submitted_code_evidence>" in prompt
        assert "<learner_pedagogical_context>" in prompt
        assert "</learner_pedagogical_context>" in prompt

        # 2. Vùng bằng chứng mã nguồn chứa code và thẻ untrusted
        ev_start = prompt.find("<submitted_code_evidence>")
        ev_end = prompt.find("</submitted_code_evidence>")
        ev_content = prompt[ev_start:ev_end]

        assert "<untrusted_student_code>" in ev_content
        assert "public class Car" in ev_content
        assert "<untrusted_problem_statement>" in ev_content
        # Không được chứa thông tin hồ sơ trong phân vùng code evidence
        assert "Nguyen Van A" not in ev_content
        assert "step_by_step" not in ev_content

        # 3. Vùng cá nhân hóa chứa hồ sơ và điểm thuần thục
        ped_start = prompt.find("<learner_pedagogical_context>")
        ped_end = prompt.find("</learner_pedagogical_context>")
        ped_content = prompt[ped_start:ped_end]

        assert "Nguyen Van A" in ped_content
        assert "step_by_step" in ped_content
        assert "csharp.property" in ped_content
        assert "0.35" in ped_content
        # Không được chứa code bài nộp trong phân vùng learner context
        assert "public class Car" not in ped_content


class TestExclusionOfUnrelatedHistoricalSessions:
    """Acceptance: Add tests proving unrelated historical sessions are excluded."""

    def test_filter_relevant_skills_excludes_unrelated_skills(self):
        all_masteries = [
            {"skill_id": "csharp.property", "mastery_score": 0.4},
            {"skill_id": "csharp.inheritance", "mastery_score": 0.85},
            {"skill_id": "csharp.polymorphism", "mastery_score": 0.90},
            {"skill_id": "csharp.static", "mastery_score": 0.70},
        ]

        target_skills = ["csharp.property"]
        filtered = StudentContextBuilder.filter_relevant_skills(all_masteries, target_skills)

        assert len(filtered) == 1
        assert filtered[0]["skill_id"] == "csharp.property"
        assert filtered[0]["mastery_score"] == 0.4

        # Kỹ năng không liên quan bị loại bỏ hoàn toàn
        matched_ids = [s["skill_id"] for s in filtered]
        assert "csharp.inheritance" not in matched_ids
        assert "csharp.polymorphism" not in matched_ids
        assert "csharp.static" not in matched_ids

    def test_filter_recent_related_mistakes_excludes_unrelated_sessions(self):
        history_events = [
            {"skill_id": "csharp.property", "reason": "Quên khai báo get/set cho property", "event_type": "unresolved_attempt"},
            {"skill_id": "csharp.inheritance", "reason": "Lỗi gọi base constructor", "event_type": "unresolved_attempt"},
            {"skill_id": "csharp.polymorphism", "reason": "Thiếu từ khóa override", "event_type": "unresolved_attempt"},
            {"skill_id": "csharp.static", "reason": "Truy cập static field qua instance", "event_type": "unresolved_attempt"},
        ]

        target_skills = ["csharp.property"]
        filtered_mistakes = StudentContextBuilder.filter_recent_related_mistakes(history_events, target_skills)

        assert len(filtered_mistakes) == 1
        assert filtered_mistakes[0]["skill_id"] == "csharp.property"
        assert "Quên khai báo get/set" in filtered_mistakes[0]["reason"]

        # Các lỗi từ session thuộc chủ đề khác bị loại trừ 100%
        for m in filtered_mistakes:
            assert m["skill_id"] != "csharp.inheritance"
            assert m["skill_id"] != "csharp.polymorphism"
            assert m["skill_id"] != "csharp.static"

    def test_unrelated_topics_completely_absent_from_final_prompt(self):
        builder = StudentContextBuilder()

        # Dữ liệu chứa cả kỹ năng liên quan và kỹ năng khác
        all_masteries = [
            {"skill_id": "csharp.property", "mastery_score": 0.3},
            {"skill_id": "csharp.inheritance", "mastery_score": 0.95},
        ]
        all_mistakes = [
            {"skill_id": "csharp.property", "reason": "Nhầm thuộc tính với trường dữ liệu"},
            {"skill_id": "csharp.inheritance", "reason": "Lỗi đa kế thừa trong C#"},
        ]

        target_skills = ["csharp.property"]
        rel_masteries = builder.filter_relevant_skills(all_masteries, target_skills)
        rel_mistakes = builder.filter_recent_related_mistakes(all_mistakes, target_skills)

        submission = CodeSubmissionContext(
            problem_statement="Khai báo thuộc tính Age trong class Person.",
            student_code="class Person { int Age; }",
            topic="csharp.property",
        )
        personalization = LearnerPersonalizationContext(
            student_profile={"skill_level": "beginner"},
            relevant_skill_mastery=rel_masteries,
            recent_related_mistakes=rel_mistakes,
        )

        prompt = builder.build_user_prompt(submission, personalization)

        # Kỹ năng liên quan xuất hiện
        assert "csharp.property" in prompt
        assert "Nhầm thuộc tính với trường dữ liệu" in prompt

        # Kỹ năng từ phiên học không liên quan TUYỆT ĐỐI KHÔNG xuất hiện
        assert "csharp.inheritance" not in prompt
        assert "Lỗi đa kế thừa" not in prompt


class TestTokenBudgetingAndTruncation:
    """Kiểm tra cơ chế quản lý ngân sách token và cắt tỉa nội dung an toàn."""

    def test_truncate_text_under_limit(self):
        text = "Short text"
        assert truncate_text(text, 50) == "Short text"

    def test_truncate_text_over_limit_with_indicator(self):
        long_text = "A" * 1000
        truncated = truncate_text(long_text, 200, "mã nguồn")
        assert len(truncated) <= 200 + 10  # cho phép dung sai nhỏ của marker
        assert "[Đoạn mã nguồn đã được cắt bớt" in truncated

    def test_budget_limits_code_and_compiler_error(self):
        config = TokenBudgetConfig(
            max_problem_chars=100,
            max_code_chars=200,
            max_compiler_error_chars=150,
            max_relevant_skills=2,
            max_recent_mistakes=2,
            max_total_user_prompt_chars=2500,
        )
        builder = StudentContextBuilder(config)

        submission = CodeSubmissionContext(
            problem_statement="P" * 500,
            student_code="C" * 1000,
            compiler_error="E" * 800,
        )

        prompt = builder.build_user_prompt(submission)

        assert "[Đoạn đề bài đã được cắt bớt" in prompt
        assert "[Đoạn mã nguồn đã được cắt bớt" in prompt
        assert "[Đoạn lỗi biên dịch đã được cắt bớt" in prompt

    def test_budget_limits_number_of_skills_and_mistakes(self):
        config = TokenBudgetConfig(max_relevant_skills=3, max_recent_mistakes=2)
        builder = StudentContextBuilder(config)

        many_skills = [{"skill_id": f"csharp.skill_{i}", "mastery_score": 0.5} for i in range(10)]
        many_mistakes = [{"skill_id": "csharp.property", "reason": f"Lỗi số {i}"} for i in range(10)]

        personalization = LearnerPersonalizationContext(
            relevant_skill_mastery=many_skills,
            recent_related_mistakes=many_mistakes,
        )
        submission = CodeSubmissionContext(problem_statement="Test", student_code="class A {}")

        prompt = builder.build_user_prompt(submission, personalization)

        # Chỉ có tối đa 3 kỹ năng
        assert "csharp.skill_0" in prompt
        assert "csharp.skill_2" in prompt
        assert "csharp.skill_3" not in prompt

        # Chỉ có tối đa 2 lỗi sai
        assert "Lỗi số 0" in prompt
        assert "Lỗi số 1" in prompt
        assert "Lỗi số 2" not in prompt


class TestPedagogicalInvariantAndPolicy:
    """Kiểm tra nguyên tắc bất biến: Mastery không được dùng làm bằng chứng kết luận code có bug."""

    def test_pedagogical_invariant_notice_in_learner_context(self):
        builder = StudentContextBuilder()
        submission = CodeSubmissionContext(problem_statement="Test", student_code="class A {}")
        personalization = LearnerPersonalizationContext(
            relevant_skill_mastery=[{"skill_id": "csharp.property", "mastery_score": 0.05}]  # Điểm rất thấp!
        )

        prompt = builder.build_user_prompt(submission, personalization)

        # Cảnh báo sư phạm bất biến phải hiện diện trong prompt
        assert "PEDAGOGICAL INVARIANT" in prompt
        assert "TUYỆT ĐỐI KHÔNG ĐƯỢC coi điểm thuần thục thấp hoặc sai lầm trước đây là bằng chứng" in prompt

    def test_system_policy_includes_no_mastery_contamination_tenet(self):
        policy = SYSTEM_POLICY_V1

        # Tenet 7: BẢO VỆ TÍNH KHÁCH QUAN CỦA BẰNG CHỨNG & KHÔNG Ô NHIỄM BỞI MASTERY
        assert "NO MASTERY CONTAMINATION" in policy
        assert "PHẢI CĂN CỨ DUY NHẤT trên <submitted_code_evidence>" in policy
        assert "TUYỆT ĐỐI KHÔNG ĐƯỢC DÙNG điểm mastery thấp hoặc sai lầm trước đây làm căn cứ suy diễn" in policy

    def test_adapts_explanation_style_based_on_student_profile(self):
        builder = StudentContextBuilder()
        submission = CodeSubmissionContext(problem_statement="Đề bài", student_code="class A {}")

        # Profile 1: concise, balanced
        p1 = LearnerPersonalizationContext(
            student_profile={
                "preferred_explanation": "concise",
                "solution_preference": "balanced",
            }
        )
        prompt1 = builder.build_user_prompt(submission, p1)
        assert "súc tích, ngắn gọn" in prompt1
        assert "cân bằng giữa gợi ý và lời giải" in prompt1

        # Profile 2: example_first, hint_first
        p2 = LearnerPersonalizationContext(
            student_profile={
                "preferred_explanation": "example_first",
                "solution_preference": "hint_first",
            }
        )
        prompt2 = builder.build_user_prompt(submission, p2)
        assert "ưu tiên ví dụ minh họa trực quan" in prompt2
        assert "ưu tiên gợi ý định hướng trước lời giải" in prompt2

    def test_guest_mode_or_empty_learner_context(self):
        builder = StudentContextBuilder()
        submission = CodeSubmissionContext(problem_statement="Đề bài guest", student_code="class Guest {}")

        # Guest không có profile
        prompt = builder.build_user_prompt(submission, personalization=None)

        assert "<submitted_code_evidence>" in prompt
        assert "<learner_pedagogical_context>" in prompt
        assert "Chưa có dữ liệu độ thuần thục kỹ năng liên quan" in prompt
        assert "Không ghi nhận ngộ nhận hay lỗi sai trước đó" in prompt


class TestContextBuilderDatabaseIntegration:
    """Kiểm tra tích hợp tải dữ liệu người học từ Database (loại bỏ phiên không liên quan)."""

    @pytest.mark.anyio
    async def test_load_and_build_learner_context_from_db(self):
        async with TestingSessionLocal() as db_session:
            # 1. Tạo user và student profile
            user = User(email="student_ctx@test.com", hashed_password="pw", is_active=True)
            db_session.add(user)
            await db_session.commit()
            await db_session.refresh(user)

            profile = StudentProfile(
                user_id=user.id,
                display_name="Nguyen Van Context",
                preferred_explanation="step_by_step",
                solution_preference="hint_first",
            )
            db_session.add(profile)

            # 2. Tạo 2 bản ghi mastery: 1 liên quan (property), 1 không liên quan (inheritance)
            m_prop = StudentSkillMastery(
                user_id=user.id,
                skill_id="csharp.property",
                mastery_score=0.45,
            )
            m_inh = StudentSkillMastery(
                user_id=user.id,
                skill_id="csharp.inheritance",
                mastery_score=0.90,
            )
            db_session.add_all([m_prop, m_inh])
            await db_session.commit()

            # 3. Tạo 2 phiên học và 2 lần thử
            sess_prop = LearningSession(user_id=user.id, title="Học thuộc tính C#", topic="csharp.property")
            sess_inh = LearningSession(user_id=user.id, title="Học kế thừa C#", topic="csharp.inheritance")
            db_session.add_all([sess_prop, sess_inh])
            await db_session.commit()
            await db_session.refresh(sess_prop)
            await db_session.refresh(sess_inh)

            att_prop = StudentAttempt(
                session_id=sess_prop.id,
                problem_reference="Tạo property",
                success_state="unresolved_attempt",
                diagnosis={"knowledge_components": ["csharp.property"]},
            )
            att_inh = StudentAttempt(
                session_id=sess_inh.id,
                problem_reference="Kế thừa",
                success_state="unresolved_attempt",
                diagnosis={"knowledge_components": ["csharp.inheritance"]},
            )
            db_session.add_all([att_prop, att_inh])
            await db_session.commit()
            await db_session.refresh(att_prop)
            await db_session.refresh(att_inh)

            # Tạo audit logs
            audit_prop = StudentMasteryAudit(
                user_id=user.id,
                skill_id="csharp.property",
                attempt_id=att_prop.id,
                event_type="unresolved_attempt",
                previous_score=0.6,
                new_score=0.45,
                reason="Lỗi cú pháp getter trong property",
            )
            audit_inh = StudentMasteryAudit(
                user_id=user.id,
                skill_id="csharp.inheritance",
                attempt_id=att_inh.id,
                event_type="unresolved_attempt",
                previous_score=0.95,
                new_score=0.90,
                reason="Lỗi gọi base constructor khi kế thừa",
            )
            db_session.add_all([audit_prop, audit_inh])
            await db_session.commit()

            # 4. Gọi load_and_build_learner_context chỉ với target skill = ["csharp.property"]
            ctx = await StudentContextBuilder.load_and_build_learner_context(
                db=db_session,
                user_id=user.id,
                relevant_skills=["csharp.property"],
            )

            # 5. Kiểm tra kết quả
            assert ctx.student_profile is not None
            assert ctx.student_profile["display_name"] == "Nguyen Van Context"
            assert ctx.student_profile["preferred_explanation"] == "step_by_step"

            # Kỹ năng liên quan: chỉ có csharp.property
            assert len(ctx.relevant_skill_mastery) == 1
            assert ctx.relevant_skill_mastery[0]["skill_id"] == "csharp.property"
            assert ctx.relevant_skill_mastery[0]["mastery_score"] == 0.45

            # Lỗi sai gần đây: chỉ có csharp.property, hoàn toàn loại bỏ csharp.inheritance
            assert len(ctx.recent_related_mistakes) == 1
            assert ctx.recent_related_mistakes[0]["skill_id"] == "csharp.property"
            assert "Lỗi cú pháp getter" in ctx.recent_related_mistakes[0]["reason"]
