"""
Unit test kiểm định Dataset Validator (APT-026 & APT-027).
"""

import json
import pytest
from pathlib import Path
import sys

# Thêm root vào sys.path để import validator
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from scripts.validate_vietcsharptutor import DatasetValidator, REQUIRED_FIELDS


@pytest.fixture
def valid_sample():
    return {
        "id": "vct-001",
        "language": "vi",
        "topic": "class_object",
        "difficulty": "beginner",
        "problem_family_id": "fam-student-profile",
        "problem_statement_vi": "Viết chương trình C# khai báo lớp Student và sử dụng đối tượng trong hàm Main.",
        "student_code": "using System;\nclass Program { static void Main() { Student s; s.Study(); } }",
        "compiler_error": "Use of unassigned local variable 's' (CS0165)",
        "expected_behavior": "Khởi tạo đối tượng Student với từ khóa new trước khi gọi phương thức.",
        "bug_status": "has_bug",
        "error_category": "compile_error",
        "bug_type": "uninstantiated_object_reference",
        "bug_location": {"file": "Program.cs", "start_line": 2, "end_line": 2, "symbol": "s.Study"},
        "knowledge_components": ["OOP.Classes", "OOP.Instantiation"],
        "possible_misconception": "Nghĩ rằng khai báo biến tham chiếu thì đối tượng đã được tạo trong bộ nhớ.",
        "reference_diagnosis": "Biến s chưa được khởi tạo với từ khóa new.",
        "evidence": "s.Study();",
        "hint_1": "Hãy kiểm tra xem biến s đã được khởi tạo hay chưa.",
        "hint_2": "Cần sử dụng từ khóa new để tạo đối tượng.",
        "hint_3": "Thêm s = new Student(); trước khi gọi s.Study();",
        "reference_solution": "using System;\nclass Program { static void Main() { Student s = new Student(); s.Study(); } }",
        "explanation_vi": "Biến tham chiếu cần được khởi tạo trước khi gọi phương thức.",
        "source_type": "expert_authored",
        "split": "dev",
        "review_status": "approved"
    }


def test_validator_valid_sample(valid_sample):
    validator = DatasetValidator()
    errors = validator.validate_sample(valid_sample, 0)
    assert len(errors) == 0, f"Mẫu hợp lệ không được có lỗi: {errors}"


def test_validator_missing_required_field(valid_sample):
    validator = DatasetValidator()
    invalid_sample = dict(valid_sample)
    del invalid_sample["evidence"]
    errors = validator.validate_sample(invalid_sample, 0)
    assert any("Thiếu trường bắt buộc: 'evidence'" in err for err in errors)


def test_validator_evidence_grounding_failure(valid_sample):
    validator = DatasetValidator()
    invalid_sample = dict(valid_sample)
    invalid_sample["evidence"] = "Console.WriteLine('This does not exist in code');"
    errors = validator.validate_sample(invalid_sample, 0)
    assert any("Evidence Grounding Failure" in err for err in errors)


def test_validator_no_bug_semantic_constraints(valid_sample):
    validator = DatasetValidator()
    no_bug_sample = dict(valid_sample)
    no_bug_sample["topic"] = "correct_code"
    no_bug_sample["bug_status"] = "no_bug"
    no_bug_sample["error_category"] = "no_bug"
    no_bug_sample["bug_type"] = "no_bug"
    no_bug_sample["bug_location"] = None
    no_bug_sample["evidence"] = None
    no_bug_sample["possible_misconception"] = None

    errors = validator.validate_sample(no_bug_sample, 0)
    assert len(errors) == 0, f"Mẫu no_bug hợp lệ nhưng bị báo lỗi: {errors}"

    # Thử vi phạm ràng buộc no_bug: có evidence
    no_bug_sample["evidence"] = "s.Study();"
    errors = validator.validate_sample(no_bug_sample, 0)
    assert any("evidence phải là null" in err for err in errors)


def test_validator_insufficient_context_constraints(valid_sample):
    validator = DatasetValidator()
    ctx_sample = dict(valid_sample)
    ctx_sample["topic"] = "insufficient_context"
    ctx_sample["bug_status"] = "insufficient_context"
    ctx_sample["error_category"] = "insufficient_context"
    ctx_sample["bug_type"] = "insufficient_context"
    ctx_sample["possible_misconception"] = None

    errors = validator.validate_sample(ctx_sample, 0)
    assert len(errors) == 0, f"Mẫu insufficient_context hợp lệ nhưng bị báo lỗi: {errors}"

    # Thử vi phạm: gán misconception khi thiếu ngữ cảnh
    ctx_sample["possible_misconception"] = "Học sinh hiểu sai về OOP"
    errors = validator.validate_sample(ctx_sample, 0)
    assert any("possible_misconception phải là null" in err for err in errors)


def test_validator_family_leakage_detection(valid_sample):
    validator = DatasetValidator()
    sample1 = dict(valid_sample)
    sample1["id"] = "vct-001"
    sample1["problem_family_id"] = "fam-student-profile"
    sample1["split"] = "dev"

    sample2 = dict(valid_sample)
    sample2["id"] = "vct-002"
    sample2["problem_family_id"] = "fam-student-profile"
    sample2["split"] = "test"  # Cố tình gây rò rỉ họ bài toán sang test

    is_valid, errors, stats = validator.validate_dataset([sample1, sample2])
    assert not is_valid
    assert stats["has_family_leakage"] is True
    assert any("Rò rỉ họ bài toán" in err or "Family Leakage" in err for err in errors)


def test_vietcsharptutor_600_dataset_integrity():
    """Kiểm tra toàn vẹn toàn bộ 600 ca trong file vietcsharptutor_600.jsonl thực tế."""
    dataset_path = ROOT_DIR / "data" / "vietcsharptutor" / "vietcsharptutor_600.jsonl"
    schema_path = ROOT_DIR / "data" / "vietcsharptutor" / "schema.json"

    assert dataset_path.exists(), f"Không tìm thấy file dataset: {dataset_path}"
    assert schema_path.exists(), f"Không tìm thấy schema: {schema_path}"

    validator = DatasetValidator(schema_path=schema_path)
    samples = []
    with open(dataset_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                samples.append(json.loads(line))

    assert len(samples) == 600, f"Dataset phải có đúng 600 ca, nhận: {len(samples)}"

    is_valid, errors, stats = validator.validate_dataset(samples)
    assert is_valid is True, f"Phát hiện {len(errors)} lỗi trong dataset thực tế: {errors[:5]}"
    assert stats["total_samples"] == 600
    assert stats["unique_families"] == 60
    assert stats["has_family_leakage"] is False
    assert stats["split_distribution"]["dev"] == 360
    assert stats["split_distribution"]["validation"] == 120
    assert stats["split_distribution"]["test"] == 120
