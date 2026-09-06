"""
Unit test kiểm định Evaluation Runner và Manifests (APT-028).
"""

import json
from pathlib import Path
import pytest
from app.evaluation.runner import EvaluationRunner
from app.evaluation.schemas import GroundTruth, GROUND_TRUTH_SENTINEL_71F2
from app.tutor.provider import DeterministicMockTutorProvider, TutorLLMProvider


def test_evaluation_runner_system_validation():
    with pytest.raises(ValueError, match="Hệ thống không hợp lệ"):
        EvaluationRunner(system="X", split="dev")

    with pytest.raises(ValueError, match="Split không hợp lệ"):
        EvaluationRunner(system="A", split="unknown_split")


def test_evaluation_runner_manifest_no_secrets(tmp_path):
    mock_provider = DeterministicMockTutorProvider()
    runner = EvaluationRunner(
        system="C",
        split="validation",
        output_dir=tmp_path,
        seed=42,
        mock=True,
        provider_client=mock_provider,
    )
    result = runner.run()

    manifest_file = Path(result["manifest_path"])
    predictions_file = Path(result["predictions_path"])

    assert manifest_file.exists()
    assert predictions_file.exists()

    with open(manifest_file, "r", encoding="utf-8") as f:
        manifest_text = f.read()
        manifest = json.loads(manifest_text)

    # 1. Kiểm tra không có bất kỳ secret/API key nào trong manifest
    for forbidden_token in ["AIza", "sk-", "secret", "password", "PRIVATE_KEY"]:
        assert forbidden_token not in manifest_text, f"Phát hiện rò rỉ secret trong manifest: {forbidden_token}"

    # 2. Kiểm tra các trường bắt buộc của manifest
    assert manifest["system"] == "C"
    assert manifest["split"] == "validation"
    assert manifest["prompt_version"] == "v1.0-structured-progressive"
    assert "dataset_hash" in manifest
    assert "split_hash" in manifest
    assert "git_commit" in manifest
    assert manifest["total_samples"] == 120


def test_evaluation_runner_determinism(tmp_path):
    dir1 = tmp_path / "run1"
    dir2 = tmp_path / "run2"

    mock_provider1 = DeterministicMockTutorProvider()
    mock_provider2 = DeterministicMockTutorProvider()

    runner1 = EvaluationRunner(system="A", split="validation", output_dir=dir1, seed=123, mock=True, provider_client=mock_provider1)
    res1 = runner1.run()

    runner2 = EvaluationRunner(system="A", split="validation", output_dir=dir2, seed=123, mock=True, provider_client=mock_provider2)
    res2 = runner2.run()

    with open(res1["predictions_path"], "r", encoding="utf-8") as f1, open(res2["predictions_path"], "r", encoding="utf-8") as f2:
        preds1 = [json.loads(line) for line in f1]
        preds2 = [json.loads(line) for line in f2]

    assert len(preds1) == len(preds2) == 120
    for p1, p2 in zip(preds1, preds2):
        assert p1["id"] == p2["id"]
        assert p1["bug_status"] == p2["bug_status"]
        assert p1["error_category"] == p2["error_category"]


def test_research_prediction_cannot_be_constructed_from_ground_truth(tmp_path):
    """
    APT-053 Regression Test:
    Kiểm tra chắc chắn rằng prediction nghiên cứu KHÔNG THỂ được xây dựng từ nhãn vàng (Ground Truth):
    1. Proposed C và Proposed D ném ngoại lệ RuntimeError nếu không có provider.
    2. Toàn bộ các trường prediction (bug_status, error_category, bug_type, v.v.)
       đều xuất phát từ provider output, không sao chép nhãn vàng của sample.
    3. Nhãn vàng bị đầu độc (poisoned ground truth) không bao giờ lọt vào prediction.
    4. Input kiểu GroundTruth bị từ chối với TypeError.
    """
    test_sample = {
        "id": "vct-gold-copy-check",
        "language": "csharp",
        "topic": "class_object",
        "difficulty": "beginner",
        "problem_statement_vi": "Khai báo lớp và phương thức.",
        "student_code": "class Item { void Run() { } }",
        "compiler_error": None,
        "bug_status": "has_bug",
        "error_category": "conceptual_misuse",
        "bug_type": "POISON_GOLD_BUG_TYPE_99AA",
        "bug_location": {"file": "Program.cs", "start_line": 1, "end_line": 1, "symbol": "POISON_SYMBOL"},
        "knowledge_components": ["OOP.POISON_KC_GOLD"],
        "possible_misconception": "POISON_MISCONCEPTION_GOLD",
        "reference_diagnosis": "POISON_REF_DIAGNOSIS",
        "evidence": "POISON_EVIDENCE",
        "hint_1": "POISON_HINT_1",
        "hint_2": "POISON_HINT_2",
        "hint_3": "POISON_HINT_3",
        "reference_solution": "POISON_SOLUTION",
        "explanation_vi": "POISON_EXPLANATION",
    }

    # 1. Proposed C và Proposed D bắt buộc phải có provider
    runner_c_no_provider = EvaluationRunner(system="C", split="validation", output_dir=tmp_path, provider_client=None)
    with pytest.raises(RuntimeError, match="cannot produce prediction without a configured LLM provider"):
        runner_c_no_provider._predict_single(test_sample)

    runner_d_no_provider = EvaluationRunner(system="D", split="validation", output_dir=tmp_path, provider_client=None)
    with pytest.raises(RuntimeError, match="cannot produce prediction without a configured LLM provider"):
        runner_d_no_provider._predict_single(test_sample)

    # 2. Tạo một test provider trả về giá trị HOÀN TOÀN KHÁC BIỆT với nhãn vàng của sample
    provider_canned_payload = {
        "bug_status": "no_bug",
        "error_category": "no_bug",
        "bug_type": None,
        "bug_location": None,
        "evidence": None,
        "knowledge_components": ["CleanRoom.Verified"],
        "possible_misconception": None,
        "reference_diagnosis": "Hệ thống xác nhận mã sạch lỗi",
        "hint_1": "Không có lỗi nào cần sửa",
        "hint_2": "",
        "hint_3": "",
        "explanation_vi": "Mã nguồn học sinh đã chính xác",
    }

    class IndependentMockProvider(TutorLLMProvider):
        async def generate_response(self, messages, *, temperature=0.2, max_tokens=1500) -> str:
            return json.dumps(provider_canned_payload)

    runner_with_provider = EvaluationRunner(
        system="C",
        split="validation",
        output_dir=tmp_path,
        provider_client=IndependentMockProvider()
    )

    pred = runner_with_provider._predict_single(test_sample)

    # 3. Xác minh prediction khớp 100% với Provider Output và KHÔNG khớp Ground Truth
    assert pred["bug_status"] == "no_bug"
    assert pred["bug_status"] != test_sample["bug_status"]

    assert pred["error_category"] == "no_bug"
    assert pred["error_category"] != test_sample["error_category"]

    assert pred["bug_type"] is None
    assert pred["bug_type"] != test_sample["bug_type"]

    assert pred["evidence"] is None
    assert pred["evidence"] != test_sample["evidence"]

    assert pred["knowledge_components"] == ["CleanRoom.Verified"]
    assert "OOP.POISON_KC_GOLD" not in pred["knowledge_components"]

    assert pred["possible_misconception"] is None
    assert pred["possible_misconception"] != test_sample["possible_misconception"]

    # 4. Kiểm tra các giá trị độc hại (POISON) tuyệt đối không lọt vào prediction
    for poison_val in [
        "POISON_GOLD_BUG_TYPE_99AA",
        "POISON_SYMBOL",
        "OOP.POISON_KC_GOLD",
        "POISON_MISCONCEPTION_GOLD",
        "POISON_REF_DIAGNOSIS",
        "POISON_EVIDENCE",
        "POISON_HINT_1",
        "POISON_HINT_2",
        "POISON_HINT_3",
        "POISON_SOLUTION",
        "POISON_EXPLANATION",
    ]:
        pred_serialized = json.dumps(pred, ensure_ascii=False)
        assert poison_val not in pred_serialized, f"Rò rỉ nhãn vàng độc hại vào prediction: {poison_val}"

    # 5. Xác minh từ chối GroundTruth instance trực tiếp
    gt_obj = GroundTruth(
        sample_id="vct-gt",
        bug_status="has_bug",
        error_category="logic_error",
        bug_type="syntax_error",
        evidence="code",
        knowledge_components=["OOP.Classes"],
        reference_solution="solution",
        reference_diagnosis="diagnosis",
    )
    with pytest.raises(TypeError, match="EvaluationRunner cannot accept GroundTruth"):
        runner_with_provider._predict_single(gt_obj)
