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
