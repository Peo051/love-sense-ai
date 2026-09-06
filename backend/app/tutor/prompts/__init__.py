"""
Package prompts phiên bản hóa của CodeSense AI Tutor.
"""

from typing import Optional

from app.tutor.context_builder import (
    CodeSubmissionContext,
    LearnerPersonalizationContext,
    StudentContextBuilder,
    TokenBudgetConfig,
)
from app.tutor.prompts.diagnosis_v1 import DIAGNOSIS_SCHEMA_PROMPT_V1
from app.tutor.prompts.hint_v1 import (
    HINT_LEVEL_POLICY_V1,
    get_hint_instruction,
    is_solution_allowed,
)
from app.tutor.prompts.system_policy_v1 import PROMPT_VERSION, SYSTEM_POLICY_V1
from app.tutor.prompts.verification_v1 import (
    VERIFICATION_CHECKLIST_V1,
    verify_pedagogical_safety,
)

__all__ = [
    "CodeSubmissionContext",
    "DIAGNOSIS_SCHEMA_PROMPT_V1",
    "HINT_LEVEL_POLICY_V1",
    "LearnerPersonalizationContext",
    "PROMPT_VERSION",
    "SYSTEM_POLICY_V1",
    "StudentContextBuilder",
    "TokenBudgetConfig",
    "VERIFICATION_CHECKLIST_V1",
    "build_tutor_system_prompt",
    "build_tutor_user_prompt",
    "get_hint_instruction",
    "is_solution_allowed",
    "verify_pedagogical_safety",
]


def build_tutor_system_prompt(hint_level: int = 1) -> str:
    """
    Sinh system prompt hợp nhất từ các module system_policy_v1, diagnosis_v1 và hint_v1.
    """
    hint_instruction = get_hint_instruction(hint_level)

    return f"""{SYSTEM_POLICY_V1}

{DIAGNOSIS_SCHEMA_PROMPT_V1}

=== HƯỚNG DẪN CẤP ĐỘ GỢI Ý HIỆN TẠI ===
{hint_instruction}

=== ĐỊNH DẠNG JSON SCHEMA PHẢN HỒI (BẮT BUỘC) ===
Bạn PHẢI trả về duy nhất 1 JSON object theo định dạng sau:
{{
    "diagnosis": {{
        "issue_type": "string (syntax_error | semantic_error | logical_error | conceptual_misconception | oop_design_flaw | none)",
        "severity": "string (info | warning | error)",
        "location": "string hoặc null",
        "confidence": float (0.0 đến 1.0)
    }},
    "knowledge_components": ["tên các khái niệm OOP liên quan"],
    "possible_misconception": {{
        "type": "string",
        "description": "string (sử dụng ngữ nghĩa giả thuyết ngộ nhận)",
        "confidence": float (0.0 đến 1.0)
    }} hoặc null,
    "evidence": {{
        "code": "string (trích xuất từ untrusted student code)",
        "reason": "string"
    }} hoặc null,
    "teaching_strategy": "string",
    "tutor_response": "string (lời phản hồi sư phạm)",
    "hint_level": {hint_level},
    "solution_revealed": {"true" if is_solution_allowed(hint_level) else "false"},
    "next_action": "string (hành động cụ thể tiếp theo)",
    "prompt_version": "{PROMPT_VERSION}"
}}
"""


def build_tutor_user_prompt(
    *,
    problem_statement: str,
    student_code: str,
    compiler_error: Optional[str] = None,
    student_question: Optional[str] = None,
    topic: Optional[str] = None,
    hint_level: int = 1,
    personalization: Optional[LearnerPersonalizationContext] = None,
    current_diagnosis: Optional[dict] = None,
    hint_history: Optional[list[dict]] = None,
    context_builder: Optional[StudentContextBuilder] = None,
) -> str:
    """
    Sinh user prompt có cấu trúc và bao bọc toàn bộ dữ liệu người dùng nộp
    bên trong các thẻ phân định ranh giới dữ liệu không tin cậy (untrusted data boundaries).
    Áp dụng phân tách ranh giới nghiêm ngặt giữa <submitted_code_evidence>
    và <learner_pedagogical_context> thông qua StudentContextBuilder.
    """
    builder = context_builder or StudentContextBuilder()
    submission = CodeSubmissionContext(
        problem_statement=problem_statement,
        student_code=student_code,
        compiler_error=compiler_error,
        student_question=student_question,
        topic=topic,
        current_diagnosis=current_diagnosis,
        hint_history=hint_history or [],
    )
    return builder.build_user_prompt(
        submission=submission,
        personalization=personalization,
        hint_level=hint_level,
    )

