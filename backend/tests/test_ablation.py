"""
Unit test kiểm định Ablation Study Engine (APT-030).
"""

import json
from pathlib import Path
import pytest
from app.evaluation.ablation import AblationRunner, ABLATION_CONFIGS
from app.evaluation.metrics import TutoringMetricsSuite


def test_ablation_configs_definitions():
    expected_configs = {"FULL", "NO_STUDENT_MODEL", "NO_PROGRESSIVE_HINT", "NO_STRUCTURED_DIAGNOSIS", "DIRECT_BASELINE"}
    assert set(ABLATION_CONFIGS.keys()) == expected_configs


def test_ablation_invalid_config():
    with pytest.raises(ValueError, match="Cấu hình ablation không hợp lệ"):
        AblationRunner(config_name="INVALID_CFG", split="validation")


def test_ablation_run_and_manifest(tmp_path):
    runner = AblationRunner(
        config_name="FULL",
        split="validation",
        output_dir=tmp_path,
        seed=42,
        mock=True
    )
    res = runner.run()

    pred_file = Path(res["predictions_path"])
    manifest_file = Path(res["manifest_path"])

    assert pred_file.exists()
    assert manifest_file.exists()

    with open(manifest_file, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    assert manifest["ablation_config"] == "FULL"
    assert manifest["split"] == "validation"
    assert manifest["dataset_version"] == "1.0.0"
    assert "split_hash" in manifest
    assert "git_commit" in manifest
    assert manifest["total_samples"] == 120


def test_ablation_leakage_differential(tmp_path):
    """Kiểm tra tính khác biệt: NO_PROGRESSIVE_HINT phải làm tăng tỷ lệ rò rỉ giải pháp so với FULL."""
    dir_full = tmp_path / "full"
    dir_no_hint = tmp_path / "no_hint"

    res_full = AblationRunner("FULL", "validation", output_dir=dir_full, seed=42, mock=True).run()
    res_no_hint = AblationRunner("NO_PROGRESSIVE_HINT", "validation", output_dir=dir_no_hint, seed=42, mock=True).run()

    with open(res_full["predictions_path"], "r", encoding="utf-8") as f:
        preds_full = [json.loads(l) for l in f if l.strip()]

    with open(res_no_hint["predictions_path"], "r", encoding="utf-8") as f:
        preds_no_hint = [json.loads(l) for l in f if l.strip()]

    # Đọc ground truth validation
    root = Path(__file__).resolve().parents[2]
    ds_path = root / "data" / "vietcsharptutor" / "vietcsharptutor_600.jsonl"
    with open(ds_path, "r", encoding="utf-8") as f:
        gt = [json.loads(l) for l in f if l.strip()]

    suite = TutoringMetricsSuite()
    metrics_full = suite.evaluate(preds_full, gt)["overall"]
    metrics_no_hint = suite.evaluate(preds_no_hint, gt)["overall"]

    # FULL phải có leakage = 0.0, trong khi NO_PROGRESSIVE_HINT phải có leakage cao (> 0.5)
    assert metrics_full["solution_leakage_rate"] == 0.0
    assert metrics_no_hint["solution_leakage_rate"] > 0.50
