"""
Bộ kiểm thử tính xác thực của bằng chứng mã nguồn (Evidence Grounding Tests)
và các bài kiểm thử đối kháng (Adversarial Tests).
"""

import json
import pytest

from app.schemas.tutor_schema import (
    DiagnosisCategory,
    IssueSeverity,
    TutorDiagnosis,
    TutorEvidence,
    TutorRequest,
    TutorResponse,
)
from app.tutor.evidence_grounding import EvidenceGroundingValidator, GroundingResult
from app.tutor.provider import DeterministicMockTutorProvider
from app.tutor.service import TutorService
from app.tutor.validator import TutorOutputValidator


class TestEvidenceGroundingBasics:
    """Kiểm tra các hàm chuẩn hóa và đối sánh cơ bản."""

    def test_whitespace_normalization(self):
        raw = "  public   int   Age   { \n\t get; \n set;  } "
        normalized = EvidenceGroundingValidator.normalize_whitespace(raw)
        assert normalized == "public int Age { get; set; }"

    def test_compact_tokens(self):
        spaced = "w = w ;"
        compact = EvidenceGroundingValidator.compact_tokens(spaced)
        assert compact == "w=w;"

        multiline = "get {\n    return Balance;\n}"
        compact_ml = EvidenceGroundingValidator.compact_tokens(multiline)
        assert compact_ml == "get{return Balance;}"

    def test_extract_identifiers(self):
        code = "public class Student { private string studentName; public void SetName(string n) { studentName = n; } }"
        ids = EvidenceGroundingValidator.extract_identifiers(code)
        assert "Student" in ids
        assert "studentName" in ids
        assert "SetName" in ids
        assert "n" in ids
        # Keywords should be excluded
        assert "public" not in ids
        assert "class" not in ids
        assert "void" not in ids


class TestEvidenceValidationAndFuzzyMatching:
    """Kiểm tra đối sánh mờ có kiểm soát và chuẩn hóa bằng chứng."""

    def test_exact_grounding(self):
        student_code = "public class Student { public Student(string name) { name = name; } }"
        evidence = TutorEvidence(code="name = name;", reason="Parameter shadows field")

        result = EvidenceGroundingValidator.validate_evidence_snippet(
            evidence,
            student_code=student_code,
        )
        assert result.is_grounded is True
        assert result.evidence is not None
        assert result.evidence.code == "name = name;"

    def test_whitespace_and_indentation_normalized_grounding(self):
        student_code = """public class BankAccount
{
    public decimal Balance
    {
        get
        {
            return Balance;
        }
    }
}"""
        # Trích dẫn trên 1 dòng với khoảng trắng khác
        evidence = TutorEvidence(
            code="get { return Balance; }",
            reason="Recursive getter invocation",
        )

        result = EvidenceGroundingValidator.validate_evidence_snippet(
            evidence,
            student_code=student_code,
        )
        assert result.is_grounded is True
        assert result.evidence is not None

    def test_bounded_fuzzy_matching_formatting_differences(self):
        student_code = "public int Age { set { if ( value < 0 ) _age = 0 ; } }"
        # Khác biệt về khoảng trắng quanh dấu ngoặc và toán tử
        evidence = TutorEvidence(
            code="if (value < 0) _age = 0;",
            reason="Invalid setter validation",
        )

        result = EvidenceGroundingValidator.validate_evidence_snippet(
            evidence,
            student_code=student_code,
        )
        assert result.is_grounded is True

    def test_compiler_error_grounding(self):
        student_code = "public class Program { public static void Main() { Greet(); } }"
        compiler_err = "CS0120: An object reference is required for the non-static field, method, or property 'Program.Greet()'"
        evidence = TutorEvidence(
            code="CS0120: An object reference is required",
            reason="Compiler error shows non-static method call from static Main",
        )

        result = EvidenceGroundingValidator.validate_evidence_snippet(
            evidence,
            student_code=student_code,
            compiler_error=compiler_err,
        )
        assert result.is_grounded is True

    def test_evidence_item_length_limit(self):
        student_code = "public class BigClass { " + ("int x = 1; " * 100) + "}"
        huge_evidence_code = "int x = 1; " * 80  # Rất dài > 600 chars
        evidence = TutorEvidence(code=huge_evidence_code, reason="Too long evidence")

        result = EvidenceGroundingValidator.validate_evidence_snippet(
            evidence,
            student_code=student_code,
        )
        assert result.is_grounded is True
        assert len(result.evidence.code) <= EvidenceGroundingValidator.MAX_EVIDENCE_LENGTH + 10
        assert result.evidence.code.endswith("...")


class TestAdversarialEvidenceScenarios:
    """Các bài kiểm thử đối kháng (Adversarial Tests) khi LLM bịa đặt mã nguồn."""

    def test_adversarial_fabricated_line_rejection(self):
        """
        Adversarial: Sinh viên không hề viết dòng code này, nhưng LLM tự bịa ra.
        Acceptance: Unsupported evidence is removed or rejected.
        """
        student_code = """public class Rectangle
{
    private int width;
    private int height;

    public Rectangle(int w, int h)
    {
        width = w;
        height = h;
    }
}"""
        # LLM tự bịa ra dòng gán chia cho 0 hoàn toàn không có trong bài nộp
        fabricated_evidence = TutorEvidence(
            code="int area = width / 0;",
            reason="Mô hình tự bịa rằng sinh viên chia cho 0",
        )

        result = EvidenceGroundingValidator.validate_evidence_snippet(
            fabricated_evidence,
            student_code=student_code,
        )
        assert result.is_grounded is False
        assert result.is_fabricated is True
        assert result.evidence is None
        assert "bịa đặt" in result.rejection_reason or "không thể tìm thấy" in result.rejection_reason

    def test_adversarial_partial_multi_line_fabrication(self):
        """
        Adversarial: Bằng chứng gồm 2 dòng, dòng 1 có thật, dòng 2 do LLM tự bịa đặt biến mới.
        """
        student_code = """public class Student
{
    private string name;
    public Student(string name)
    {
        name = name;
    }
}"""
        # Dòng 1 có thật ('name = name;'), dòng 2 bịa đặt ('this.fabricatedId = 999;')
        mixed_evidence = TutorEvidence(
            code="name = name;\nthis.fabricatedId = 999;",
            reason="Phần sau là mã giả tưởng",
        )

        result = EvidenceGroundingValidator.validate_evidence_snippet(
            mixed_evidence,
            student_code=student_code,
        )
        assert result.is_grounded is False
        assert result.is_fabricated is True

    def test_adversarial_reference_solution_leakage_rejection(self):
        """
        Adversarial: LLM trích dẫn mã từ đề bài hoặc lời giải mẫu mà sinh viên chưa hề viết.
        Acceptance: Reject evidence from the reference solution as if it were student code.
        """
        problem_statement = "Yêu cầu: Xây dựng phương thức public double CalculatePerimeter() => 2 * (_width + _height);"
        reference_solution = "public double CalculatePerimeter() => 2 * (_width + _height);"
        student_code = """public class Rectangle
{
    private double _width;
    private double _height;
}"""
        # LLM trích dẫn hàm CalculatePerimeter từ reference_solution và gán là bằng chứng của sinh viên
        leaked_evidence = TutorEvidence(
            code="public double CalculatePerimeter() => 2 * (_width + _height);",
            reason="Trích dẫn nhầm từ lời giải mẫu",
        )

        result = EvidenceGroundingValidator.validate_evidence_snippet(
            leaked_evidence,
            student_code=student_code,
            reference_solution=reference_solution,
            problem_statement=problem_statement,
        )
        assert result.is_grounded is False
        assert result.is_reference_leakage is True
        assert result.evidence is None

    def test_high_confidence_cannot_survive_completely_unsupported_diagnosis(self):
        """
        Acceptance: High confidence cannot survive completely unsupported diagnosis.
        Khi chẩn đoán có độ tin cậy 0.95 nhưng bằng chứng bị từ chối,
        confidence phải bị hạ xuống <= 0.40 và chuyển sang UNKNOWN.
        """
        student_code = "public class Car { public int Speed; }"
        fabricated_evidence = TutorEvidence(
            code="public static int Speed = -1;",
            reason="Bịa đặt dòng khai báo static âm",
        )
        diagnosis = TutorDiagnosis(
            category=DiagnosisCategory.CONCEPTUAL_MISUSE,
            issue_type="static_instance_confusion",
            severity="error",
            location="Field Speed",
            confidence=0.98,
            evidence=fabricated_evidence,
        )

        grounded = EvidenceGroundingValidator.ground_diagnosis(
            diagnosis,
            student_code=student_code,
        )

        # 1. Bằng chứng bị gỡ bỏ
        assert grounded.evidence is None
        # 2. Độ tin cậy cao không thể tồn tại khi thiếu căn cứ
        assert grounded.confidence <= 0.40
        # 3. Đánh dấu bất định
        assert grounded.category == DiagnosisCategory.UNKNOWN
        assert grounded.issue_type == "unclassified_issue"
        assert "unverified" in grounded.location

    def test_valid_code_no_bug_unaffected_by_grounding(self):
        """Mã nguồn hoàn chỉnh (NO_BUG) không bị ảnh hưởng tiêu cực bởi grounded validator."""
        diagnosis = TutorDiagnosis(
            category=DiagnosisCategory.NO_BUG,
            issue_type="no_issue_detected",
            severity="info",
            confidence=1.0,
            evidence=None,
        )
        grounded = EvidenceGroundingValidator.ground_diagnosis(
            diagnosis,
            student_code="public class CleanCode {}",
        )
        assert grounded.category == DiagnosisCategory.NO_BUG
        assert grounded.confidence == 1.0


class TestTutorServiceEndToEndWithGrounding:
    """Kiểm thử tích hợp đầu-cuối với TutorService khi gặp đầu ra bịa đặt từ LLM."""

    @pytest.mark.anyio
    async def test_tutor_service_strips_fabricated_evidence_and_lowers_confidence(self):
        """
        Khi LLM trả về JSON với bằng chứng tự bịa, TutorService tự động:
        1. Gỡ bỏ evidence giả mạo.
        2. Hạ confidence xuống <= 0.40.
        3. Đổi teaching_strategy sang 'uncertainty_clarification'.
        """
        adversarial_canned = {
            "diagnosis": {
                "category": "logic_error",
                "issue_type": "parameter_field_shadowing",
                "severity": "error",
                "location": "Student.cs: constructor",
                "confidence": 0.95,
            },
            "knowledge_components": ["csharp_constructor"],
            "possible_misconception": {
                "type": "parameter_shadowing_confusion",
                "description": "Ngộ nhận",
                "confidence": 0.8,
            },
            "evidence": {
                "code": "this.fabricated_var = 12345;",  # Không hề có trong student_code
                "reason": "Bịa đặt",
            },
            "teaching_strategy": "socratic_questioning",
            "tutor_response": "Bạn có chắc đoạn mã này đúng không?",
            "hint_level": 1,
            "solution_revealed": False,
            "next_action": "Kiểm tra lại code",
            "prompt_version": "v1",
        }

        mock_provider = DeterministicMockTutorProvider(canned_response=adversarial_canned)
        service = TutorService(llm_provider=mock_provider)

        request = TutorRequest(
            problem_statement="Xây dựng lớp Student có constructor.",
            student_code="public class Student { public Student() {} }",
            hint_level=1,
        )

        response = await service.generate_feedback(request)

        # 1. Evidence bị gỡ bỏ
        assert response.evidence is None
        assert response.diagnosis.evidence is None
        # 2. Confidence bị hạ xuống <= 0.40
        assert response.diagnosis.confidence <= 0.40
        # 3. Phân loại chuyển thành UNKNOWN
        assert response.diagnosis.category == DiagnosisCategory.UNKNOWN
        # 4. Chiến lược chuyển thành uncertainty_clarification
        assert response.teaching_strategy == "uncertainty_clarification"
