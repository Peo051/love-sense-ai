"""
Test Fixtures & Synthetic Records for Evaluation Testing (APT-054).

Cung cấp:
- Mẫu dữ liệu synthetic biệt lập hoàn toàn phục vụ kiểm thử đơn vị.
- Hàm khởi tạo ModelInput, GroundTruth và EvaluationRecord sạch.
- Dataset tạm thời không chứa nhãn vàng rò rỉ.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.evaluation.schemas import (
    EvaluationMetadata,
    EvaluationRecord,
    GroundTruth,
    ModelInput,
)


def get_sample_test_record(
    sample_id: str = "test-sample-001",
    has_bug: bool = True,
    split: str = "validation",
) -> Dict[str, Any]:
    """Tạo một bản ghi raw dataset record mẫu cho kiểm thử."""
    if has_bug:
        return {
            "id": sample_id,
            "split": split,
            "language": "csharp",
            "topic": "class_object",
            "difficulty": "beginner",
            "problem_statement_vi": "Viết lớp SinhVien với phương thức InThongTin.",
            "student_code": "public class SinhVien { public string Ten; public void InThongTin() { Console.WriteLine(Ten); } }",
            "compiler_error": None,
            "bug_status": "has_bug",
            "error_category": "logic_error",
            "bug_type": "uninitialized_field",
            "bug_location": {"file": "Program.cs", "start_line": 1, "end_line": 1, "symbol": "Ten"},
            "evidence": "public string Ten;",
            "knowledge_components": ["csharp_classes", "variable_initialization"],
            "possible_misconception": "Không khởi tạo giá trị mặc định cho trường trước khi sử dụng.",
            "reference_diagnosis": "Trường dữ liệu Ten chưa được khởi tạo.",
            "hint_1": "Hãy kiểm tra xem Ten đã có giá trị ban đầu chưa.",
            "hint_2": "Bạn có thể sử dụng constructor để gán giá trị cho Ten.",
            "hint_3": "Thêm constructor: public SinhVien(string ten) { Ten = ten; }",
            "reference_solution": "public class SinhVien { public string Ten; public SinhVien(string ten) { Ten = ten; } public void InThongTin() { Console.WriteLine(Ten); } }",
            "explanation_vi": "Giải thích chi tiết về khởi tạo trường trong C#.",
        }
    else:
        return {
            "id": sample_id,
            "split": split,
            "language": "csharp",
            "topic": "class_object",
            "difficulty": "beginner",
            "problem_statement_vi": "Viết lớp SinhVien với phương thức InThongTin.",
            "student_code": "public class SinhVien { public string Ten = \"Test\"; public void InThongTin() { Console.WriteLine(Ten); } }",
            "compiler_error": None,
            "bug_status": "no_bug",
            "error_category": "no_bug",
            "bug_type": None,
            "bug_location": None,
            "evidence": None,
            "knowledge_components": ["csharp_classes"],
            "possible_misconception": None,
            "reference_diagnosis": "Mã nguồn chính xác.",
            "hint_1": "Mã nguồn của bạn đã chạy đúng yêu cầu.",
            "hint_2": "",
            "hint_3": "",
            "reference_solution": "public class SinhVien { public string Ten = \"Test\"; public void InThongTin() { Console.WriteLine(Ten); } }",
            "explanation_vi": "Không có lỗi.",
        }


def get_clean_test_model_input(
    sample_id: str = "test-sample-001",
    student_code: str = "public class Program { public static void Main() {} }",
    problem_statement: str = "Yêu cầu viết chương trình C# cơ bản.",
    compiler_error: Optional[str] = None,
) -> ModelInput:
    """Tạo đối tượng ModelInput thuần khiết không có nhãn vàng."""
    return ModelInput(
        sample_id=sample_id,
        student_code=student_code,
        problem_statement=problem_statement,
        compiler_error=compiler_error,
    )


def get_clean_test_ground_truth(
    sample_id: str = "test-sample-001",
    bug_status: str = "has_bug",
    error_category: str = "logic_error",
    bug_type: str = "semantic_error",
) -> GroundTruth:
    """Tạo đối tượng GroundTruth độc lập phục vụ kiểm thử offline evaluator."""
    return GroundTruth(
        sample_id=sample_id,
        bug_status=bug_status,
        error_category=error_category,
        bug_type=bug_type,
        bug_location={"file": "Program.cs", "start_line": 1, "end_line": 1},
        knowledge_components=["test_kc"],
        evidence="student_code_snippet",
        hint_1="Test hint 1",
        hint_2="Test hint 2",
        hint_3="Test hint 3",
        reference_solution="Test solution",
    )


def get_test_dataset(size: int = 5, split: str = "validation") -> List[Dict[str, Any]]:
    """Sinh danh sách các mẫu dữ liệu hợp lệ phục vụ kiểm định runner."""
    samples = []
    for i in range(1, size + 1):
        samples.append(get_sample_test_record(sample_id=f"sample_{split}_{i:03d}", split=split))
    return samples


def create_temp_dataset_file(
    tmp_path: Path,
    samples: Optional[List[Dict[str, Any]]] = None,
    filename: str = "test_dataset.jsonl",
) -> Path:
    """Ghi dataset mẫu ra file jsonl tạm."""
    file_path = tmp_path / filename
    if samples is None:
        samples = get_test_dataset(size=5, split="validation")
    with open(file_path, "w", encoding="utf-8") as f:
        for s in samples:
            f.write(json.dumps(s, ensure_ascii=False) + "\n")
    return file_path
