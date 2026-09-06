#!/usr/bin/env python3
"""
CLI Runner cho Ablation Study (APT-030).

Hỗ trợ 5 cấu hình triệt tiêu:
  FULL, NO_STUDENT_MODEL, NO_PROGRESSIVE_HINT, NO_STRUCTURED_DIAGNOSIS, DIRECT_BASELINE
Ví dụ:
  python scripts/run_ablation.py --ablation FULL --split validation
  python scripts/run_ablation.py --ablation ALL --split validation
"""

import argparse
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "backend"))

from app.evaluation.ablation import AblationRunner, ABLATION_CONFIGS


def main():
    parser = argparse.ArgumentParser(description="VietCSharpTutor Ablation Runner CLI (APT-030)")
    parser.add_argument(
        "--ablation",
        type=str,
        required=True,
        help=f"Cấu hình triệt tiêu ({', '.join(list(ABLATION_CONFIGS.keys()))}, hoặc ALL)"
    )
    parser.add_argument("--split", type=str, default="validation", choices=["dev", "validation", "test"])
    parser.add_argument("--model", type=str, default="mock-tutor-v1")
    parser.add_argument("--provider", type=str, default="mock")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--mock", action="store_true", default=True)
    args = parser.parse_args()

    configs_to_run = list(ABLATION_CONFIGS.keys()) if args.ablation.upper() == "ALL" else [args.ablation.upper()]

    for cfg in configs_to_run:
        runner = AblationRunner(
            config_name=cfg,
            split=args.split,
            model=args.model,
            provider=args.provider,
            seed=args.seed,
            mock=args.mock
        )
        res = runner.run()
        print(f"-> [THÀNH CÔNG] {cfg}: {res['predictions_path']}\n")


if __name__ == "__main__":
    main()
