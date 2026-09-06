"""
Strict Whitelist ModelInput Schema for Clean-Room Research Evaluation.
APT-049: Enforce strict architectural boundary preventing ground-truth leakage into model inference.
"""

from typing import Any, Dict, Optional, Set
from pydantic import BaseModel, ConfigDict, Field, ValidationError


FORBIDDEN_GOLD_FIELDS: Set[str] = {
    "topic",
    "difficulty",
    "problem_family_id",
    "bug_status",
    "error_category",
    "bug_type",
    "bug_location",
    "knowledge_components",
    "possible_misconception",
    "reference_diagnosis",
    "evidence",
    "hint_1",
    "hint_2",
    "hint_3",
    "reference_solution",
    "explanation_vi",
    "review_status",
    "source_type",
    "split",
    "expected_behavior",
}

ALLOWED_MODEL_INPUT_FIELDS: Set[str] = {
    "sample_id",
    "problem_statement",
    "student_code",
    "compiler_error",
    "student_question",
}


class ModelInput(BaseModel):
    """
    Minimal immutable input object containing ONLY information legitimately visible to the model.

    Guarantees:
    1. Frozen/Immutable: Attributes cannot be modified or reassigned after construction.
    2. extra='forbid': Any unknown, malicious, or gold annotation fields cause an immediate ValidationError.
    3. Whitelist Construction: from_dataset_record() explicitly picks only allowed fields.
    """

    sample_id: str = Field(
        ...,
        description="Unique identifier for the benchmark problem instance.",
        min_length=1,
    )
    problem_statement: str = Field(
        ...,
        description="Vietnamese problem specification describing required behavior.",
        min_length=1,
    )
    student_code: str = Field(
        ...,
        description="Source code submitted by the student for diagnosis.",
    )
    compiler_error: Optional[str] = Field(
        default=None,
        description="Roslyn compiler error message (if any), or None.",
    )
    student_question: Optional[str] = Field(
        default=None,
        description="Optional student inquiry or reflection (only if experimentally justified).",
    )

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        str_strip_whitespace=True,
    )

    @classmethod
    def from_dataset_record(cls, record: Dict[str, Any]) -> "ModelInput":
        """
        Explicit whitelist conversion from a raw dataset record.

        CRITICAL ARCHITECTURAL RULES:
        - NEVER use ModelInput(**record).
        - NEVER copy the record dictionary (record.copy()).
        - NEVER dump and remove keys (model_dump then delete).
        - Explicitly select only legitimate fields one by one.
        """
        if not isinstance(record, dict):
            raise TypeError(f"Expected dict for dataset record, got {type(record).__name__}")

        # Resolve sample_id (support both 'id' from VietCSharpTutor and 'sample_id')
        sample_id_raw = record.get("id") or record.get("sample_id")
        if not sample_id_raw or not str(sample_id_raw).strip():
            raise ValueError("Dataset record missing mandatory 'id' or 'sample_id' field.")
        sample_id = str(sample_id_raw).strip()

        # Resolve problem_statement (support 'problem_statement_vi' from VietCSharpTutor)
        problem_statement_raw = record.get("problem_statement_vi") or record.get("problem_statement")
        if not problem_statement_raw or not str(problem_statement_raw).strip():
            raise ValueError(f"Dataset record '{sample_id}' missing mandatory problem statement.")
        problem_statement = str(problem_statement_raw).strip()

        # Resolve student_code
        student_code_raw = record.get("student_code")
        if student_code_raw is None:
            raise ValueError(f"Dataset record '{sample_id}' missing 'student_code' field.")
        student_code = str(student_code_raw)

        # Resolve optional compiler_error
        compiler_error_raw = record.get("compiler_error")
        compiler_error: Optional[str] = None
        if compiler_error_raw is not None and str(compiler_error_raw).strip():
            compiler_error = str(compiler_error_raw).strip()

        # Resolve optional student_question
        student_question_raw = record.get("student_question")
        student_question: Optional[str] = None
        if student_question_raw is not None and str(student_question_raw).strip():
            student_question = str(student_question_raw).strip()

        # Strict whitelist instantiation
        return cls(
            sample_id=sample_id,
            problem_statement=problem_statement,
            student_code=student_code,
            compiler_error=compiler_error,
            student_question=student_question,
        )

    def to_model_dict(self) -> Dict[str, Any]:
        """
        Return a clean dictionary representation for LLM prompt construction.
        Guaranteed to contain zero ground-truth keys.
        """
        data = self.model_dump()
        # Defensive assertion: ensure no forbidden fields ever exist
        leaked = set(data.keys()) & FORBIDDEN_GOLD_FIELDS
        if leaked:
            raise RuntimeError(f"CRITICAL: Forbidden gold fields detected in ModelInput dict: {leaked}")
        return data


GROUND_TRUTH_SENTINEL_71F2: str = "GROUND_TRUTH_SENTINEL_71F2"


class GroundTruth(BaseModel):
    """
    Dedicated GroundTruth schema accessible ONLY to offline evaluator and dataset-validation layer.

    Guarantees:
    1. STRICT ISOLATION: GroundTruth must never be accepted by:
       - prompt builder
       - provider client
       - model runner
       - student context builder
    2. Frozen/Immutable: Attributes cannot be reassigned after construction.
    3. extra='forbid': Any unknown or unauthorized fields cause an immediate ValidationError.
    4. Deliberate sentinel: Contains GROUND_TRUTH_SENTINEL_71F2 ensuring leakage detection in model requests.
    """

    sample_id: str = Field(
        ...,
        description="Unique identifier linking GroundTruth with ModelInput and Prediction.",
        min_length=1,
    )
    expected_behavior: str = Field(
        default="",
        description="Ground-truth expected behavior description.",
    )
    bug_status: str = Field(
        ...,
        description="Gold label: 'has_bug', 'no_bug', or 'insufficient_context'.",
        min_length=1,
    )
    error_category: str = Field(
        default="",
        description="Gold label for error category (e.g., 'compile_error', 'logic_error').",
    )
    bug_type: str = Field(
        default="",
        description="Gold label for specific bug type.",
    )
    bug_location: Optional[str] = Field(
        default=None,
        description="Gold label for bug line or code snippet.",
    )
    knowledge_components: list[str] = Field(
        default_factory=list,
        description="Gold list of relevant knowledge component tags.",
    )
    possible_misconception: Optional[str] = Field(
        default=None,
        description="Gold student misconception hypothesis.",
    )
    reference_diagnosis: str = Field(
        default="",
        description="Gold expert diagnostic explanation.",
    )
    evidence: Optional[str] = Field(
        default=None,
        description="Gold evidence substring from student_code.",
    )
    reference_solution: str = Field(
        default="",
        description="Gold reference patch or correct solution code.",
    )
    hint_1: str = Field(
        default="",
        description="Gold Socratic hint tier 1.",
    )
    hint_2: str = Field(
        default="",
        description="Gold conceptual hint tier 2.",
    )
    hint_3: str = Field(
        default="",
        description="Gold tactical hint tier 3.",
    )
    explanation_vi: str = Field(
        default="",
        description="Gold full Vietnamese pedagogical explanation.",
    )
    sentinel: str = Field(
        default=GROUND_TRUTH_SENTINEL_71F2,
        description="Deliberate sentinel tag to detect leakage into model prompts or requests.",
    )

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        str_strip_whitespace=True,
    )

    @classmethod
    def from_dataset_record(cls, record: Dict[str, Any]) -> "GroundTruth":
        """
        Explicit extraction of gold-standard annotations from raw dataset record.
        Only used by offline evaluation metric calculators and dataset validators.
        """
        if not isinstance(record, dict):
            raise TypeError(f"Expected dict for dataset record, got {type(record).__name__}")

        sample_id_raw = record.get("id") or record.get("sample_id")
        if not sample_id_raw or not str(sample_id_raw).strip():
            raise ValueError("Dataset record missing mandatory 'id' or 'sample_id' for GroundTruth.")
        sample_id = str(sample_id_raw).strip()

        bug_status = str(record.get("bug_status") or "").strip()
        if not bug_status:
            raise ValueError(f"Dataset record '{sample_id}' missing mandatory 'bug_status'.")

        return cls(
            sample_id=sample_id,
            expected_behavior=str(record.get("expected_behavior") or "").strip(),
            bug_status=bug_status,
            error_category=str(record.get("error_category") or "").strip(),
            bug_type=str(record.get("bug_type") or "").strip(),
            bug_location=str(record.get("bug_location")).strip() if record.get("bug_location") is not None else None,
            knowledge_components=list(record.get("knowledge_components") or []),
            possible_misconception=str(record.get("possible_misconception")).strip() if record.get("possible_misconception") is not None else None,
            reference_diagnosis=str(record.get("reference_diagnosis") or "").strip(),
            evidence=str(record.get("evidence")).strip() if record.get("evidence") is not None else None,
            reference_solution=str(record.get("reference_solution") or "").strip(),
            hint_1=str(record.get("hint_1") or "").strip(),
            hint_2=str(record.get("hint_2") or "").strip(),
            hint_3=str(record.get("hint_3") or "").strip(),
            explanation_vi=str(record.get("explanation_vi") or "").strip(),
            sentinel=GROUND_TRUTH_SENTINEL_71F2,
        )


class EvaluationMetadata(BaseModel):
    """
    Non-gold experiment bookkeeping and stratification metadata.
    Accessible only to dataset managers, offline evaluators (for stratified slices), and manifest writers.

    CRITICAL SECURITY INVARIANT:
    Must NEVER be visible to the model, prompt builders, or provider clients by default.
    Contains potentially confounding tags like topic and difficulty.
    """

    sample_id: str = Field(
        ...,
        description="Unique sample identifier linking with ModelInput and GroundTruth.",
        min_length=1,
    )
    split: str = Field(
        default="test",
        description="Dataset split: 'dev', 'validation', or 'test'.",
    )
    dataset_version: str = Field(
        default="1.0.0",
        description="Version string of the benchmark dataset.",
    )
    source_type: str = Field(
        default="expert_authored",
        description="Authoring provenance ('expert_authored', 'controlled_mutation', etc.).",
    )
    problem_family_id: str = Field(
        default="",
        description="Problem family grouping to verify anti-leakage cross-split isolation.",
    )
    topic: str = Field(
        default="",
        description="OOP topic tag (e.g. 'csharp.encapsulation') for post-hoc stratification only.",
    )
    difficulty: str = Field(
        default="beginner",
        description="Difficulty tier ('beginner', 'easy', 'medium') for post-hoc stratification only.",
    )
    review_status: str = Field(
        default="approved",
        description="Quality assurance review status.",
    )
    run_id: Optional[str] = Field(
        default=None,
        description="Optional experiment run identifier.",
    )

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        str_strip_whitespace=True,
    )

    @classmethod
    def from_dataset_record(cls, record: Dict[str, Any], run_id: Optional[str] = None) -> "EvaluationMetadata":
        """
        Explicit extraction of experiment metadata from raw dataset record.
        """
        if not isinstance(record, dict):
            raise TypeError(f"Expected dict for dataset record, got {type(record).__name__}")

        sample_id_raw = record.get("id") or record.get("sample_id")
        if not sample_id_raw or not str(sample_id_raw).strip():
            raise ValueError("Dataset record missing mandatory 'id' or 'sample_id' for EvaluationMetadata.")

        return cls(
            sample_id=str(sample_id_raw).strip(),
            split=str(record.get("split") or "test").strip(),
            dataset_version=str(record.get("dataset_version") or "1.0.0").strip(),
            source_type=str(record.get("source_type") or "expert_authored").strip(),
            problem_family_id=str(record.get("problem_family_id") or "").strip(),
            topic=str(record.get("topic") or "").strip(),
            difficulty=str(record.get("difficulty") or "beginner").strip(),
            review_status=str(record.get("review_status") or "approved").strip(),
            run_id=run_id,
        )


class EvaluationRecord(BaseModel):
    """
    Canonical clean-room container encapsulating the complete lifecycle of an evaluation sample.

    Architecture:
    ├── model_input: Strictly whitelisted fields visible to the model during inference.
    ├── ground_truth: Isolated gold annotations for offline grading only.
    └── metadata: Non-gold experiment bookkeeping and slicing tags.

    Invariants:
    - Inference API must receive ONLY model_input.
    - Offline Evaluator receives: prediction, ground_truth, and optionally metadata.
    - Manifest writer receives: metadata.
    """

    model_input: ModelInput
    ground_truth: GroundTruth
    metadata: EvaluationMetadata

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
    )

    @classmethod
    def from_dataset_record(cls, record: Dict[str, Any], run_id: Optional[str] = None) -> "EvaluationRecord":
        """
        Parse a raw dataset record and cleanly decompose it into 3 strictly isolated objects.
        """
        return cls(
            model_input=ModelInput.from_dataset_record(record),
            ground_truth=GroundTruth.from_dataset_record(record),
            metadata=EvaluationMetadata.from_dataset_record(record, run_id=run_id),
        )

    def get_inference_input(self) -> ModelInput:
        """Explicit getter guaranteeing only ModelInput is handed to inference."""
        return self.model_input


def assert_not_ground_truth(data: Any) -> None:
    """
    Runtime security assertion ensuring GroundTruth, EvaluationMetadata, or EvaluationRecord
    is NEVER passed into inference components.
    Raises TypeError if forbidden object or sentinel is detected.
    """
    if isinstance(data, GroundTruth):
        raise TypeError(
            "CRITICAL ARCHITECTURAL VIOLATION: GroundTruth object passed to inference component! "
            "Model inference must strictly receive ModelInput."
        )
    if isinstance(data, EvaluationMetadata):
        raise TypeError(
            "CRITICAL ARCHITECTURAL VIOLATION: EvaluationMetadata object passed to inference component! "
            "Bookkeeping metadata must remain strictly outside the inference path."
        )
    if isinstance(data, EvaluationRecord):
        raise TypeError(
            "CRITICAL ARCHITECTURAL VIOLATION: Combined EvaluationRecord passed to inference component! "
            "Inference API must receive ONLY model_input (call record.get_inference_input())."
        )
    if isinstance(data, dict):
        if data.get("sentinel") == GROUND_TRUTH_SENTINEL_71F2:
            raise TypeError(
                "CRITICAL ARCHITECTURAL VIOLATION: GroundTruth sentinel detected in inference payload!"
            )
    if isinstance(data, str) and GROUND_TRUTH_SENTINEL_71F2 in data:
        raise TypeError(
            "CRITICAL ARCHITECTURAL VIOLATION: GroundTruth sentinel detected in string payload!"
        )


def verify_inference_input(input_obj: Any) -> ModelInput:
    """
    Ensures that the input passed to inference/prompt builder is strictly a ModelInput
    and NEVER a GroundTruth object or raw dictionary containing GroundTruth.
    """
    assert_not_ground_truth(input_obj)
    if isinstance(input_obj, ModelInput):
        return input_obj
    if isinstance(input_obj, dict):
        return ModelInput.from_dataset_record(input_obj)
    raise TypeError(f"Expected ModelInput or clean record dict, got {type(input_obj).__name__}")
