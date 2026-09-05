"""
Taxonomy phân loại lỗi lập trình C# OOP dành cho sinh viên mới học (Beginner C# OOP Taxonomy).

Định nghĩa 8 nhóm chẩn đoán cốt lõi và các nhãn chuẩn hóa, ngăn chặn việc sử dụng các nhãn tự do (free-form labels).
"""

from typing import Any, Optional

from app.schemas.tutor_schema import DiagnosisCategory


# Bảng từ vựng chuẩn hóa các lỗi C# OOP cơ bản cho từng category
TAXONOMY_ISSUE_TYPES: dict[DiagnosisCategory, list[str]] = {
    DiagnosisCategory.COMPILE_ERROR: [
        "syntax_error",
        "type_mismatch",
        "missing_semicolon",
        "unassigned_variable",
        "missing_member",
        "inaccessible_member",
        "invalid_return_type",
        "missing_return_statement",
        "missing_closing_brace",
    ],
    DiagnosisCategory.RUNTIME_ERROR: [
        "recursive_property_accessor",
        "null_reference_risk",
        "index_out_of_range",
        "divide_by_zero",
        "invalid_cast",
        "stack_overflow_risk",
    ],
    DiagnosisCategory.LOGIC_ERROR: [
        "parameter_field_shadowing",
        "invalid_setter_validation",
        "incorrect_calculation",
        "off_by_one",
        "inverted_condition",
        "unreachable_code",
        "state_not_updated",
        "semantic_error",
        "logical_error",
    ],
    DiagnosisCategory.CONCEPTUAL_MISUSE: [
        "static_instance_confusion",
        "encapsulation_bypass",
        "constructor_return_type",
        "improper_inheritance",
        "overload_override_confusion",
        "reference_vs_value_confusion",
    ],
    DiagnosisCategory.REQUIREMENT_VIOLATION: [
        "missing_required_member",
        "incorrect_signature",
        "incorrect_access_modifier",
        "missing_validation_requirement",
        "unmet_specification",
    ],
    DiagnosisCategory.NO_BUG: [
        "no_issue_detected",
        "correct_implementation",
    ],
    DiagnosisCategory.INSUFFICIENT_CONTEXT: [
        "incomplete_code",
        "missing_class_body",
        "empty_submission",
    ],
    DiagnosisCategory.UNKNOWN: [
        "unclassified_issue",
    ],
}

# Bảng ánh xạ các biến thể/từ đồng nghĩa về DiagnosisCategory
CATEGORY_ALIASES: dict[str, DiagnosisCategory] = {
    # compile_error
    "compile_error": DiagnosisCategory.COMPILE_ERROR,
    "syntax_error": DiagnosisCategory.COMPILE_ERROR,
    "syntax": DiagnosisCategory.COMPILE_ERROR,
    "compilation_error": DiagnosisCategory.COMPILE_ERROR,
    "compiler_error": DiagnosisCategory.COMPILE_ERROR,
    "build_error": DiagnosisCategory.COMPILE_ERROR,
    # runtime_error
    "runtime_error": DiagnosisCategory.RUNTIME_ERROR,
    "runtime": DiagnosisCategory.RUNTIME_ERROR,
    "stackoverflow": DiagnosisCategory.RUNTIME_ERROR,
    "stack_overflow": DiagnosisCategory.RUNTIME_ERROR,
    "nullreference": DiagnosisCategory.RUNTIME_ERROR,
    "null_pointer": DiagnosisCategory.RUNTIME_ERROR,
    "exception": DiagnosisCategory.RUNTIME_ERROR,
    # logic_error
    "logic_error": DiagnosisCategory.LOGIC_ERROR,
    "logical_error": DiagnosisCategory.LOGIC_ERROR,
    "logic": DiagnosisCategory.LOGIC_ERROR,
    "semantic_error": DiagnosisCategory.LOGIC_ERROR,
    "bug": DiagnosisCategory.LOGIC_ERROR,
    # conceptual_misuse
    "conceptual_misuse": DiagnosisCategory.CONCEPTUAL_MISUSE,
    "conceptual_misconception": DiagnosisCategory.CONCEPTUAL_MISUSE,
    "conceptual": DiagnosisCategory.CONCEPTUAL_MISUSE,
    "oop_design_flaw": DiagnosisCategory.CONCEPTUAL_MISUSE,
    "oop_misuse": DiagnosisCategory.CONCEPTUAL_MISUSE,
    "misconception": DiagnosisCategory.CONCEPTUAL_MISUSE,
    # requirement_violation
    "requirement_violation": DiagnosisCategory.REQUIREMENT_VIOLATION,
    "specification_violation": DiagnosisCategory.REQUIREMENT_VIOLATION,
    "missing_requirement": DiagnosisCategory.REQUIREMENT_VIOLATION,
    "requirement": DiagnosisCategory.REQUIREMENT_VIOLATION,
    # no_bug
    "no_bug": DiagnosisCategory.NO_BUG,
    "none": DiagnosisCategory.NO_BUG,
    "no_issue": DiagnosisCategory.NO_BUG,
    "no_error": DiagnosisCategory.NO_BUG,
    "correct": DiagnosisCategory.NO_BUG,
    "valid": DiagnosisCategory.NO_BUG,
    "ok": DiagnosisCategory.NO_BUG,
    # insufficient_context
    "insufficient_context": DiagnosisCategory.INSUFFICIENT_CONTEXT,
    "incomplete_code": DiagnosisCategory.INSUFFICIENT_CONTEXT,
    "incomplete": DiagnosisCategory.INSUFFICIENT_CONTEXT,
    "missing_context": DiagnosisCategory.INSUFFICIENT_CONTEXT,
    "too_short": DiagnosisCategory.INSUFFICIENT_CONTEXT,
    # unknown
    "unknown": DiagnosisCategory.UNKNOWN,
    "unclassified": DiagnosisCategory.UNKNOWN,
    "other": DiagnosisCategory.UNKNOWN,
}

# Bảng ánh xạ cụ thể từ biến thể issue_type về (DiagnosisCategory, chuẩn issue_type)
ISSUE_TYPE_ALIASES: dict[str, tuple[DiagnosisCategory, str]] = {
    # semantic / logical / syntax
    "semantic_error": (DiagnosisCategory.LOGIC_ERROR, "semantic_error"),
    "logical_error": (DiagnosisCategory.LOGIC_ERROR, "logical_error"),
    "syntax_error": (DiagnosisCategory.COMPILE_ERROR, "syntax_error"),
    # recursive getter
    "recursive_property_accessor": (DiagnosisCategory.RUNTIME_ERROR, "recursive_property_accessor"),
    "recursive_getter": (DiagnosisCategory.RUNTIME_ERROR, "recursive_property_accessor"),
    "recursive_property": (DiagnosisCategory.RUNTIME_ERROR, "recursive_property_accessor"),
    "property_recursion": (DiagnosisCategory.RUNTIME_ERROR, "recursive_property_accessor"),
    "getter_stack_overflow": (DiagnosisCategory.RUNTIME_ERROR, "recursive_property_accessor"),
    # parameter shadowing
    "parameter_field_shadowing": (DiagnosisCategory.LOGIC_ERROR, "parameter_field_shadowing"),
    "parameter_shadowing": (DiagnosisCategory.LOGIC_ERROR, "parameter_field_shadowing"),
    "variable_shadowing": (DiagnosisCategory.LOGIC_ERROR, "parameter_field_shadowing"),
    "field_shadowing": (DiagnosisCategory.LOGIC_ERROR, "parameter_field_shadowing"),
    "shadowing": (DiagnosisCategory.LOGIC_ERROR, "parameter_field_shadowing"),
    # invalid setter
    "invalid_setter_validation": (DiagnosisCategory.LOGIC_ERROR, "invalid_setter_validation"),
    "setter_validation": (DiagnosisCategory.LOGIC_ERROR, "invalid_setter_validation"),
    "invalid_setter": (DiagnosisCategory.LOGIC_ERROR, "invalid_setter_validation"),
    "setter_bug": (DiagnosisCategory.LOGIC_ERROR, "invalid_setter_validation"),
    # static instance confusion
    "static_instance_confusion": (DiagnosisCategory.CONCEPTUAL_MISUSE, "static_instance_confusion"),
    "static_vs_instance": (DiagnosisCategory.CONCEPTUAL_MISUSE, "static_instance_confusion"),
    "static_confusion": (DiagnosisCategory.CONCEPTUAL_MISUSE, "static_instance_confusion"),
    "cs0120": (DiagnosisCategory.CONCEPTUAL_MISUSE, "static_instance_confusion"),
    "object_reference_required": (DiagnosisCategory.CONCEPTUAL_MISUSE, "static_instance_confusion"),
    # no bug
    "no_issue_detected": (DiagnosisCategory.NO_BUG, "no_issue_detected"),
    "correct_implementation": (DiagnosisCategory.NO_BUG, "correct_implementation"),
    "none": (DiagnosisCategory.NO_BUG, "no_issue_detected"),
    "correct": (DiagnosisCategory.NO_BUG, "no_issue_detected"),
    "valid": (DiagnosisCategory.NO_BUG, "no_issue_detected"),
    # insufficient context
    "incomplete_code": (DiagnosisCategory.INSUFFICIENT_CONTEXT, "incomplete_code"),
    "missing_class_body": (DiagnosisCategory.INSUFFICIENT_CONTEXT, "missing_class_body"),
    "empty_submission": (DiagnosisCategory.INSUFFICIENT_CONTEXT, "empty_submission"),
    "incomplete": (DiagnosisCategory.INSUFFICIENT_CONTEXT, "incomplete_code"),
    "insufficient": (DiagnosisCategory.INSUFFICIENT_CONTEXT, "incomplete_code"),
}


def normalize_category(val: Any) -> DiagnosisCategory:
    """
    Chuẩn hóa chuỗi hoặc enum bất kỳ về một trong 8 DiagnosisCategory hợp lệ.
    """
    if isinstance(val, DiagnosisCategory):
        return val

    if not val or not isinstance(val, str):
        return DiagnosisCategory.UNKNOWN

    cleaned = val.strip().lower()
    if cleaned in CATEGORY_ALIASES:
        return CATEGORY_ALIASES[cleaned]

    for category in DiagnosisCategory:
        if cleaned == category.value:
            return category

    return DiagnosisCategory.UNKNOWN


def normalize_issue_type(issue_type_raw: Any, category: DiagnosisCategory) -> str:
    """
    Chuẩn hóa tên lỗi issue_type dựa trên taxonomy của category.
    """
    if not issue_type_raw or not isinstance(issue_type_raw, str):
        return TAXONOMY_ISSUE_TYPES[category][0]

    cleaned = issue_type_raw.strip().lower().replace(" ", "_").replace("-", "_")

    if cleaned in ISSUE_TYPE_ALIASES:
        return ISSUE_TYPE_ALIASES[cleaned][1]

    allowed_for_cat = TAXONOMY_ISSUE_TYPES.get(category, [])
    if cleaned in allowed_for_cat:
        return cleaned

    for standard_type in allowed_for_cat:
        if standard_type in cleaned or cleaned in standard_type:
            return standard_type

    return allowed_for_cat[0] if allowed_for_cat else "unclassified_issue"


def normalize_diagnosis_labels(
    category_raw: Any,
    issue_type_raw: Any,
) -> tuple[DiagnosisCategory, str]:
    """
    Chuẩn hóa đồng thời cả category và issue_type thành cặp nhãn chuẩn trong taxonomy.
    """
    cleaned_issue = (
        str(issue_type_raw).strip().lower().replace(" ", "_").replace("-", "_")
        if issue_type_raw
        else ""
    )

    if cleaned_issue in ISSUE_TYPE_ALIASES:
        implied_category, standard_issue = ISSUE_TYPE_ALIASES[cleaned_issue]
        category = (
            normalize_category(category_raw)
            if category_raw and category_raw != "unknown"
            else implied_category
        )
        if category == DiagnosisCategory.UNKNOWN:
            category = implied_category
        return category, standard_issue

    category = normalize_category(category_raw)
    issue_type = normalize_issue_type(cleaned_issue, category)
    return category, issue_type


def is_valid_taxonomy_label(category: DiagnosisCategory, issue_type: str) -> bool:
    """
    Kiểm tra xem issue_type có thuộc bảng taxonomy chuẩn của category hay không.
    """
    return issue_type in TAXONOMY_ISSUE_TYPES.get(category, [])
