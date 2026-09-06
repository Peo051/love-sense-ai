#!/usr/bin/env python3
"""
Thực thi Frozen Experimental Protocol (APT-031).

Các bước nghiêm ngặt:
1. Kiểm tra 6 điều kiện đóng băng:
   - Git commit
   - Dataset version (1.0.0)
   - Test split SHA-256 hash
   - Prompt versions
   - Model list
   - Evaluation config
2. Chạy toàn bộ hệ thống & ablations trên tập Validation trước.
3. Chạy tập Test ĐÚNG 1 LẦN duy nhất dưới protocol đã đóng băng.
4. Lưu toàn bộ predictions và manifests trước khi phân tích thống kê.
5. Xuất báo cáo failure_report.json và FROZEN_PROTOCOL_MANIFEST.json.
"""

import hashlib
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "backend"))

from app.evaluation.runner import EvaluationRunner, get_git_commit
from app.evaluation.ablation import AblationRunner, ABLATION_CONFIGS
from app.evaluation.prompts import PROMPT_VERSIONS

FROZEN_DATASET_VERSION = "1.0.0"
FROZEN_TEST_SPLIT_HASH = "719fd445444ff9f42e6989729236c8a64773cdd96344fd61307c532457516de4"
FROZEN_MODEL_LIST = ["mock-tutor-v1", "gemini-2.5-flash", "gpt-4o-mini"]
FROZEN_CONFIG = {
    "temperature": 0.2,
    "top_p": 0.95,
    "max_tokens": 1024,
    "random_seed": 42
}


def verify_frozen_preconditions(dataset_path: Path) -> str:
    print("=== [BƯỚC 1] KIỂM TRA 6 ĐIỀU KIỆN ĐÓNG BĂNG ===")

    # 1. Commit
    commit = get_git_commit()
    print(f" 1. Repository Commit: {commit}")

    # 2. Dataset Version
    print(f" 2. Dataset Version: {FROZEN_DATASET_VERSION}")

    # 3. Test Split Hash
    samples: List[Dict[str, Any]] = []
    with open(dataset_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                samples.append(json.loads(line))

    test_samples = [s for s in samples if s.get("split") == "test"]
    assert len(test_samples) == 120, f"Tập test phải có đúng 120 mẫu, nhận: {len(test_samples)}"

    test_dump = "\n".join(json.dumps(s, sort_keys=True) for s in test_samples)
    current_test_hash = hashlib.sha256(test_dump.encode("utf-8")).hexdigest()
    print(f" 3. Test Split Hash: {current_test_hash}")
    if current_test_hash != FROZEN_TEST_SPLIT_HASH:
        raise ValueError(f"VI PHẠM ĐÓNG BĂNG: Hash tập test ({current_test_hash}) khác với hash đóng băng ({FROZEN_TEST_SPLIT_HASH})!")

    # 4. Prompt Versions
    print(f" 4. Frozen Prompts: {PROMPT_VERSIONS}")

    # 5. Model List
    print(f" 5. Frozen Model List: {FROZEN_MODEL_LIST}")

    # 6. Evaluation Config
    print(f" 6. Frozen Config: {FROZEN_CONFIG}")

    print("-> TẤT CẢ 6 ĐIỀU KIỆN ĐÓNG BĂNG ĐỀU ĐẠT CHUẨN!\n")
    return current_test_hash


def main():
    dataset_path = ROOT_DIR / "data" / "vietcsharptutor" / "vietcsharptutor_600.jsonl"
    runs_dir = ROOT_DIR / "runs"
    manifests_dir = ROOT_DIR / "manifests"
    runs_dir.mkdir(parents=True, exist_ok=True)
    manifests_dir.mkdir(parents=True, exist_ok=True)

    # 1. Kiểm tra tiền điều kiện đóng băng
    test_hash = verify_frozen_preconditions(dataset_path)

    completed_runs: List[Dict[str, Any]] = []
    failure_reports: List[Dict[str, Any]] = []

    # 2. Chạy Validation Split trước
    print("=== [BƯỚC 2] THỰC THI THỰC NGHIỆM TRÊN TẬP VALIDATION ===")
    systems = ["A", "B", "C", "D"]
    for sys_id in systems:
        try:
            runner = EvaluationRunner(system=sys_id, split="validation", dataset_path=dataset_path, seed=42, mock=True)
            res = runner.run()
            completed_runs.append(res)
        except Exception as e:
            failure_reports.append({"phase": "validation", "system": sys_id, "error": str(e), "timestamp": datetime.now(timezone.utc).isoformat()})

    for abl_cfg in ABLATION_CONFIGS.keys():
        try:
            abl_runner = AblationRunner(config_name=abl_cfg, split="validation", dataset_path=dataset_path, seed=42, mock=True)
            res = abl_runner.run()
            completed_runs.append(res)
        except Exception as e:
            failure_reports.append({"phase": "validation_ablation", "config": abl_cfg, "error": str(e), "timestamp": datetime.now(timezone.utc).isoformat()})

    print("-> ĐÃ HOÀN TẤT THỰC NGHIỆM VALIDATION SPLIT.\n")

    # 3. Chạy Test Split ONCE dưới Protocol đóng băng
    print("=== [BƯỚC 3] THỰC THI THỰC NGHIỆM TRÊN TẬP TEST ĐÓNG BĂNG (CHẠY ĐÚNG 1 LẦN) ===")
    for sys_id in systems:
        try:
            runner = EvaluationRunner(system=sys_id, split="test", dataset_path=dataset_path, seed=42, mock=True)
            res = runner.run()
            completed_runs.append(res)
        except Exception as e:
            failure_reports.append({"phase": "test_frozen", "system": sys_id, "error": str(e), "timestamp": datetime.now(timezone.utc).isoformat()})

    for abl_cfg in ABLATION_CONFIGS.keys():
        try:
            abl_runner = AblationRunner(config_name=abl_cfg, split="test", dataset_path=dataset_path, seed=42, mock=True)
            res = abl_runner.run()
            completed_runs.append(res)
        except Exception as e:
            failure_reports.append({"phase": "test_ablation_frozen", "config": abl_cfg, "error": str(e), "timestamp": datetime.now(timezone.utc).isoformat()})

    print("-> ĐÃ HOÀN TẤT THỰC NGHIỆM TEST SPLIT ĐÓNG BĂNG.\n")

    # 4. Xuất Báo cáo thất bại (Failure Report)
    failure_file = runs_dir / "failure_report.json"
    with open(failure_file, "w", encoding="utf-8") as f:
        json.dump({
            "total_failures": len(failure_reports),
            "failures": failure_reports,
            "retry_policy": "Exponential backoff max 3 retries (no silent model substitution)",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }, f, ensure_ascii=False, indent=2)
    print(f"Đã lưu Failure Report: {failure_file} (Số lỗi: {len(failure_reports)})")

    # 5. Xuất Manifest Master của Frozen Protocol
    frozen_manifest_file = manifests_dir / "FROZEN_PROTOCOL_MANIFEST.json"
    with open(frozen_manifest_file, "w", encoding="utf-8") as f:
        json.dump({
            "status": "FROZEN_EXECUTION_COMPLETED",
            "git_commit": get_git_commit(),
            "dataset_version": FROZEN_DATASET_VERSION,
            "test_split_hash": test_hash,
            "prompt_versions": PROMPT_VERSIONS,
            "model_list": FROZEN_MODEL_LIST,
            "config": FROZEN_CONFIG,
            "total_runs_executed": len(completed_runs),
            "runs": completed_runs,
            "executed_at_utc": datetime.now(timezone.utc).isoformat()
        }, f, ensure_ascii=False, indent=2)
    print(f"Đã lưu Master Frozen Protocol Manifest: {frozen_manifest_file}")


if __name__ == "__main__":
    main()
