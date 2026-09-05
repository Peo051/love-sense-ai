import json
import pytest

from app.schemas.tutor_schema import (
    DiagnosisCategory,
    IssueSeverity,
    PossibleMisconception,
    TutorDiagnosis,
    TutorEvidence,
    TutorResponse,
)
from app.tutor.diagnosis import DiagnosisSubsystem
from app.tutor.taxonomy import (
    TAXONOMY_ISSUE_TYPES,
    is_valid_taxonomy_label,
    normalize_category,
    normalize_diagnosis_labels,
    normalize_issue_type,
)
from app.tutor.validator import TutorOutputValidator


# ==================== TEST FIXTURES ====================

@pytest.fixture
def recursive_getter_fixture() -> dict[str, str]:
    return {
        "problem": "Tạo lớp BankAccount có thuộc tính Balance kiểu decimal.",
        "code": """public class BankAccount
{
    private decimal _balance;

    public decimal Balance
    {
        get { return Balance; }
        set { _balance = value; }
    }
}""",
        "compiler_error": None,
    }


@pytest.fixture
def parameter_field_shadowing_fixture() -> dict[str, str]:
    return {
        "problem": "Tạo lớp Student có trường name và constructor nhận tham số name.",
        "code": """public class Student
{
    private string name;

    public Student(string name)
    {
        name = name;
    }
}""",
        "compiler_error": None,
    }


@pytest.fixture
def invalid_setter_validation_fixture() -> dict[str, str]:
    return {
        "problem": "Tạo lớp Person có thuộc tính Age, kiểm tra nếu age < 0 thì gán về 0.",
        "code": """public class Person
{
    private int _age;

    public int Age
    {
        get { return _age; }
        set
        {
            if (_age < 0)
            {
                _age = 0;
            }
        }
    }
}""",
        "compiler_error": None,
    }


@pytest.fixture
def static_instance_confusion_cs0120_fixture() -> dict[str, str]:
    return {
        "problem": "Gọi phương thức Greet từ hàm Main.",
        "code": """public class Program
{
    public void Greet()
    {
        Console.WriteLine("Hello!");
    }

    public static void Main()
    {
        Greet();
    }
}""",
        "compiler_error": "CS0120: An object reference is required for the non-static field, method, or property 'Program.Greet()'",
    }


@pytest.fixture
def static_instance_confusion_field_fixture() -> dict[str, str]:
    return {
        "problem": "Xây dựng lớp Car có tốc độ xe speed.",
        "code": """public class Car
{
    public static int speed;

    public void Accelerate()
    {
        speed += 10;
    }
}""",
        "compiler_error": None,
    }


@pytest.fixture
def valid_code_fixture() -> dict[str, str]:
    return {
        "problem": "Xây dựng lớp Circle có thuộc tính bán kính Radius và phương thức tính diện tích CalculateArea.",
        "code": """public class Circle
{
    private double _radius;

    public Circle(double radius)
    {
        _radius = radius > 0 ? radius : 0;
    }

    public double Radius
    {
        get { return _radius; }
        set { _radius = value > 0 ? value : 0; }
    }

    public double CalculateArea()
    {
        return 3.14159 * _radius * _radius;
    }
}""",
        "compiler_error": None,
    }


@pytest.fixture
def insufficient_code_fixture() -> dict[str, str]:
    return {
        "problem": "Xây dựng lớp Dog có thuộc tính Breed.",
        "code": "class Dog {",
        "compiler_error": None,
    }


# ==================== UNIT TESTS ====================

class TestTaxonomyAndNormalization:
    """Kiểm tra các quy tắc phân loại 8 categories và chuẩn hóa nhãn theo taxonomy C# OOP."""

    def test_eight_diagnosis_categories_defined(self):
        """Xác nhận đủ 8 nhóm chẩn đoán cốt lõi."""
        expected_categories = {
            "compile_error",
            "runtime_error",
            "logic_error",
            "conceptual_misuse",
            "requirement_violation",
            "no_bug",
            "insufficient_context",
            "unknown",
        }
        actual_categories = {c.value for c in DiagnosisCategory}
        assert actual_categories == expected_categories

    def test_normalize_category_variants(self):
        """Kiểm tra việc chuẩn hóa chuỗi tự do về DiagnosisCategory chuẩn."""
        assert normalize_category("syntax_error") == DiagnosisCategory.COMPILE_ERROR
        assert normalize_category("compile_error") == DiagnosisCategory.COMPILE_ERROR
        assert normalize_category("runtime") == DiagnosisCategory.RUNTIME_ERROR
        assert normalize_category("stackoverflow") == DiagnosisCategory.RUNTIME_ERROR
        assert normalize_category("logical_error") == DiagnosisCategory.LOGIC_ERROR
        assert normalize_category("semantic_error") == DiagnosisCategory.LOGIC_ERROR
        assert normalize_category("conceptual_misconception") == DiagnosisCategory.CONCEPTUAL_MISUSE
        assert normalize_category("requirement_violation") == DiagnosisCategory.REQUIREMENT_VIOLATION
        assert normalize_category("none") == DiagnosisCategory.NO_BUG
        assert normalize_category("correct") == DiagnosisCategory.NO_BUG
        assert normalize_category("valid") == DiagnosisCategory.NO_BUG
        assert normalize_category("incomplete") == DiagnosisCategory.INSUFFICIENT_CONTEXT
        assert normalize_category("too_short") == DiagnosisCategory.INSUFFICIENT_CONTEXT
        assert normalize_category("something_random_xyz") == DiagnosisCategory.UNKNOWN

    def test_normalize_diagnosis_labels(self):
        """Acceptance: Output labels are normalized."""
        cat, issue = normalize_diagnosis_labels("runtime", "recursive getter")
        assert cat == DiagnosisCategory.RUNTIME_ERROR
        assert issue == "recursive_property_accessor"

        cat, issue = normalize_diagnosis_labels("logic", "shadowing")
        assert cat == DiagnosisCategory.LOGIC_ERROR
        assert issue == "parameter_field_shadowing"

        cat, issue = normalize_diagnosis_labels("conceptual", "static_confusion")
        assert cat == DiagnosisCategory.CONCEPTUAL_MISUSE
        assert issue == "static_instance_confusion"

        cat, issue = normalize_diagnosis_labels("none", "none")
        assert cat == DiagnosisCategory.NO_BUG
        assert issue == "no_issue_detected"

        cat, issue = normalize_diagnosis_labels("incomplete", "too_short")
        assert cat == DiagnosisCategory.INSUFFICIENT_CONTEXT
        assert issue == "incomplete_code"

    def test_is_valid_taxonomy_label(self):
        """Kiểm tra tính hợp lệ của taxonomy nhãn."""
        assert is_valid_taxonomy_label(DiagnosisCategory.RUNTIME_ERROR, "recursive_property_accessor")
        assert is_valid_taxonomy_label(DiagnosisCategory.LOGIC_ERROR, "parameter_field_shadowing")
        assert is_valid_taxonomy_label(DiagnosisCategory.NO_BUG, "no_issue_detected")
        assert not is_valid_taxonomy_label(DiagnosisCategory.LOGIC_ERROR, "invented_random_error_123")


class TestStructuredDiagnosisFixtures:
    """Kiểm thử 6 kịch bản chẩn đoán bắt buộc theo test fixtures."""

    def test_recursive_getter_diagnosis(self, recursive_getter_fixture):
        """Kịch bản 1: Recursive getter dẫn đến StackOverflowException."""
        diagnosis = DiagnosisSubsystem.diagnose(
            student_code=recursive_getter_fixture["code"],
            compiler_error=recursive_getter_fixture["compiler_error"],
            problem_statement=recursive_getter_fixture["problem"],
        )

        assert diagnosis.category == DiagnosisCategory.RUNTIME_ERROR
        assert diagnosis.issue_type == "recursive_property_accessor"
        assert diagnosis.severity == IssueSeverity.ERROR.value
        assert diagnosis.confidence >= 0.9
        assert diagnosis.location is not None and "Balance" in diagnosis.location
        assert diagnosis.evidence is not None
        assert "return Balance;" in diagnosis.evidence.code
        assert diagnosis.possible_misconception is not None
        assert "property_vs_backing_field_confusion" in diagnosis.possible_misconception.type

    def test_parameter_field_shadowing_diagnosis(self, parameter_field_shadowing_fixture):
        """Kịch bản 2: Parameter / field shadowing trong constructor."""
        diagnosis = DiagnosisSubsystem.diagnose(
            student_code=parameter_field_shadowing_fixture["code"],
            compiler_error=parameter_field_shadowing_fixture["compiler_error"],
            problem_statement=parameter_field_shadowing_fixture["problem"],
        )

        assert diagnosis.category == DiagnosisCategory.LOGIC_ERROR
        assert diagnosis.issue_type == "parameter_field_shadowing"
        assert diagnosis.severity == IssueSeverity.WARNING.value
        assert diagnosis.confidence >= 0.9
        assert diagnosis.location == "constructor"
        assert diagnosis.evidence is not None
        assert "name = name;" in diagnosis.evidence.code
        assert diagnosis.possible_misconception is not None
        assert "parameter_shadowing_confusion" in diagnosis.possible_misconception.type

    def test_invalid_setter_validation_diagnosis(self, invalid_setter_validation_fixture):
        """Kịch bản 3: Invalid setter validation (kiểm tra nhầm backing field)."""
        diagnosis = DiagnosisSubsystem.diagnose(
            student_code=invalid_setter_validation_fixture["code"],
            compiler_error=invalid_setter_validation_fixture["compiler_error"],
            problem_statement=invalid_setter_validation_fixture["problem"],
        )

        assert diagnosis.category == DiagnosisCategory.LOGIC_ERROR
        assert diagnosis.issue_type == "invalid_setter_validation"
        assert diagnosis.severity == IssueSeverity.WARNING.value
        assert diagnosis.confidence >= 0.85
        assert diagnosis.evidence is not None
        assert "_age < 0" in diagnosis.evidence.code
        assert diagnosis.possible_misconception is not None

    def test_static_instance_confusion_cs0120_diagnosis(self, static_instance_confusion_cs0120_fixture):
        """Kịch bản 4a: Static / instance confusion từ lỗi trình biên dịch CS0120."""
        diagnosis = DiagnosisSubsystem.diagnose(
            student_code=static_instance_confusion_cs0120_fixture["code"],
            compiler_error=static_instance_confusion_cs0120_fixture["compiler_error"],
            problem_statement=static_instance_confusion_cs0120_fixture["problem"],
        )

        assert diagnosis.category == DiagnosisCategory.CONCEPTUAL_MISUSE
        assert diagnosis.issue_type == "static_instance_confusion"
        assert diagnosis.severity == IssueSeverity.ERROR.value
        assert diagnosis.confidence >= 0.9
        assert diagnosis.evidence is not None
        assert "CS0120" in diagnosis.evidence.code
        assert diagnosis.possible_misconception is not None

    def test_static_instance_confusion_field_diagnosis(self, static_instance_confusion_field_fixture):
        """Kịch bản 4b: Static / instance confusion do khai báo biến thành viên thành static."""
        diagnosis = DiagnosisSubsystem.diagnose(
            student_code=static_instance_confusion_field_fixture["code"],
            compiler_error=static_instance_confusion_field_fixture["compiler_error"],
            problem_statement=static_instance_confusion_field_fixture["problem"],
        )

        assert diagnosis.category == DiagnosisCategory.CONCEPTUAL_MISUSE
        assert diagnosis.issue_type == "static_instance_confusion"
        assert diagnosis.severity == IssueSeverity.ERROR.value
        assert diagnosis.confidence >= 0.9
        assert diagnosis.evidence is not None
        assert "public static int speed" in diagnosis.evidence.code
        assert diagnosis.possible_misconception is not None

    def test_valid_code_diagnosis_no_bug_no_invented_error(self, valid_code_fixture):
        """
        Kịch bản 5: Mã nguồn hợp lệ đạt chuẩn OOP.
        Acceptance: No-bug cases do not receive invented errors.
        """
        diagnosis = DiagnosisSubsystem.diagnose(
            student_code=valid_code_fixture["code"],
            compiler_error=valid_code_fixture["compiler_error"],
            problem_statement=valid_code_fixture["problem"],
        )

        assert diagnosis.category == DiagnosisCategory.NO_BUG
        assert diagnosis.issue_type == "no_issue_detected"
        assert diagnosis.severity == IssueSeverity.INFO.value
        assert diagnosis.confidence == 1.0
        # Tuyệt đối không được có ngộ nhận bịa đặt
        assert diagnosis.possible_misconception is None

    def test_insufficient_code_diagnosis(self, insufficient_code_fixture):
        """Kịch bản 6: Mã nguồn chưa hoàn chỉnh hoặc thiếu ngữ cảnh."""
        diagnosis = DiagnosisSubsystem.diagnose(
            student_code=insufficient_code_fixture["code"],
            compiler_error=insufficient_code_fixture["compiler_error"],
            problem_statement=insufficient_code_fixture["problem"],
        )

        assert diagnosis.category == DiagnosisCategory.INSUFFICIENT_CONTEXT
        assert diagnosis.issue_type == "incomplete_code"
        assert diagnosis.possible_misconception is None
        assert diagnosis.confidence <= 0.9


class TestPedagogicalSafetyAndNormalizationEnforcement:
    """Kiểm tra các quy tắc đảm bảo LLM không bịa đặt lỗi và chuẩn hóa dữ liệu."""

    def test_normalizer_strips_misconception_on_no_bug(self):
        """Nếu LLM trả về no_bug nhưng cố tình bịa misconception, normalizer phải xóa bỏ."""
        hallucinated_input = {
            "category": "no_bug",
            "issue_type": "no_issue_detected",
            "severity": "error",
            "confidence": 0.5,
            "possible_misconception": {
                "type": "invented_student_flaw",
                "description": "Mô hình tự bịa rằng sinh viên không hiểu lập trình.",
                "confidence": 0.9,
            },
        }

        normalized = DiagnosisSubsystem.normalize_diagnosis(hallucinated_input)
        assert normalized.category == DiagnosisCategory.NO_BUG
        assert normalized.issue_type == "no_issue_detected"
        assert normalized.severity == IssueSeverity.INFO.value
        assert normalized.confidence == 1.0
        assert normalized.possible_misconception is None

    def test_validator_integration_with_no_bug_response(self):
        """TutorOutputValidator đảm bảo phản hồi no_bug sạch sẽ 100%."""
        mock_raw_llm_json = json.dumps({
            "diagnosis": {
                "category": "none",
                "issue_type": "correct",
                "severity": "warning",
                "confidence": 0.7,
                "possible_misconception": {
                    "type": "fake_misconception",
                    "description": "Lỗi giả tưởng",
                    "confidence": 0.8,
                },
            },
            "knowledge_components": ["encapsulation"],
            "possible_misconception": {
                "type": "fake_misconception",
                "description": "Lỗi giả tưởng ngoài top level",
                "confidence": 0.8,
            },
            "teaching_strategy": "positive_reinforcement",
            "tutor_response": "Mã nguồn của bạn viết rất tốt và chuẩn OOP!",
            "hint_level": 1,
            "solution_revealed": False,
            "next_action": "Thử thêm phương thức tính chu vi.",
            "prompt_version": "v1",
        })

        response = TutorOutputValidator.parse_and_validate(mock_raw_llm_json)
        assert response.diagnosis.category == DiagnosisCategory.NO_BUG
        assert response.diagnosis.issue_type == "no_issue_detected"
        assert response.diagnosis.severity == IssueSeverity.INFO.value
        assert response.diagnosis.possible_misconception is None
        assert response.possible_misconception is None

    def test_schema_level_enforcement_for_no_bug(self):
        """Schema TutorDiagnosis tự động xóa possible_misconception khi category là NO_BUG."""
        diagnosis = TutorDiagnosis(
            category=DiagnosisCategory.NO_BUG,
            issue_type="no_issue_detected",
            confidence=0.9,
            possible_misconception=PossibleMisconception(
                type="some_misconception",
                description="Mô tả",
                confidence=0.5,
            ),
        )
        assert diagnosis.possible_misconception is None
        assert diagnosis.severity == "info"
