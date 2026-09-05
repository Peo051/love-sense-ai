import pytest
from pydantic import ValidationError

from app.schemas.tutor_schema import (
    HintLevel,
    IssueSeverity,
    PossibleMisconception,
    TutorDiagnosis,
    TutorEvidence,
    TutorFeedbackRequest,
    TutorFeedbackResponse,
    TutorRequest,
    TutorResponse,
)


def sample_valid_request_payload():
    return {
        "problem_statement": "Xây dựng lớp Student có các thuộc tính Id, Name, và GPA kèm constructor.",
        "student_code": """public class Student {
    private string name;
    public Student(string name) {
        name = name;
    }
}""",
        "programming_language": "csharp",
        "compiler_error": "CS0171: Field 'Student.name' must be fully assigned before control is returned to the caller",
        "student_question": "Tại sao em gán name = name rồi mà compiler vẫn báo lỗi ạ?",
        "topic": "class_constructor",
        "hint_level": 1,
        "save_input": False,
        "save_result": True,
    }


def sample_valid_response_payload():
    return {
        "diagnosis": {
            "issue_type": "semantic_error",
            "severity": "warning",
            "location": "Student(string name) constructor",
            "confidence": 0.95,
        },
        "knowledge_components": [
            "csharp_constructor",
            "variable_shadowing",
            "this_keyword",
        ],
        "possible_misconception": {
            "type": "parameter_shadowing_confusion",
            "description": "Sinh viên có thể đang nghĩ rằng phép gán 'name = name' sẽ tự động cập nhật trường của đối tượng thay vì gán tham số vào chính nó.",
            "confidence": 0.88,
        },
        "evidence": {
            "code": "name = name;",
            "reason": "Tham số constructor trùng tên với trường private khiến trường này không được khởi tạo.",
        },
        "teaching_strategy": "socratic_questioning",
        "tutor_response": "Hãy quan sát tên tham số 'name' và trường 'private string name'. Khi viết 'name = name', theo bạn C# sẽ ưu tiên tham chiếu đến biến nào? Bạn đã từng nghe về từ khóa 'this' trong C# chưa?",
        "hint_level": 1,
        "solution_revealed": False,
        "next_action": "Xem lại cách phân biệt giữa biến trường (field) và tham số cục bộ khi chúng có cùng tên.",
    }


class TestTutorRequestSchema:
    def test_valid_request_serialization_deserialization(self):
        payload = sample_valid_request_payload()
        request = TutorRequest(**payload)

        assert request.problem_statement.startswith("Xây dựng lớp Student")
        assert request.programming_language == "csharp"
        assert request.hint_level == HintLevel.POINTING
        assert request.compiler_error is not None
        assert request.topic == "class_constructor"

        # Dump và validate lại
        dumped = request.model_dump()
        restored = TutorRequest.model_validate(dumped)
        assert restored.problem_statement == request.problem_statement
        assert restored.student_code == request.student_code

    def test_minimal_valid_request(self):
        request = TutorRequest(
            problem_statement="Tạo class Point với tọa độ X, Y.",
            student_code="public class Point { public int X; public int Y; }",
        )
        assert request.programming_language == "csharp"
        assert request.hint_level == 1
        assert request.compiler_error is None
        assert request.student_question is None
        assert request.topic is None
        assert request.save_input is False
        assert request.save_result is True

    @pytest.mark.parametrize("valid_lang", ["csharp", "c#", "cs", "CSHARP", "  c#  "])
    def test_language_normalization(self, valid_lang):
        request = TutorRequest(
            problem_statement="Đề bài C# cơ bản OOP.",
            student_code="class A {}",
            programming_language=valid_lang,
        )
        assert request.programming_language == "csharp"

    @pytest.mark.parametrize("invalid_lang", ["python", "java", "cpp", "javascript", "golang"])
    def test_unsupported_language_raises_error(self, invalid_lang):
        with pytest.raises(ValidationError) as exc_info:
            TutorRequest(
                problem_statement="Đề bài kiểm tra lập trình.",
                student_code="class A {}",
                programming_language=invalid_lang,
            )
        assert "Unsupported programming language" in str(exc_info.value)
        assert "csharp" in str(exc_info.value)

    def test_empty_or_whitespace_problem_statement_raises_error(self):
        with pytest.raises(ValidationError) as exc_info:
            TutorRequest(
                problem_statement="   \t   ",
                student_code="class A {}",
            )
        assert "Problem statement must not be empty" in str(exc_info.value)

    def test_too_short_problem_statement_raises_error(self):
        with pytest.raises(ValidationError) as exc_info:
            TutorRequest(
                problem_statement="abc",
                student_code="class A {}",
            )
        assert "Problem statement is too short" in str(exc_info.value)

    def test_empty_or_whitespace_student_code_raises_error(self):
        with pytest.raises(ValidationError) as exc_info:
            TutorRequest(
                problem_statement="Xây dựng class Animal hoàn chỉnh.",
                student_code="    \t   ",
            )
        assert "Student code must not be empty" in str(exc_info.value)

    def test_excessive_length_limits(self):
        # problem_statement > 10,000 ký tự
        with pytest.raises(ValidationError):
            TutorRequest(
                problem_statement="X" * 10001,
                student_code="class A {}",
            )

        # student_code > 20,000 ký tự
        with pytest.raises(ValidationError):
            TutorRequest(
                problem_statement="Đề bài kiểm tra kích thước code.",
                student_code="C" * 20001,
            )

        # student_question > 2,000 ký tự
        with pytest.raises(ValidationError):
            TutorRequest(
                problem_statement="Đề bài kiểm tra câu hỏi sinh viên.",
                student_code="class A {}",
                student_question="Q" * 2001,
            )

    @pytest.mark.parametrize("invalid_hint", [0, -1, 4, 10])
    def test_invalid_hint_level_raises_error(self, invalid_hint):
        with pytest.raises(ValidationError):
            TutorRequest(
                problem_statement="Đề bài hợp lệ với gợi ý.",
                student_code="class A {}",
                hint_level=invalid_hint,
            )

    def test_optional_fields_clean_whitespace(self):
        request = TutorRequest(
            problem_statement="Đề bài hợp lệ chuẩn hóa chuỗi rỗng.",
            student_code="class A {}",
            compiler_error="   ",
            student_question="   \t  ",
            topic="   ",
        )
        assert request.compiler_error is None
        assert request.student_question is None
        assert request.topic is None


class TestTutorResponseSchema:
    def test_valid_response_serialization_deserialization(self):
        payload = sample_valid_response_payload()
        response = TutorResponse(**payload)

        assert response.diagnosis.issue_type == "semantic_error"
        assert response.diagnosis.confidence == 0.95
        assert len(response.knowledge_components) == 3
        assert response.possible_misconception is not None
        assert response.possible_misconception.type == "parameter_shadowing_confusion"
        assert response.evidence is not None
        assert response.evidence.code == "name = name;"
        assert response.solution_revealed is False

        # Kiểm tra serialize JSON và parse lại
        json_data = response.model_dump_json()
        restored = TutorResponse.model_validate_json(json_data)
        assert restored.diagnosis.issue_type == "semantic_error"
        assert restored.tutor_response == response.tutor_response

    def test_diagnosis_confidence_bounds(self):
        with pytest.raises(ValidationError):
            TutorDiagnosis(
                issue_type="syntax_error",
                confidence=1.5,
            )

        with pytest.raises(ValidationError):
            TutorDiagnosis(
                issue_type="syntax_error",
                confidence=-0.1,
            )

    def test_possible_misconception_semantics(self):
        misconception = PossibleMisconception(
            type="reference_vs_value_confusion",
            description="Sinh viên có thể đang nghĩ rằng tham số kiểu tham chiếu được truyền dưới dạng bản sao độc lập.",
            confidence=0.75,
        )
        assert misconception.type == "reference_vs_value_confusion"
        assert misconception.confidence == 0.75

        # Type hoặc description rỗng
        with pytest.raises(ValidationError):
            PossibleMisconception(
                type="   ",
                description="Hợp lệ",
                confidence=0.5,
            )

        with pytest.raises(ValidationError):
            PossibleMisconception(
                type="valid_type",
                description="   ",
                confidence=0.5,
            )

    def test_alias_classes(self):
        assert TutorFeedbackRequest is TutorRequest
        assert TutorFeedbackResponse is TutorResponse


class TestNoEmotionDomainFields:
    """
    Xác nhận không còn bất kỳ trường nào liên quan đến cảm xúc/hẹn hò trong schemas mới.
    """
    forbidden_terms = ["emotion", "partner", "relationship", "romantic", "affectionate", "sulking"]

    def test_request_has_no_emotion_fields(self):
        field_names = list(TutorRequest.model_fields.keys())
        for field in field_names:
            for term in self.forbidden_terms:
                assert term not in field.lower(), f"Forbidden emotion term '{term}' found in request field '{field}'"

    def test_response_has_no_emotion_fields(self):
        field_names = list(TutorResponse.model_fields.keys())
        for field in field_names:
            for term in self.forbidden_terms:
                assert term not in field.lower(), f"Forbidden emotion term '{term}' found in response field '{field}'"
