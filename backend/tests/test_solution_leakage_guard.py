import pytest
from app.schemas.tutor_schema import (
    DiagnosisCategory,
    PossibleMisconception,
    TutorDiagnosis,
    TutorEvidence,
    TutorRequest,
    TutorResponse,
)
from app.tutor.leakage_guard import LeakageCheckResult, SolutionLeakageGuard
from app.tutor.provider import DeterministicMockTutorProvider
from app.tutor.service import TutorService
from app.tutor.validator import TutorOutputValidator


@pytest.fixture
def base_diagnosis() -> TutorDiagnosis:
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
def sample_student_code() -> str:
    return """public class Dog {
    private string name;
    public Dog(string name) {
        name = name;
    }
}"""


@pytest.fixture
def sample_reference_solution() -> str:
    return """public class Dog {
    private string name;
    public Dog(string name) {
        this.name = name;
    }
}"""


class TestSolutionLeakageGuardDirectChecks:
    """Kiểm tra các phương thức kiểm định tất định trực tiếp (Deterministic checks first)."""

    def test_verbatim_reference_solution_blocked_at_early_levels(
        self, sample_student_code, sample_reference_solution
    ):
        leaked_response = f"Bạn hãy xem code giải hoàn chỉnh này:\n{sample_reference_solution}"
        
        # Level 1
        res1 = SolutionLeakageGuard.check_leakage(
            tutor_response_text=leaked_response,
            hint_level=1,
            student_code=sample_student_code,
            reference_solution=sample_reference_solution,
        )
        assert res1.has_leakage is True
        assert res1.leakage_type == "full_reference_verbatim"

        # Level 3
        res3 = SolutionLeakageGuard.check_leakage(
            tutor_response_text=leaked_response,
            hint_level=3,
            student_code=sample_student_code,
            reference_solution=sample_reference_solution,
        )
        assert res3.has_leakage is True
        assert res3.leakage_type == "full_reference_verbatim"

    def test_corrected_line_verbatim_blocked_at_early_levels(
        self, sample_student_code, sample_reference_solution
    ):
        leaked_response = "Để sửa lỗi này, bạn chỉ cần viết this.name = name; vào trong hàm."
        res = SolutionLeakageGuard.check_leakage(
            tutor_response_text=leaked_response,
            hint_level=1,
            student_code=sample_student_code,
            reference_solution=sample_reference_solution,
        )
        assert res.has_leakage is True
        assert res.leakage_type == "corrected_line_verbatim"

    def test_large_code_blocks_containing_repair_blocked(self, sample_student_code):
        leaked_response = (
            "Dưới đây là đoạn mã sửa:\n"
            "```csharp\n"
            "this.name = name;\n"
            "```\n"
            "Bạn thử lại nhé."
        )
        res1 = SolutionLeakageGuard.check_leakage(
            tutor_response_text=leaked_response,
            hint_level=1,
            student_code=sample_student_code,
        )
        assert res1.has_leakage is True
        assert res1.leakage_type in ("large_repair_code_block", "corrected_line_verbatim")

    def test_direct_replacement_pattern_blocked(self):
        patterns = [
            "Thay 'name = name;' bằng 'this.name = name;' trong constructor.",
            "Bạn chỉ cần sửa thành câu lệnh this.name = name; là được.",
            "Hãy đổi name = name thành this.name = name.",
            "Please replace name = name with this.name = name.",
        ]
        for text in patterns:
            res = SolutionLeakageGuard.check_leakage(
                tutor_response_text=text,
                hint_level=1,
            )
            assert res.has_leakage is True, f"Failed for text: {text}"
            assert res.leakage_type in ("direct_replacement_pattern", "corrected_line_verbatim")

    def test_false_unrevealed_metadata_detected(self):
        res = SolutionLeakageGuard.check_leakage(
            tutor_response_text="Hãy suy nghĩ về phạm vi của biến.",
            hint_level=2,
            solution_revealed=True,  # Inconsistent: Level 2 cannot reveal solution
        )
        assert res.has_leakage is True
        assert res.leakage_type == "false_unrevealed_metadata"

    def test_task_specific_keyword_exceptions_not_blocked(self, sample_student_code):
        """
        Cho phép ngoại lệ: giải thích khái niệm có chứa từ khóa độc lập như 'this', 'base', 'get'
        mà không đưa ra đoạn mã sửa hoàn chỉnh.
        """
        pedagogical_responses = [
            "Bạn đã từng nghe về từ khóa 'this' trong C# chưa? Từ khóa này có vai trò gì trong việc trỏ đến đối tượng?",
            "Hãy suy nghĩ về sự khác biệt giữa tham số hàm và trường (field) khi có cùng tên. Bạn có nhớ từ khóa 'this' không?",
            "Trong lập trình hướng đối tượng C#, từ khóa 'base' được dùng để gọi thành viên của lớp cơ sở.",
        ]
        for text in pedagogical_responses:
            res = SolutionLeakageGuard.check_leakage(
                tutor_response_text=text,
                hint_level=1,
                student_code=sample_student_code,
            )
            assert res.has_leakage is False, f"False positive on safe text: {text}"

    def test_level_4_remains_capable_of_showing_solution(
        self, sample_student_code, sample_reference_solution
    ):
        """Level 4 cho phép hiển thị giải pháp tường minh (solution_revealed = True)."""
        explicit_response = (
            "Dưới đây là giải pháp hoàn chỉnh:\n"
            "```csharp\n"
            "this.name = name;\n"
            "```\n"
            "Giải thích: Sử dụng this.name để gán vào trường của đối tượng."
        )
        res = SolutionLeakageGuard.check_leakage(
            tutor_response_text=explicit_response,
            hint_level=4,
            student_code=sample_student_code,
            reference_solution=sample_reference_solution,
            solution_revealed=True,
        )
        assert res.has_leakage is False
        assert "Level 4 cho phép" in res.details


class TestSolutionLeakageSanitization:
    """Kiểm tra việc hạ cấp về safe hint và ghi nhận validator_actions."""

    def test_sanitize_if_leaked_downgrades_to_deterministic_safe_hint(
        self, base_diagnosis, sample_student_code, sample_reference_solution
    ):
        leaked_response_model = TutorResponse(
            diagnosis=base_diagnosis,
            knowledge_components=["csharp.oop.constructor_assignment"],
            teaching_strategy="leaked_repair",
            tutor_response="Thay 'name = name;' bằng 'this.name = name;' ngay lập tức.",
            hint_level=1,
            solution_revealed=False,
            next_action="Chạy lại code",
        )

        sanitized = SolutionLeakageGuard.sanitize_if_leaked(
            response=leaked_response_model,
            student_code=sample_student_code,
            reference_solution=sample_reference_solution,
        )

        # 1. Obvious early-answer leakage is blocked
        assert "this.name = name;" not in sanitized.tutor_response
        assert sanitized.solution_revealed is False
        # 2. Teaching strategy and response downgraded to pedagogical safe hint
        assert sanitized.teaching_strategy == "socratic_questioning"
        assert "?" in sanitized.tutor_response
        # 3. Validator action recorded
        assert len(sanitized.validator_actions) > 0
        assert any("downgraded_to_safe_hint" in act for act in sanitized.validator_actions)


class TestTutorServiceLeakageIntegration:
    """Kiểm tra tích hợp toàn trình trong TutorService."""

    @pytest.mark.anyio
    async def test_tutor_service_blocks_premature_leakage_from_llm(
        self, sample_student_code, sample_reference_solution
    ):
        # Tạo mock provider trả về JSON mớm giải pháp trực tiếp ở hint_level 1
        class LeakingMockProvider:
            async def generate_response(self, messages, temperature=0.2):
                return '''{
                    "diagnosis": {
                        "issue_type": "parameter_field_shadowing",
                        "severity": "error",
                        "location": "Dog constructor",
                        "confidence": 0.95
                    },
                    "knowledge_components": ["csharp.oop.constructor_assignment"],
                    "possible_misconception": {
                        "type": "scope_confusion",
                        "description": "Nhầm lẫn scope",
                        "confidence": 0.8
                    },
                    "evidence": {
                        "code": "name = name;",
                        "reason": "Phép gán tham số cục bộ"
                    },
                    "teaching_strategy": "direct_answer",
                    "tutor_response": "Bạn chỉ cần sửa thành câu lệnh this.name = name; là xong nhé.",
                    "hint_level": 1,
                    "solution_revealed": false,
                    "next_action": "Sửa lại code"
                }'''

        service = TutorService(llm_provider=LeakingMockProvider())
        req = TutorRequest(
            problem_statement="Tạo lớp Dog với constructor gán tên.",
            student_code=sample_student_code,
            hint_level=1,
        )

        response = await service.generate_feedback(
            request=req,
            reference_solution=sample_reference_solution,
        )

        # Đảm bảo câu mớm đã bị chặn và hạ cấp về Socratic hint
        assert "this.name = name;" not in response.tutor_response
        assert response.solution_revealed is False
        assert response.hint_level == 1
        assert any("downgraded_to_safe_hint" in act for act in response.validator_actions)
