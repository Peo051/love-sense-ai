"""
Unit Tests for Strict ModelInput Boundary (APT-049).

Verifies:
1. ModelInput rejects unknown and malicious extra fields.
2. ModelInput contains zero gold-standard annotation attributes.
3. DatasetRecord to ModelInput conversion strictly uses explicit whitelist construction.
4. Nested metadata and full dataset samples cannot accidentally be serialized into ModelInput.
5. ModelInput is strictly immutable (frozen=True).
"""

from typing import Any, Dict
import pytest
from pydantic import ValidationError

from app.evaluation.schemas import (
    ALLOWED_MODEL_INPUT_FIELDS,
    FORBIDDEN_GOLD_FIELDS,
    ModelInput,
)


@pytest.fixture
def full_gold_sample() -> Dict[str, Any]:
    """Sample mimicking a complete 26-field record from VietCSharpTutor-600."""
    return {
        "id": "vct-042",
        "language": "vi",
        "topic": "csharp.encapsulation",
        "difficulty": "beginner",
        "problem_family_id": "fam-bank-account",
        "problem_statement_vi": "Xây dựng lớp BankAccount với số dư private...",
        "student_code": "public class BankAccount { public int Balance; }",
        "compiler_error": "CS0101: Namespace already contains a definition",
        "expected_behavior": "Balance phải là private và có getter/setter hợp lệ.",
        "bug_status": "has_bug",
        "error_category": "conceptual_misuse",
        "bug_type": "encapsulation_break",
        "bug_location": "public int Balance;",
        "knowledge_components": ["csharp.encapsulation", "csharp.access_modifier"],
        "possible_misconception": "Nghĩ rằng mọi thuộc tính phải public để Main truy cập.",
        "reference_diagnosis": "Vi phạm tính bao đóng do public trực tiếp biến Balance.",
        "evidence": "public int Balance;",
        "hint_1": "Hãy kiểm tra mức độ truy cập của biến Balance.",
        "hint_2": "Nguyên lý đóng gói yêu cầu che giấu trạng thái nội bộ.",
        "hint_3": "Sử dụng private int _balance và property Balance tương ứng.",
        "reference_solution": "public class BankAccount { private int _balance; ... }",
        "explanation_vi": "Giải thích chi tiết về tính đóng gói trong C#.",
        "source_type": "expert_authored",
        "split": "test",
        "review_status": "approved",
    }


def test_model_input_rejects_unknown_fields():
    """
    Requirement 3 & 6: Extra/unknown fields MUST be rejected immediately.
    Attempting to pass any unwhitelisted field to ModelInput constructor must raise ValidationError.
    """
    # 1. Arbitrary malicious extra field
    with pytest.raises(ValidationError) as exc_info:
        ModelInput(
            sample_id="test-1",
            problem_statement="Problem description",
            student_code="int x = 1;",
            malicious_payload="DROP TABLE users;",
        )
    assert "Extra inputs are not permitted" in str(exc_info.value) or "malicious_payload" in str(exc_info.value)

    # 2. Direct injection of gold bug_status
    with pytest.raises(ValidationError) as exc_info:
        ModelInput(
            sample_id="test-2",
            problem_statement="Problem description",
            student_code="int x = 1;",
            bug_status="has_bug",
        )
    assert "bug_status" in str(exc_info.value)

    # 3. Direct injection of reference_solution
    with pytest.raises(ValidationError) as exc_info:
        ModelInput(
            sample_id="test-3",
            problem_statement="Problem description",
            student_code="int x = 1;",
            reference_solution="int x = 2;",
        )
    assert "reference_solution" in str(exc_info.value)

    # 4. Direct injection of knowledge_components
    with pytest.raises(ValidationError) as exc_info:
        ModelInput(
            sample_id="test-4",
            problem_statement="Problem description",
            student_code="int x = 1;",
            knowledge_components=["csharp.syntax"],
        )
    assert "knowledge_components" in str(exc_info.value)


def test_model_input_has_no_gold_annotations():
    """
    Requirement: ModelInput schema must have NO gold annotation fields in its schema definition.
    """
    model_field_names = set(ModelInput.model_fields.keys())

    # Ensure model field names exactly match allowed whitelist
    assert model_field_names == ALLOWED_MODEL_INPUT_FIELDS

    # Ensure none of the forbidden gold fields are present
    intersection = model_field_names & FORBIDDEN_GOLD_FIELDS
    assert len(intersection) == 0, f"Found forbidden gold fields in ModelInput: {intersection}"

    # Also verify on instantiated object
    instance = ModelInput(
        sample_id="vct-001",
        problem_statement="Test problem",
        student_code="class Test {}",
    )
    for forbidden in FORBIDDEN_GOLD_FIELDS:
        assert not hasattr(instance, forbidden), f"Instance unexpectedly has attribute: {forbidden}"


def test_dataset_to_model_input_is_whitelist_only(full_gold_sample: Dict[str, Any]):
    """
    Requirement 4 & 5: Conversion from dataset sample must use explicit whitelist extraction.
    Must successfully extract legitimate fields while strictly ignoring all 20+ gold fields.
    """
    model_input = ModelInput.from_dataset_record(full_gold_sample)

    # Legitimate fields correctly mapped
    assert model_input.sample_id == "vct-042"
    assert model_input.problem_statement == "Xây dựng lớp BankAccount với số dư private..."
    assert model_input.student_code == "public class BankAccount { public int Balance; }"
    assert model_input.compiler_error == "CS0101: Namespace already contains a definition"
    assert model_input.student_question is None

    # Verify attributes do not exist
    for forbidden in FORBIDDEN_GOLD_FIELDS:
        assert not hasattr(model_input, forbidden)

    # Verify dict dump has exactly the whitelisted keys
    data_dict = model_input.to_model_dict()
    assert set(data_dict.keys()) == ALLOWED_MODEL_INPUT_FIELDS
    for forbidden in FORBIDDEN_GOLD_FIELDS:
        assert forbidden not in data_dict


def test_nested_gold_metadata_not_serialized():
    """
    Requirement 6: Nested gold metadata or extra dictionaries in sample must NOT leak into serialization.
    """
    record_with_nested = {
        "id": "vct-999",
        "problem_statement_vi": "Nested test problem",
        "student_code": "Console.WriteLine();",
        "metadata": {
            "internal_tokens": 450,
            "hidden_gold": "logic_error",
            "reference_solution": "Console.WriteLine('Correct');",
        },
        "annotations": {
            "bug_location": "line 1",
            "kcs": ["csharp.io"],
        },
    }

    model_input = ModelInput.from_dataset_record(record_with_nested)

    # Check serialized dict
    dumped = model_input.model_dump()
    assert "metadata" not in dumped
    assert "annotations" not in dumped
    assert "internal_tokens" not in str(dumped)
    assert "hidden_gold" not in str(dumped)

    # Check serialized JSON string
    dumped_json = model_input.model_dump_json()
    assert "metadata" not in dumped_json
    assert "annotations" not in dumped_json
    assert "hidden_gold" not in dumped_json
    assert "logic_error" not in dumped_json


def test_model_input_immutability():
    """
    Requirement 2: ModelInput must be immutable (frozen=True).
    Attempting to mutate attributes after creation must raise an exception.
    """
    instance = ModelInput(
        sample_id="vct-001",
        problem_statement="Original statement",
        student_code="int a = 1;",
    )

    with pytest.raises(ValidationError) as exc_info:
        instance.student_code = "int a = 2;"
    assert "Instance is frozen" in str(exc_info.value)

    with pytest.raises(ValidationError) as exc_info:
        instance.sample_id = "vct-hacked"
    assert "Instance is frozen" in str(exc_info.value)


def test_from_dataset_record_rejects_missing_mandatory_fields():
    """
    Validation test: Dataset record must have id/sample_id and problem_statement.
    """
    # Missing sample_id
    with pytest.raises(ValueError, match="missing mandatory 'id' or 'sample_id'"):
        ModelInput.from_dataset_record({
            "problem_statement_vi": "Some task",
            "student_code": "code",
        })

    # Missing problem_statement
    with pytest.raises(ValueError, match="missing mandatory problem statement"):
        ModelInput.from_dataset_record({
            "id": "vct-001",
            "student_code": "code",
        })

    # Missing student_code
    with pytest.raises(ValueError, match="missing 'student_code' field"):
        ModelInput.from_dataset_record({
            "id": "vct-001",
            "problem_statement_vi": "Some task",
        })
