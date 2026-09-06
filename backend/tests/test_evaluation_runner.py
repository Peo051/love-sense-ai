"""
Unit test kiểm định Evaluation Runner và Manifests (APT-028).
"""

import json
from pathlib import Path
import pytest
from app.evaluation.runner import EvaluationRunner


def test_evaluation_runner_system_validation():
    with pytest.raises(ValueError, match="Hệ thống không hợp lệ"):
        EvaluationRunner(system="X", split="dev")

    with pytest.raises(ValueError, match="Split không hợp lệ"):
        EvaluationRunner(system="A", split="unknown_split")


def test_evaluation_runner_manifest_no_secrets(tmp_path):
    runner = EvaluationRunner(
        system="C",
        split="validation",
        output_dir=tmp_path,
        seed=42,
        mock=True
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

    runner1 = EvaluationRunner(system="A", split="validation", output_dir=dir1, seed=123, mock=True)
    res1 = runner1.run()

    runner2 = EvaluationRunner(system="A", split="validation", output_dir=dir2, seed=123, mock=True)
    res2 = runner2.run()

    with open(res1["predictions_path"], "r", encoding="utf-8") as f1, open(res2["predictions_path"], "r", encoding="utf-8") as f2:
        preds1 = [json.loads(line) for line in f1]
        preds2 = [json.loads(line) for line in f2]

    assert len(preds1) == len(preds2) == 120
    for p1, p2 in zip(preds1, preds2):
        assert p1["id"] == p2["id"]
        assert p1["bug_status"] == p2["bug_status"]
        assert p1["error_category"] == p2["error_category"]
