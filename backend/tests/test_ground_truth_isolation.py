"""
Unit Tests for Isolated GroundTruth Schema and Security Boundary (APT-050).

Verifies:
1. GroundTruth is strictly rejected by:
   - model runner
   - prompt builder (build_prompt_a, b, c, d)
   - student context builder (CodeSubmissionContext, LearnerPersonalizationContext)
   - provider client (DeterministicMockTutorProvider, OpenAITutorProvider)
2. Deliberate sentinel (GROUND_TRUTH_SENTINEL_71F2) cannot appear in serialized model requests.
3. ModelInput and GroundTruth are completely separate objects with disjoint schemas (except sample_id).
4. Evaluator can still compare predictions against GroundTruth via sample_id.
"""

from typing import Any, Dict
import pytest

from app.evaluation.schemas import (
    GROUND_TRUTH_SENTINEL_71F2,
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
from app.evaluation.runner import EvaluationRunner
from app.tutor.context_builder import CodeSubmissionContext, LearnerPersonalizationContext
from app.tutor.provider import DeterministicMockTutorProvider


@pytest.fixture
def full_gold_sample() -> Dict[str, Any]:
    """Sample mimicking a complete 26-field record from VietCSharpTutor-600."""
    return {
        "id": "vct-101",
        "language": "vi",
        "topic": "csharp.encapsulation",
        "difficulty": "beginner",
        "problem_family_id": "fam-bank",
        "problem_statement_vi": "Thiết kế lớp Account có số dư được bảo vệ.",
        "student_code": "public class Account { public int Balance; }",
        "compiler_error": "CS0101: Namespace conflict",
        "expected_behavior": "Balance phải có access modifier private.",
        "bug_status": "has_bug",
        "error_category": "conceptual_misuse",
        "bug_type": "encapsulation_break",
        "bug_location": "public int Balance;",
        "knowledge_components": ["csharp.encapsulation"],
        "possible_misconception": "Nghĩ rằng public thuận tiện hơn.",
        "reference_diagnosis": "Vi phạm tính đóng gói nghiêm trọng.",
        "evidence": "public int Balance;",
        "hint_1": "Gợi ý định hướng 1.",
        "hint_2": "Gợi ý khái niệm 2.",
        "hint_3": "Gợi ý hành động 3.",
        "reference_solution": "public class Account { private int _balance; }",
        "explanation_vi": "Giải thích chi tiết.",
        "source_type": "expert_authored",
        "split": "test",
        "review_status": "approved",
    }


@pytest.fixture
def ground_truth_instance(full_gold_sample: Dict[str, Any]) -> GroundTruth:
    return GroundTruth.from_dataset_record(full_gold_sample)


def test_ground_truth_not_accepted_by_runner(ground_truth_instance: GroundTruth, tmp_path):
    """
    Requirement 1: GroundTruth object must be rejected by EvaluationRunner.
    """
    runner = EvaluationRunner(system="C", split="validation", output_dir=tmp_path, mock=True)

    # Passing GroundTruth object directly to _predict_single must raise TypeError
    with pytest.raises(TypeError, match="EvaluationRunner cannot accept GroundTruth objects"):
        runner._predict_single(ground_truth_instance)

    # Passing dictionary containing the sentinel must raise TypeError
    with pytest.raises(TypeError, match="GroundTruth sentinel detected"):
        runner._predict_single({"sentinel": GROUND_TRUTH_SENTINEL_71F2, "id": "vct-101"})


def test_ground_truth_not_accepted_by_prompt_builder(ground_truth_instance: GroundTruth):
    """
    Requirement 1: GroundTruth object must be rejected by all prompt builders.
    """
    # 1. Baseline A prompt builder
    with pytest.raises(TypeError, match="GroundTruth object passed to inference component"):
        build_prompt_a(ground_truth_instance)

    # 2. Baseline B prompt builder
    with pytest.raises(TypeError, match="GroundTruth object passed to inference component"):
        build_prompt_b(ground_truth_instance)

    # 3. Proposed C prompt builder
    with pytest.raises(TypeError, match="GroundTruth object passed to inference component"):
        build_prompt_c(ground_truth_instance)

    # 4. Proposed D prompt builder
    with pytest.raises(TypeError, match="GroundTruth object passed to inference component"):
        build_prompt_d(ground_truth_instance)

    # 5. Proposed D prompt builder with GroundTruth in student_context
    with pytest.raises(TypeError, match="GroundTruth object passed to inference component"):
        build_prompt_d("Problem", "code", student_context=ground_truth_instance)

    # 6. Proposed D prompt builder with sentinel leaked in context dict
    with pytest.raises(TypeError, match="GroundTruth sentinel detected"):
        build_prompt_d("Problem", "code", student_context={"sentinel": GROUND_TRUTH_SENTINEL_71F2})


def test_ground_truth_not_accepted_by_student_context_builder(ground_truth_instance: GroundTruth):
    """
    Requirement 1: GroundTruth object must be rejected by student context builder.
    """
    # Attempting to pass GroundTruth into CodeSubmissionContext
    with pytest.raises(TypeError, match="GroundTruth object passed to inference component"):
        CodeSubmissionContext(
            problem_statement=ground_truth_instance,  # type: ignore
            student_code="class Foo {}",
        )

    # Attempting to pass GroundTruth sentinel into LearnerPersonalizationContext
    with pytest.raises(TypeError, match="GroundTruth sentinel detected"):
        LearnerPersonalizationContext(
            student_profile={"sentinel": GROUND_TRUTH_SENTINEL_71F2}
        )


@pytest.mark.anyio
async def test_ground_truth_not_accepted_by_provider_client(ground_truth_instance: GroundTruth):
    """
    Requirement 1: Provider client must reject GroundTruth payloads.
    """
    provider = DeterministicMockTutorProvider()

    # Passing GroundTruth object in messages list
    with pytest.raises(TypeError, match="GroundTruth object passed to inference component"):
        await provider.generate_response([ground_truth_instance])  # type: ignore

    # Passing message with GroundTruth sentinel in content
    with pytest.raises(TypeError, match="GroundTruth sentinel detected"):
        await provider.generate_response([
            {"role": "user", "content": f"Secret leakage: {GROUND_TRUTH_SENTINEL_71F2}"}
        ])


def test_ground_truth_not_model_serializable(full_gold_sample: Dict[str, Any]):
    """
    Requirement 5: Ensure deliberate sentinel cannot appear in serialized model requests.
    """
    model_input = ModelInput.from_dataset_record(full_gold_sample)

    serialized_dict = model_input.model_dump()
    serialized_json = model_input.model_dump_json()

    assert GROUND_TRUTH_SENTINEL_71F2 not in serialized_dict
    assert GROUND_TRUTH_SENTINEL_71F2 not in serialized_json
    assert GROUND_TRUTH_SENTINEL_71F2 not in str(serialized_dict)

    # Build valid prompt from ModelInput and verify sentinel absence
    prompt = build_prompt_c(model_input)
    assert GROUND_TRUTH_SENTINEL_71F2 not in prompt


def test_model_input_and_ground_truth_are_separate_objects(full_gold_sample: Dict[str, Any]):
    """
    Requirement 2 & 3: ModelInput and GroundTruth are completely separate objects.
    No combined object is returned to inference code.
    """
    model_input = ModelInput.from_dataset_record(full_gold_sample)
    ground_truth = GroundTruth.from_dataset_record(full_gold_sample)

    # Type verification
    assert isinstance(model_input, ModelInput)
    assert isinstance(ground_truth, GroundTruth)
    assert type(model_input) is not type(ground_truth)
    assert not issubclass(ModelInput, GroundTruth)
    assert not issubclass(GroundTruth, ModelInput)

    # Disjoint attribute sets (except linking key: sample_id)
    input_fields = set(ModelInput.model_fields.keys())
    gt_fields = set(GroundTruth.model_fields.keys())
    common_fields = input_fields & gt_fields

    assert common_fields == {"sample_id"}, f"Unexpected common fields: {common_fields}"

    # Sentinel verification
    assert ground_truth.sentinel == GROUND_TRUTH_SENTINEL_71F2
    assert not hasattr(model_input, "sentinel")

    # Evaluator can link them using sample_id
    assert model_input.sample_id == ground_truth.sample_id == "vct-101"

    # Verify ground truth fields are accessible for evaluation
    assert ground_truth.bug_status == "has_bug"
    assert ground_truth.bug_type == "encapsulation_break"
    assert "csharp.encapsulation" in ground_truth.knowledge_components
