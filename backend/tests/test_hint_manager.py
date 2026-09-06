import pytest
from app.schemas.tutor_schema import (
    DiagnosisCategory,
    PossibleMisconception,
    TutorDiagnosis,
    TutorEvidence,
    TutorRequest,
    TutorResponse,
)
from app.tutor.hint_manager import (
    HintManager,
    HintPayload,
    HintSessionState,
)
from app.tutor.provider import DeterministicMockTutorProvider
from app.tutor.service import TutorService


@pytest.fixture
def shadowing_diagnosis() -> TutorDiagnosis:
    """Chẩn đoán lỗi parameter/field shadowing."""
    return TutorDiagnosis(
        category=DiagnosisCategory.LOGIC_ERROR,
        issue_type="parameter_field_shadowing",
        location="dòng 7 trong constructor Dog(string name)",
        severity="error",
        confidence=0.92,
        evidence=TutorEvidence(code="name = name;", reason="Phép gán tham số cục bộ vào chính nó"),
        knowledge_components=["csharp.oop.constructor_assignment", "csharp.oop.this_keyword"],
        possible_misconception=PossibleMisconception(
            type="scope_confusion",
            description="Sinh viên nhầm lẫn giữa tham số cục bộ và trường thực thể khi trùng tên.",
            confidence=0.88,
        ),
    )


@pytest.fixture
def recursive_getter_diagnosis() -> TutorDiagnosis:
    """Chẩn đoán lỗi recursive property getter."""
    return TutorDiagnosis(
        category=DiagnosisCategory.RUNTIME_ERROR,
        issue_type="recursive_property_accessor",
        location="dòng 6 trong getter Name",
        severity="error",
        confidence=0.95,
        evidence=TutorEvidence(code="return Name;", reason="Gọi getter đệ quy dẫn đến StackOverflowException"),
        knowledge_components=["csharp.oop.properties_backing_field"],
    )


class TestHintSessionState:
    """Kiểm tra tính tất định của quản lý trạng thái phiên học."""

    def test_initial_session_state_defaults(self):
        state = HintSessionState(session_id="test_session_1")
        assert state.session_id == "test_session_1"
        assert state.current_hint_level == 1
        assert state.highest_hint_level_used == 1
        assert state.solution_revealed is False

    def test_advance_deterministic_sequential(self):
        state = HintSessionState(session_id="test_seq")
        
        # Advance 1 -> 2
        lvl = state.advance()
        assert lvl == 2
        assert state.current_hint_level == 2
        assert state.highest_hint_level_used == 2
        assert state.solution_revealed is False

        # Advance 2 -> 3
        lvl = state.advance()
        assert lvl == 3
        assert state.current_hint_level == 3
        assert state.highest_hint_level_used == 3
        assert state.solution_revealed is False

        # Advance 3 -> 4
        lvl = state.advance()
        assert lvl == 4
        assert state.current_hint_level == 4
        assert state.highest_hint_level_used == 4
        assert state.solution_revealed is True

        # Advance capped at 4
        lvl = state.advance()
        assert lvl == 4
        assert state.current_hint_level == 4
        assert state.highest_hint_level_used == 4
        assert state.solution_revealed is True

    def test_prevent_automatic_jump_from_1_to_4(self):
        """Do not automatically jump from level 1 to level 4."""
        state = HintSessionState(session_id="no_jump")
        assert state.current_hint_level == 1

        # Request jump to level 4 without explicit permission
        lvl = state.advance(requested_level=4, allow_jump_to_solution=False)
        assert lvl == 2  # Throttled to level 2 for pedagogical safety
        assert state.current_hint_level == 2
        assert state.highest_hint_level_used == 2
        assert state.solution_revealed is False

    def test_allow_jump_to_solution_when_explicitly_permitted(self):
        state = HintSessionState(session_id="explicit_jump")
        lvl = state.advance(requested_level=4, allow_jump_to_solution=True)
        assert lvl == 4
        assert state.current_hint_level == 4
        assert state.highest_hint_level_used == 4
        assert state.solution_revealed is True

    def test_highest_hint_level_used_remains_highest_on_step_back(self):
        state = HintSessionState(session_id="step_back")
        state.advance(requested_level=3)
        assert state.highest_hint_level_used == 3

        # Step back to level 2
        state.advance(requested_level=2)
        assert state.current_hint_level == 2
        assert state.highest_hint_level_used == 3  # Keeps highest
        assert state.solution_revealed is False


class TestHintManager:
    """Kiểm tra bộ điều phối HintManager."""

    def test_get_or_create_and_advance(self):
        manager = HintManager()
        session = manager.get_or_create_session("sess_100")
        assert session.current_hint_level == 1

        # Request next hint
        updated = manager.advance_hint("sess_100")
        assert updated.current_hint_level == 2
        assert updated.highest_hint_level_used == 2

    def test_reset_session(self):
        manager = HintManager()
        manager.advance_hint("sess_200", requested_level=3)
        assert manager.get_or_create_session("sess_200").current_hint_level == 3

        reset_state = manager.reset_session("sess_200")
        assert reset_state.current_hint_level == 1
        assert reset_state.highest_hint_level_used == 1
        assert reset_state.solution_revealed is False

    def test_pedagogical_safety_validation(self):
        valid, _ = HintManager.validate_pedagogical_safety(hint_level=1, solution_revealed=False)
        assert valid is True

        valid, _ = HintManager.validate_pedagogical_safety(hint_level=3, solution_revealed=False)
        assert valid is True

        valid, msg = HintManager.validate_pedagogical_safety(hint_level=2, solution_revealed=True)
        assert valid is False
        assert "Vi phạm sư phạm" in msg

        valid, _ = HintManager.validate_pedagogical_safety(hint_level=4, solution_revealed=True)
        assert valid is True


class TestProgressiveHintLevels:
    """
    Kiểm tra 4 cấp độ gợi ý tiến dần (Level 1..4):
    - Same diagnosis can produce progressively more explicit help.
    - Level 1-3 do not intentionally reveal complete answer.
    - Level 4 reveals explicit complete code and explanation.
    """

    def test_all_four_levels_for_shadowing(self, shadowing_diagnosis):
        student_code = "public class Dog { string name; public Dog(string name) { name = name; } }"
        
        # Level 1: Socratic question (No exact repair)
        h1 = HintManager.generate_progressive_hint(shadowing_diagnosis, hint_level=1, student_code=student_code)
        assert h1.hint_level == 1
        assert h1.teaching_strategy == "socratic_questioning"
        assert h1.solution_revealed is False
        assert "this.name = name;" not in h1.tutor_response
        assert "?" in h1.tutor_response  # Contains question mark for Socratic question

        # Level 2: Conceptual explanation (OOP concepts, no corrected code)
        h2 = HintManager.generate_progressive_hint(shadowing_diagnosis, hint_level=2, student_code=student_code)
        assert h2.hint_level == 2
        assert h2.teaching_strategy == "conceptual_explanation"
        assert h2.solution_revealed is False
        assert "Variable Shadowing" in h2.tutor_response or "phạm vi" in h2.tutor_response.lower()
        assert "this.name = name;" not in h2.tutor_response

        # Level 3: Directed hint (Specific location and direction, avoid full code block)
        h3 = HintManager.generate_progressive_hint(shadowing_diagnosis, hint_level=3, student_code=student_code)
        assert h3.hint_level == 3
        assert h3.teaching_strategy == "directed_hint"
        assert h3.solution_revealed is False
        assert "this." in h3.tutor_response
        assert "```csharp" not in h3.tutor_response  # Avoids full code block

        # Level 4: Explicit solution (Complete code + beginner-level explanation)
        h4 = HintManager.generate_progressive_hint(shadowing_diagnosis, hint_level=4, student_code=student_code)
        assert h4.hint_level == 4
        assert h4.teaching_strategy == "explicit_solution"
        assert h4.solution_revealed is True
        assert "this.name = name;" in h4.tutor_response
        assert "```csharp" in h4.tutor_response

        # Verification of increasing explicitness:
        # L1 is shorter/more interrogative, L4 contains code block and explicit explanation
        assert len(h4.tutor_response) > len(h1.tutor_response)

    def test_all_four_levels_for_recursive_getter(self, recursive_getter_diagnosis):
        student_code = "public class Student { private string _name; public string Name { get { return Name; } } }"

        h1 = HintManager.generate_progressive_hint(recursive_getter_diagnosis, hint_level=1, student_code=student_code)
        assert h1.hint_level == 1
        assert h1.solution_revealed is False
        assert "return _name;" not in h1.tutor_response
        assert "?" in h1.tutor_response

        h2 = HintManager.generate_progressive_hint(recursive_getter_diagnosis, hint_level=2, student_code=student_code)
        assert h2.hint_level == 2
        assert h2.solution_revealed is False
        assert "backing field" in h2.tutor_response.lower()
        assert "return _name;" not in h2.tutor_response

        h3 = HintManager.generate_progressive_hint(recursive_getter_diagnosis, hint_level=3, student_code=student_code)
        assert h3.hint_level == 3
        assert h3.solution_revealed is False
        assert "_name" in h3.tutor_response
        assert "```csharp" not in h3.tutor_response

        h4 = HintManager.generate_progressive_hint(recursive_getter_diagnosis, hint_level=4, student_code=student_code)
        assert h4.hint_level == 4
        assert h4.solution_revealed is True
        assert "return _name;" in h4.tutor_response


class TestTutorServiceHintIntegration:
    """Kiểm tra sự phối hợp giữa TutorService và HintManager."""

    @pytest.mark.anyio
    async def test_tutor_service_session_progression_and_anti_jump(self):
        provider = DeterministicMockTutorProvider()
        service = TutorService(llm_provider=provider)
        session_id = "student_session_abc"

        # Request 1 at hint_level 1
        req1 = TutorRequest(
            problem_statement="Tạo lớp Dog",
            student_code="public class Dog { string name; public Dog(string name) { name = name; } }",
            hint_level=1,
        )
        res1 = await service.generate_feedback(req1, session_id=session_id)
        assert res1.hint_level == 1
        assert res1.highest_hint_level_used == 1
        assert res1.solution_revealed is False

        # Request 2 attempting to jump directly to Level 4 without permission
        req2 = TutorRequest(
            problem_statement="Tạo lớp Dog",
            student_code="public class Dog { string name; public Dog(string name) { name = name; } }",
            hint_level=4,
        )
        res2 = await service.generate_feedback(req2, session_id=session_id, allow_jump_to_solution=False)
        # Anti-jump mechanism: from level 1 directly to 4 is throttled to level 2
        assert res2.hint_level == 2
        assert res2.highest_hint_level_used == 2
        assert res2.solution_revealed is False

    def test_tutor_service_request_next_hint(self, shadowing_diagnosis):
        provider = DeterministicMockTutorProvider()
        service = TutorService(llm_provider=provider)
        session_id = "student_session_xyz"

        # Init at level 1
        service.hint_manager.get_or_create_session(session_id, initial_level=1)

        # Request next hint directly
        next_hint = service.request_next_hint(
            session_id=session_id,
            diagnosis=shadowing_diagnosis,
        )
        assert next_hint.hint_level == 2
        assert next_hint.teaching_strategy == "conceptual_explanation"
        assert next_hint.solution_revealed is False
