"""
Đặc tả prompt đông băng cho 4 hệ thống đánh giá VietCSharpTutor (APT-028).

- Baseline A: Direct LLM Debugging Prompt
- Baseline B: Generic Tutor Prompt
- Proposed C: Structured Diagnosis + Progressive Hints
- Proposed D: Structured Diagnosis + Progressive Hints + Student Context

Mọi prompt đều được gắn phiên bản (v1.0) và không được thay đổi trong quá trình thực nghiệm.
"""

from typing import Any, Dict, Optional, Union
from app.evaluation.schemas import ModelInput, assert_not_ground_truth

PROMPT_VERSIONS = {
    "A": "v1.0-direct-debug",
    "B": "v1.0-generic-tutor",
    "C": "v1.0-structured-progressive",
    "D": "v1.0-contextual-adaptive"
}

# --- BASELINE A: Direct LLM Debugging Prompt ---
SYSTEM_PROMPT_A = """Bạn là một lập trình viên C# chuyên nghiệp. Hãy đọc đoạn mã nguồn học viên và tìm lỗi.
Hãy chỉ ra lỗi và viết lại mã nguồn đã sửa."""

def build_prompt_a(
    problem_statement: Union[str, ModelInput],
    student_code: Optional[str] = None,
    compiler_error: Optional[str] = None
) -> str:
    assert_not_ground_truth(problem_statement)
    if isinstance(problem_statement, ModelInput):
        mi = problem_statement
        problem_statement = mi.problem_statement
        student_code = mi.student_code
        compiler_error = mi.compiler_error
    else:
        assert_not_ground_truth(student_code)
        assert_not_ground_truth(compiler_error)

    err_text = f"\nThông báo lỗi biên dịch: {compiler_error}" if compiler_error else ""
    return f"""Đề bài:
{problem_statement}

Mã nguồn học sinh:{err_text}
```csharp
{student_code}
```

Hãy tìm lỗi trong đoạn mã trên và cung cấp mã nguồn đã sửa chữa hoàn chỉnh."""


# --- BASELINE B: Generic Tutor Prompt ---
SYSTEM_PROMPT_B = """Bạn là gia sư AI dạy lập trình C#. Nhiệm vụ của bạn là giải thích lỗi cho người học một cách thân thiện và dễ hiểu.
Hãy giải thích lỗi sai và gợi ý cách khắc phục."""

def build_prompt_b(
    problem_statement: Union[str, ModelInput],
    student_code: Optional[str] = None,
    compiler_error: Optional[str] = None
) -> str:
    assert_not_ground_truth(problem_statement)
    if isinstance(problem_statement, ModelInput):
        mi = problem_statement
        problem_statement = mi.problem_statement
        student_code = mi.student_code
        compiler_error = mi.compiler_error
    else:
        assert_not_ground_truth(student_code)
        assert_not_ground_truth(compiler_error)

    err_text = f"\nThông báo lỗi biên dịch: {compiler_error}" if compiler_error else ""
    return f"""Đề bài:
{problem_statement}

Mã nguồn học sinh:{err_text}
```csharp
{student_code}
```

Hãy hướng dẫn học sinh giải quyết vấn đề trên bằng tiếng Việt."""


# --- PROPOSED C: Structured Diagnosis + Progressive Hints ---
SYSTEM_PROMPT_C = """Bạn là CodeSense AI Tutor - Hệ thống gia sư lập trình C# hướng đối tượng chuyên sâu cho người mới bắt đầu.
Nhiệm vụ của bạn là chẩn đoán sư phạm chính xác và cung cấp gợi ý tăng dần (Progressive Scaffolding) theo chuẩn cấu trúc JSON.

Quy tắc bắt buộc:
1. Xác định bug_status: "has_bug", "no_bug", hoặc "insufficient_context".
2. Phân loại error_category: "compile_error", "runtime_error", "logic_error", "conceptual_misuse", "requirement_violation", "no_bug", "insufficient_context".
3. evidence: Phải là một đoạn chuỗi trích xuất NGUYÊN VĂN (exact substring) từ student_code. Nếu no_bug thì null.
4. bug_location: Đối tượng {"file": "Program.cs", "start_line": int, "end_line": int, "symbol": string}. Nếu no_bug/insufficient_context thì null.
5. Quy tắc 3 tầng Gợi ý (Progressive Hinting Policy):
   - Hint 1 (Directional): Câu hỏi định hướng tư duy, KHÔNG tiết lộ giải pháp hoặc mã sửa.
   - Hint 2 (Conceptual Scaffolding): Giải thích bản chất khái niệm OOP liên quan.
   - Hint 3 (Tactical): Hướng dẫn hành động cụ thể tại vị trí lỗi nhưng không đưa nguyên văn toàn bộ mã giải pháp.
6. knowledge_components: Danh sách các thẻ kiến thức (ví dụ: ["OOP.Classes", "OOP.Constructors"]).
7. possible_misconception: Quan niệm sai lầm cốt lõi của người học (null nếu no_bug).
8. Đầu ra BẮT BUỘC là một JSON object duy nhất hợp lệ theo đúng cấu trúc chỉ định."""

def build_prompt_c(
    problem_statement: Union[str, ModelInput],
    student_code: Optional[str] = None,
    compiler_error: Optional[str] = None
) -> str:
    assert_not_ground_truth(problem_statement)
    if isinstance(problem_statement, ModelInput):
        mi = problem_statement
        problem_statement = mi.problem_statement
        student_code = mi.student_code
        compiler_error = mi.compiler_error
    else:
        assert_not_ground_truth(student_code)
        assert_not_ground_truth(compiler_error)

    err_text = f"\nThông báo lỗi biên dịch: {compiler_error}" if compiler_error else ""
    return f"""Đề bài:
{problem_statement}

Mã nguồn học sinh:{err_text}
```csharp
{student_code}
```

Hãy chẩn đoán sư phạm và trả về kết quả JSON với các trường:
{{
    "bug_status": "has_bug" | "no_bug" | "insufficient_context",
    "error_category": string,
    "bug_type": string,
    "bug_location": {{"file": "Program.cs", "start_line": int, "end_line": int, "symbol": string}} | null,
    "evidence": string | null,
    "knowledge_components": [string],
    "possible_misconception": string | null,
    "reference_diagnosis": string,
    "hint_1": string,
    "hint_2": string,
    "hint_3": string,
    "explanation_vi": string
}}"""


# --- PROPOSED D: Structured Diagnosis + Progressive Hints + Student Context ---
SYSTEM_PROMPT_D = """Bạn là CodeSense AI Tutor với khả năng cá nhân hóa dựa trên Mô hình Người học (Student Model).
Bạn nhận thêm bối cảnh học tập của sinh viên (lịch sử nộp bài, mức độ thuần thục kiến thức Mastery, các quan niệm sai lầm phổ biến từng gặp).
Hãy điều chỉnh lời giải thích và các tầng gợi ý phù hợp với vùng phát triển gần nhất (ZPD) của học viên."""

def build_prompt_d(
    problem_statement: Union[str, ModelInput],
    student_code: Optional[str] = None,
    compiler_error: Optional[str] = None,
    student_context: Optional[Dict[str, Any]] = None
) -> str:
    assert_not_ground_truth(problem_statement)
    if isinstance(problem_statement, ModelInput):
        mi = problem_statement
        problem_statement = mi.problem_statement
        student_code = mi.student_code
        compiler_error = mi.compiler_error
    else:
        assert_not_ground_truth(student_code)
        assert_not_ground_truth(compiler_error)

    if student_context is not None:
        assert_not_ground_truth(student_context)

    err_text = f"\nThông báo lỗi biên dịch: {compiler_error}" if compiler_error else ""
    ctx_text = ""
    if student_context:
        ctx_text = f"\nBối cảnh người học:\n- Lịch sử thử: {student_context.get('attempt_count', 1)}\n- KCs cần củng cố: {student_context.get('struggling_kcs', [])}\n- Quan niệm sai lầm gần đây: {student_context.get('recent_misconceptions', [])}\n"

    return f"""Đề bài:
{problem_statement}

Mã nguồn học sinh:{err_text}{ctx_text}
```csharp
{student_code}
```

Hãy chẩn đoán sư phạm cá nhân hóa và trả về kết quả JSON với các trường:
{{
    "bug_status": "has_bug" | "no_bug" | "insufficient_context",
    "error_category": string,
    "bug_type": string,
    "bug_location": {{"file": "Program.cs", "start_line": int, "end_line": int, "symbol": string}} | null,
    "evidence": string | null,
    "knowledge_components": [string],
    "possible_misconception": string | null,
    "reference_diagnosis": string,
    "hint_1": string,
    "hint_2": string,
    "hint_3": string,
    "explanation_vi": string
}}"""
