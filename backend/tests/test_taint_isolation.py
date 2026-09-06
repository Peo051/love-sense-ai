import pytest
import json
from pathlib import Path
from app.evaluation.prompts import (
    build_prompt_a,
    build_prompt_b,
    build_prompt_c,
    build_prompt_d,
)
from app.tutor.context_builder import StudentContextBuilder, CodeSubmissionContext, LearnerPersonalizationContext

SENTINEL_REF_SOLUTION = "SENTINEL_REF_SOL_92F1"
SENTINEL_REF_DIAGNOSIS = "SENTINEL_REF_DIAG_81E2"
SENTINEL_BUG_TYPE = "SENTINEL_BUG_TYPE_73D3"
SENTINEL_BUG_LOCATION = "SENTINEL_BUG_LOC_SYMBOL_64C4"
SENTINEL_HINT_1 = "SENTINEL_HINT_1_55B5"
SENTINEL_HINT_2 = "SENTINEL_HINT_2_46A6"
SENTINEL_HINT_3 = "SENTINEL_HINT_3_3797"
SENTINEL_MISCONCEPTION = "SENTINEL_MISCONCEPTION_2888"
SENTINEL_KC = "OOP.SENTINEL_KC_1979"

@pytest.fixture
def mock_tainted_case():
    return {
        "id": "vct-taint-sentinel",
        "language": "csharp",
        "topic": "class_object",
        "difficulty": "beginner",
        "problem_statement_vi": "Khai báo lớp Diem2D với hai toạ độ x, y.",
        "student_code": "public class Diem2D { int x; int y; }",
        "compiler_error": None,
        "bug_status": "has_bug",
        "error_category": "conceptual_misuse",
        "bug_type": SENTINEL_BUG_TYPE,
        "bug_location": {
            "file": "Program.cs",
            "start_line": 1,
            "end_line": 1,
            "symbol": SENTINEL_BUG_LOCATION
        },
        "knowledge_components": [SENTINEL_KC],
        "possible_misconception": SENTINEL_MISCONCEPTION,
        "reference_diagnosis": SENTINEL_REF_DIAGNOSIS,
        "evidence": "int x; int y;",
        "hint_1": SENTINEL_HINT_1,
        "hint_2": SENTINEL_HINT_2,
        "hint_3": SENTINEL_HINT_3,
        "reference_solution": f"public class Diem2D {{ public int X {{ get; set; }} public int Y {{ get; set; }} }} // {SENTINEL_REF_SOLUTION}",
        "explanation_vi": "Cần sử dụng thuộc tính thay vì trường dữ liệu.",
        "source_type": "expert",
        "split": "validation",
        "review_status": "reviewed"
    }


def test_reference_solution_never_reaches_prompt(mock_tainted_case):
    """Kiểm tra reference_solution tuyệt đối không lọt vào bất kỳ prompt nào của C hoặc D."""
    p_c = build_prompt_c(
        mock_tainted_case["problem_statement_vi"],
        mock_tainted_case["student_code"],
        mock_tainted_case["compiler_error"]
    )
    assert SENTINEL_REF_SOLUTION not in p_c

    clean_ctx = {"attempt_count": 1, "struggling_kcs": [], "recent_misconceptions": []}
    p_d = build_prompt_d(
        mock_tainted_case["problem_statement_vi"],
        mock_tainted_case["student_code"],
        mock_tainted_case["compiler_error"],
        student_context=clean_ctx
    )
    assert SENTINEL_REF_SOLUTION not in p_d


def test_reference_diagnosis_never_reaches_prompt(mock_tainted_case):
    """Kiểm tra reference_diagnosis không lọt vào prompt C hoặc D."""
    p_c = build_prompt_c(
        mock_tainted_case["problem_statement_vi"],
        mock_tainted_case["student_code"],
        mock_tainted_case["compiler_error"]
    )
    assert SENTINEL_REF_DIAGNOSIS not in p_c

    p_d = build_prompt_d(
        mock_tainted_case["problem_statement_vi"],
        mock_tainted_case["student_code"],
        mock_tainted_case["compiler_error"],
        student_context={}
    )
    assert SENTINEL_REF_DIAGNOSIS not in p_d


def test_bug_type_never_reaches_prompt(mock_tainted_case):
    """Kiểm tra nhãn bug_type không bị đưa vào prompt của các hệ thống đề xuất."""
    p_c = build_prompt_c(
        mock_tainted_case["problem_statement_vi"],
        mock_tainted_case["student_code"],
        mock_tainted_case["compiler_error"]
    )
    assert SENTINEL_BUG_TYPE not in p_c


def test_bug_location_never_reaches_prompt(mock_tainted_case):
    """Kiểm tra nhãn bug_location không bị rò rỉ vào prompt."""
    p_c = build_prompt_c(
        mock_tainted_case["problem_statement_vi"],
        mock_tainted_case["student_code"],
        mock_tainted_case["compiler_error"]
    )
    assert SENTINEL_BUG_LOCATION not in p_c


def test_reference_hints_never_reach_prompt(mock_tainted_case):
    """Kiểm tra các gợi ý mẫu (hint_1, hint_2, hint_3) không bị đưa vào prompt của hệ thống C."""
    p_c = build_prompt_c(
        mock_tainted_case["problem_statement_vi"],
        mock_tainted_case["student_code"],
        mock_tainted_case["compiler_error"]
    )
    assert SENTINEL_HINT_1 not in p_c
    assert SENTINEL_HINT_2 not in p_c
    assert SENTINEL_HINT_3 not in p_c


def test_ground_truth_dictionary_cannot_be_serialized_into_context(mock_tainted_case):
    """Kiểm tra toàn bộ dict ground-truth không thể bị serialize thẳng vào prompt thông qua context builder."""
    builder = StudentContextBuilder()
    code_sub = CodeSubmissionContext(
        problem_statement=mock_tainted_case["problem_statement_vi"],
        student_code=mock_tainted_case["student_code"],
        compiler_error=mock_tainted_case["compiler_error"]
    )
    learner_ctx = LearnerPersonalizationContext()
    
    # Prompt render
    user_prompt = builder.build_user_prompt(code_sub, learner_ctx)
    for sentinel in [SENTINEL_REF_SOLUTION, SENTINEL_REF_DIAGNOSIS, SENTINEL_BUG_TYPE, SENTINEL_HINT_1]:
        assert sentinel not in user_prompt


def test_proposed_d_student_context_contains_no_gold_annotations(mock_tainted_case):
    """Kiểm toán Student Context của Proposed D: Nếu truyền gold KC hoặc misconception thì phải phát hiện được rò rỉ."""
    # Khi dùng student context an toàn độc lập
    valid_student_context = {
        "attempt_count": 1,
        "struggling_kcs": ["OOP.General"],
        "recent_misconceptions": ["general_syntax_confusion"]
    }
    p_d_clean = build_prompt_d(
        mock_tainted_case["problem_statement_vi"],
        mock_tainted_case["student_code"],
        mock_tainted_case["compiler_error"],
        student_context=valid_student_context
    )
    assert SENTINEL_KC not in p_d_clean
    assert SENTINEL_MISCONCEPTION not in p_d_clean

    # Khi giả định truyền thẳng gold annotations vào student context (ô nhiễm)
    contaminated_context = {
        "attempt_count": 1,
        "struggling_kcs": mock_tainted_case["knowledge_components"],
        "recent_misconceptions": [mock_tainted_case["possible_misconception"]]
    }
    p_d_contaminated = build_prompt_d(
        mock_tainted_case["problem_statement_vi"],
        mock_tainted_case["student_code"],
        mock_tainted_case["compiler_error"],
        student_context=contaminated_context
    )
    # Taint detector phải phát hiện được sự rò rỉ này
    assert SENTINEL_KC in p_d_contaminated
    assert SENTINEL_MISCONCEPTION in p_d_contaminated
