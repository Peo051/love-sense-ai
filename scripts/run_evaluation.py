#!/usr/bin/env python3
"""
CLI Runner cho VietCSharpTutor Evaluation (APT-028).

Ví dụ sử dụng:
  python scripts/run_evaluation.py --system A --split dev
  python scripts/run_evaluation.py --system C --split validation --mock
  python scripts/run_evaluation.py --system D --split test --seed 123
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

from app.evaluation.runner import EvaluationRunner


def main():
    parser = argparse.ArgumentParser(description="VietCSharpTutor Evaluation Runner CLI (APT-028)")
    parser.add_argument("--system", type=str, required=True, choices=["A", "B", "C", "D"], help="Hệ thống cần đánh giá: A, B, C, hoặc D")
    parser.add_argument("--split", type=str, default="dev", choices=["dev", "validation", "test"], help="Phân vùng dữ liệu: dev, validation, test")
    parser.add_argument("--model", type=str, default="mock-tutor-v1", help="Tên mô hình LLM")
    parser.add_argument("--provider", type=str, default="mock", help="Nhà cung cấp (mock, gemini, etc.)")
    parser.add_argument("--dataset", type=str, default=None, help="Đường dẫn file dataset")
    parser.add_argument("--output-dir", type=str, default=None, help="Thư mục xuất kết quả")
    parser.add_argument("--seed", type=int, default=42, help="Seed ngẫu nhiên")
    parser.add_argument("--mock", action="store_true", default=True, help="Chế độ mock deterministic")
    args = parser.parse_args()

    dataset_path = Path(args.dataset) if args.dataset else None
    output_dir = Path(args.output_dir) if args.output_dir else None

    runner = EvaluationRunner(
        system=args.system,
        split=args.split,
        model=args.model,
        provider=args.provider,
        dataset_path=dataset_path,
        output_dir=output_dir,
        seed=args.seed,
        mock=args.mock
    )

    result = runner.run()
    print(f"\n[HOÀN TẤT] Run ID: {result['run_id']}")
    print(f"File dự đoán: {result['predictions_path']}")
    print(f"File manifest: {result['manifest_path']}")


if __name__ == "__main__":
    main()
