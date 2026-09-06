"""
Unit test kiểm định các chỉ số đánh giá sư phạm Tutoring Metrics Suite (APT-029).
Bao gồm bài toán tính tay (hand-computed examples) để kiểm chứng tính xác định và độ chính xác toán học.
"""

import pytest
from app.evaluation.metrics import (
    TutoringMetricsSuite,
    compute_sample_kc_f1,
    check_localization,
    check_misconception_match,
    check_solution_leakage,
    check_hint_policy,
)


def test_hand_computed_kc_f1():
    # Trường hợp 1: Trùng khớp 100%
    p, r, f1 = compute_sample_kc_f1(["OOP.Classes", "OOP.Methods"], ["OOP.Classes", "OOP.Methods"])
    assert p == 1.0 and r == 1.0 and f1 == 1.0

    # Trường hợp 2: Dự đoán thừa 1 (Precision = 1/2 = 0.5, Recall = 1/1 = 1.0, F1 = 2*0.5*1 / 1.5 = 2/3 = 0.6667)
    p, r, f1 = compute_sample_kc_f1(["OOP.Classes", "OOP.Extra"], ["OOP.Classes"])
    assert p == 0.5 and r == 1.0
    assert abs(f1 - (2 / 3)) < 1e-4

    # Trường hợp 3: Rỗng cả hai
    p, r, f1 = compute_sample_kc_f1([], [])
    assert f1 == 1.0

    # Trường hợp 4: Không có giao tập
    p, r, f1 = compute_sample_kc_f1(["OOP.A"], ["OOP.B"])
    assert f1 == 0.0


def test_hand_computed_metrics_suite():
    """Kiểm chứng toàn bộ 11 chỉ số bằng ví dụ 4 mẫu tính tay độc lập."""
    gt_dataset = [
        # Mẫu 1: Buggy, chuẩn bị mọi trường đúng
        {
            "id": "sample-01",
            "topic": "class_object",
            "bug_status": "has_bug",
            "error_category": "compile_error",
            "bug_type": "uninstantiated_object",
            "bug_location": {"file": "Program.cs", "start_line": 2, "end_line": 2, "symbol": "item.Run"},
            "knowledge_components": ["OOP.Classes", "OOP.Instantiation"],
            "possible_misconception": "Quên dùng từ khóa new khi khai báo",
            "student_code": "class Program { void Main() { Item item; item.Run(); } }",
            "reference_solution": "Item item = new Item();\nitem.Run();"
        },
        # Mẫu 2: Buggy, dự đoán sai loại lỗi, sai vị trí, rò rỉ giải pháp ở hint_1
        {
            "id": "sample-02",
            "topic": "constructor_this",
            "bug_status": "has_bug",
            "error_category": "logic_error",
            "bug_type": "variable_shadowing",
            "bug_location": {"file": "Program.cs", "start_line": 5, "end_line": 5, "symbol": "x = x"},
            "knowledge_components": ["OOP.Constructors", "OOP.ThisKeyword"],
            "possible_misconception": "Không dùng this để định danh trường",
            "student_code": "int x; public void SetX(int x) { x = x; }",
            "reference_solution": "this.x = x;\nConsole.WriteLine(this.x);"
        },
        # Mẫu 3: No-bug control, nhưng mô hình đoán has_bug (False Positive)
        {
            "id": "sample-03",
            "topic": "correct_code",
            "bug_status": "no_bug",
            "error_category": "no_bug",
            "bug_type": "no_bug",
            "bug_location": None,
            "knowledge_components": ["OOP.Classes"],
            "possible_misconception": None,
            "student_code": "class Item { public void Run() {} }",
            "reference_solution": "class Item { public void Run() {} }"
        },
        # Mẫu 4: Insufficient context control, mô hình đoán đúng
        {
            "id": "sample-04",
            "topic": "insufficient_context",
            "bug_status": "insufficient_context",
            "error_category": "insufficient_context",
            "bug_type": "insufficient_context",
            "bug_location": None,
            "knowledge_components": ["OOP.Context"],
            "possible_misconception": None,
            "student_code": "item.Run();",
            "reference_solution": "class Program { Item item = new Item(); void Test() { item.Run(); } }"
        }
    ]

    predictions = [
        # Dự đoán 1: Đúng hoàn toàn
        {
            "id": "sample-01",
            "bug_status": "has_bug",
            "error_category": "compile_error",
            "bug_type": "uninstantiated_object",
            "bug_location": {"file": "Program.cs", "start_line": 2, "end_line": 2, "symbol": "item.Run"},
            "knowledge_components": ["OOP.Classes", "OOP.Instantiation"],
            "possible_misconception": "Người học quên dùng new khi khởi tạo",
            "evidence": "item.Run();",
            "hint_1": "Hãy kiểm tra việc khởi tạo đối tượng.",
            "hint_2": "Cần toán tử new để cấp phát vùng nhớ trong heap.",
            "hint_3": "Thêm new Item() trước khi gọi phương thức.",
            "json_valid": True,
            "latency_ms": 200.0,
            "prompt_tokens": 500,
            "completion_tokens": 300
        },
        # Dự đoán 2: Sai loại lỗi, rò rỉ giải pháp ở hint_1
        {
            "id": "sample-02",
            "bug_status": "has_bug",
            "error_category": "compile_error",  # Sai (GT: logic_error)
            "bug_type": "wrong_assignment_syntax",  # Sai (GT: variable_shadowing)
            "bug_location": {"file": "Program.cs", "start_line": 20, "end_line": 20, "symbol": "other"},  # Sai
            "knowledge_components": ["OOP.Constructors", "OOP.Wrong"],  # F1 = 0.5
            "possible_misconception": "Không liên quan",  # Sai
            "evidence": "x = x;",
            "hint_1": "Sửa lại như sau: this.x = x;\nConsole.WriteLine(this.x);",  # LEAKAGE!
            "hint_2": "Giải thích thêm.",
            "hint_3": "Hoàn thành.",
            "json_valid": True,
            "latency_ms": 300.0,
            "prompt_tokens": 400,
            "completion_tokens": 200
        },
        # Dự đoán 3: False Positive cho no-bug
        {
            "id": "sample-03",
            "bug_status": "has_bug",  # FALSE POSITIVE
            "error_category": "compile_error",
            "bug_type": "hallucinated_bug",
            "knowledge_components": ["OOP.Classes"],
            "json_valid": True,
            "latency_ms": 150.0,
            "prompt_tokens": 300,
            "completion_tokens": 150
        },
        # Dự đoán 4: Nhận diện đúng insufficient context
        {
            "id": "sample-04",
            "bug_status": "insufficient_context",
            "error_category": "insufficient_context",
            "bug_type": "insufficient_context",
            "knowledge_components": ["OOP.Context"],
            "json_valid": True,
            "latency_ms": 250.0,
            "prompt_tokens": 350,
            "completion_tokens": 180
        }
    ]

    suite = TutoringMetricsSuite()
    result = suite.evaluate(predictions, gt_dataset)
    overall = result["overall"]

    # 1. Diagnosis Accuracy: Mẫu 1 (Đúng), Mẫu 2 (Sai), Mẫu 3 (Sai), Mẫu 4 (Đúng) = 2/4 = 0.5000
    assert overall["diagnosis_accuracy"] == 0.5000

    # 2. Bug Localization Accuracy: Mẫu 1 (Đúng), Mẫu 2 (Sai) trên 2 mẫu buggy = 1/2 = 0.5000
    assert overall["bug_localization_accuracy"] == 0.5000

    # 3. Error Category Accuracy: Mẫu 1 (Đúng), Mẫu 2 (Sai), Mẫu 3 (Sai), Mẫu 4 (Đúng) = 2/4 = 0.5000
    assert overall["error_category_accuracy"] == 0.5000

    # 4. Knowledge Component F1: (1.0 + 0.5 + 1.0 + 1.0) / 4 = 3.5 / 4 = 0.8750
    assert overall["knowledge_component_f1"] == 0.8750

    # 5. Misconception Accuracy: Mẫu 1 (Đúng), Mẫu 2 (Sai) trên 2 mẫu có gt = 1/2 = 0.5000
    assert overall["misconception_accuracy"] == 0.5000

    # 6. No-Bug False Positive Rate: 1 FP trên 1 no-bug sample = 1/1 = 1.0000
    assert overall["no_bug_false_positive_rate"] == 1.0000

    # 7. Insufficient-Context Accuracy: 1 đúng trên 1 mẫu = 1/1 = 1.0000
    assert overall["insufficient_context_accuracy"] == 1.0000

    # 8. Evidence Faithfulness: Cả 2 mẫu buggy đều trích xuất substring có trong student_code = 2/2 = 1.0000
    assert overall["evidence_faithfulness"] == 1.0000

    # 9. Solution Leakage Rate: Mẫu 2 rò rỉ mã trên 2 mẫu buggy = 1/2 = 0.5000
    assert overall["solution_leakage_rate"] == 0.5000

    # 10. JSON Valid Rate: 4/4 = 1.0000
    assert overall["json_valid_rate"] == 1.0000

    # 11. Hint Policy Compliance: Cả 2 mẫu đều có đủ 3 hint không rỗng = 2/2 = 1.0000
    assert overall["hint_policy_compliance"] == 1.0000

    # Kiểm tra resources
    res = result["resources"]
    assert res["prompt_tokens_total"] == 500 + 400 + 300 + 350  # 1550
    assert res["completion_tokens_total"] == 300 + 200 + 150 + 180  # 830
    assert res["total_tokens"] == 1550 + 830  # 2380
    assert res["latency_mean_ms"] == (200.0 + 300.0 + 150.0 + 250.0) / 4  # 225.0
