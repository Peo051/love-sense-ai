"""
Unit Tests for EvaluationMetadata and EvaluationRecord Schema Boundaries (APT-051).

Verifies:
1. Non-gold experiment metadata (topic, difficulty, problem_family_id, split, source_type)
   is strictly separated into EvaluationMetadata.
2. EvaluationRecord cleanly isolates model_input, ground_truth, and metadata.
3. Prompt builders cannot consume EvaluationMetadata or EvaluationRecord directly.
4. Provider requests contain zero metadata fields (topic and difficulty hidden by default).
5. EvaluationMetadata enforces immutable frozen semantics and extra='forbid'.
"""

from typing import Any, Dict
import pytest
from pydantic import ValidationError

from app.evaluation.schemas import (
    EvaluationMetadata,
    EvaluationRecord,
    GroundTruth,
    ModelInput,
    assert_not_ground_truth,
)
from app.evaluation.prompts import (
    build_prompt_a,
    build_prompt_b,
    build_prompt_c,
    build_prompt_d,
)
from app.tutor.provider import DeterministicMockTutorProvider


@pytest.fixture
def comprehensive_raw_sample() -> Dict[str, Any]:
    """Sample record mimicking full VietCSharpTutor dataset entry."""
    return {
        "id": "vct-505",
        "language": "vi",
        "topic": "csharp.polymorphism_virtual_methods",
        "difficulty": "medium",
        "problem_family_id": "fam-vehicle-hierarchy-99",
        "problem_statement_vi": "Xây dựng lớp BaseVehicle và lớp DerivedCar ghi đè Drive().",
        "student_code": "public class BaseVehicle { public void Drive() {} }",
        "compiler_error": "CS0114: Member hides inherited member; missing override",
        "expected_behavior": "BaseVehicle.Drive() cần từ khóa virtual.",
        "bug_status": "has_bug",
        "error_category": "conceptual_misuse",
        "bug_type": "missing_virtual_override",
        "bug_location": "public void Drive()",
        "knowledge_components": ["csharp.polymorphism", "csharp.virtual_method"],
        "possible_misconception": "Nghĩ rằng phương thức mặc định luôn là virtual.",
        "reference_diagnosis": "Thiếu từ khóa virtual trong lớp cơ sở.",
        "evidence": "public void Drive()",
        "hint_1": "Xem lại phương thức Drive trong BaseVehicle.",
        "hint_2": "C# yêu cầu khai báo rõ ràng virtual để cho phép đa hình.",
        "hint_3": "Thêm từ khóa virtual vào trước void Drive().",
        "reference_solution": "public class BaseVehicle { public virtual void Drive() {} }",
        "explanation_vi": "Giải thích tính đa hình trong C#.",
        "source_type": "controlled_mutation",
        "split": "test",
        "review_status": "approved",
    }


def test_evaluation_metadata_creation(comprehensive_raw_sample: Dict[str, Any]):
    """
    Requirement: Extract metadata properly from a dataset record.
    """
    metadata = EvaluationMetadata.from_dataset_record(comprehensive_raw_sample, run_id="run-exp-01")

    assert metadata.sample_id == "vct-505"
    assert metadata.split == "test"
    assert metadata.dataset_version == "1.0.0"
    assert metadata.source_type == "controlled_mutation"
    assert metadata.problem_family_id == "fam-vehicle-hierarchy-99"
    assert metadata.topic == "csharp.polymorphism_virtual_methods"
    assert metadata.difficulty == "medium"
    assert metadata.review_status == "approved"
    assert metadata.run_id == "run-exp-01"


def test_evaluation_record_separation(comprehensive_raw_sample: Dict[str, Any]):
    """
    Requirement 1: Create EvaluationRecord cleanly separating model_input, ground_truth, and metadata.
    """
    record = EvaluationRecord.from_dataset_record(comprehensive_raw_sample, run_id="run-exp-02")

    # 1. model_input must be strictly ModelInput
    assert isinstance(record.model_input, ModelInput)
    assert record.model_input.sample_id == "vct-505"
    assert record.model_input.student_code == "public class BaseVehicle { public void Drive() {} }"
    assert not hasattr(record.model_input, "topic")
    assert not hasattr(record.model_input, "difficulty")
    assert not hasattr(record.model_input, "bug_status")

    # 2. ground_truth must be strictly GroundTruth
    assert isinstance(record.ground_truth, GroundTruth)
    assert record.ground_truth.bug_status == "has_bug"
    assert record.ground_truth.bug_type == "missing_virtual_override"
    assert record.ground_truth.reference_solution.startswith("public class BaseVehicle")

    # 3. metadata must be strictly EvaluationMetadata
    assert isinstance(record.metadata, EvaluationMetadata)
    assert record.metadata.problem_family_id == "fam-vehicle-hierarchy-99"
    assert record.metadata.topic == "csharp.polymorphism_virtual_methods"

    # 4. Explicit helper for inference
    inference_input = record.get_inference_input()
    assert inference_input is record.model_input
    assert isinstance(inference_input, ModelInput)


def test_prompt_builder_cannot_consume_evaluation_metadata(comprehensive_raw_sample: Dict[str, Any]):
    """
    Requirement: Prompt builders must reject EvaluationMetadata with TypeError.
    """
    metadata = EvaluationMetadata.from_dataset_record(comprehensive_raw_sample)

    with pytest.raises(TypeError, match="EvaluationMetadata object passed to inference component"):
        build_prompt_a(metadata)

    with pytest.raises(TypeError, match="EvaluationMetadata object passed to inference component"):
        build_prompt_b(metadata)

    with pytest.raises(TypeError, match="EvaluationMetadata object passed to inference component"):
        build_prompt_c(metadata)

    with pytest.raises(TypeError, match="EvaluationMetadata object passed to inference component"):
        build_prompt_d(metadata)


def test_prompt_builder_cannot_consume_evaluation_record(comprehensive_raw_sample: Dict[str, Any]):
    """
    Requirement: Prompt builders must reject combined EvaluationRecord with TypeError.
    Inference code must explicitly extract model_input.
    """
    record = EvaluationRecord.from_dataset_record(comprehensive_raw_sample)

    with pytest.raises(TypeError, match="Combined EvaluationRecord passed to inference component"):
        build_prompt_a(record)

    with pytest.raises(TypeError, match="Combined EvaluationRecord passed to inference component"):
        build_prompt_c(record)

    with pytest.raises(TypeError, match="Combined EvaluationRecord passed to inference component"):
        build_prompt_d(record)


def test_provider_request_contains_no_metadata_fields(comprehensive_raw_sample: Dict[str, Any]):
    """
    Requirement: Ensure metadata tags (topic, difficulty, problem_family_id, split)
    do NOT leak into prompts or model requests.
    """
    record = EvaluationRecord.from_dataset_record(comprehensive_raw_sample)
    model_input = record.get_inference_input()

    # Build prompts for System A, B, C, D
    prompt_a = build_prompt_a(model_input)
    prompt_b = build_prompt_b(model_input)
    prompt_c = build_prompt_c(model_input)
    prompt_d = build_prompt_d(model_input, student_context={"attempt_count": 1})

    for p_name, prompt in [("A", prompt_a), ("B", prompt_b), ("C", prompt_c), ("D", prompt_d)]:
        assert record.metadata.topic not in prompt, f"Topic leaked in prompt {p_name}!"
        assert record.metadata.difficulty not in prompt, f"Difficulty leaked in prompt {p_name}!"
        assert record.metadata.problem_family_id not in prompt, f"Family ID leaked in prompt {p_name}!"
        assert record.metadata.source_type not in prompt, f"Source type leaked in prompt {p_name}!"


@pytest.mark.anyio
async def test_provider_client_rejects_evaluation_metadata(comprehensive_raw_sample: Dict[str, Any]):
    """
    Requirement: Provider client must reject EvaluationMetadata payloads.
    """
    metadata = EvaluationMetadata.from_dataset_record(comprehensive_raw_sample)
    provider = DeterministicMockTutorProvider()

    with pytest.raises(TypeError, match="EvaluationMetadata object passed to inference component"):
        await provider.generate_response([metadata])  # type: ignore


def test_metadata_frozen_and_extra_forbid(comprehensive_raw_sample: Dict[str, Any]):
    """
    Requirement: EvaluationMetadata must be immutable and reject unknown extra fields.
    """
    metadata = EvaluationMetadata.from_dataset_record(comprehensive_raw_sample)

    # Immutability
    with pytest.raises(ValidationError) as exc_info:
        metadata.topic = "hacked.topic"
    assert "Instance is frozen" in str(exc_info.value)

    # Extra fields forbidden
    with pytest.raises(ValidationError):
        EvaluationMetadata(
            sample_id="vct-999",
            unknown_random_field="bad_payload",
        )


def test_topic_and_difficulty_hidden_from_model_input(comprehensive_raw_sample: Dict[str, Any]):
    """
    Acceptance Criteria: topic and difficulty are completely hidden from ModelInput.
    """
    record = EvaluationRecord.from_dataset_record(comprehensive_raw_sample)
    model_input = record.model_input

    assert not hasattr(model_input, "topic")
    assert not hasattr(model_input, "difficulty")
    assert not hasattr(model_input, "problem_family_id")

    input_dict = model_input.model_dump()
    assert "topic" not in input_dict
    assert "difficulty" not in input_dict
    assert "problem_family_id" not in input_dict
