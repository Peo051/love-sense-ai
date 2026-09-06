#!/usr/bin/env python3
"""
Research Evaluation Runner CLI (APT-054).

Sử dụng ResearchRunner độc lập, bắt buộc kết nối thực tế tới LLM (Real Provider).
Tuyệt đối không hỗ trợ cờ --mock hay synthetic canned responses trong CLI nghiên cứu.

Ví dụ sử dụng nghiên cứu thực tế:
  python scripts/run_evaluation.py --system A --split dev --provider openai --model gpt-4o-mini
  python scripts/run_evaluation.py --system C --split validation --provider openai --model gpt-4o-mini
  python scripts/run_evaluation.py --system D --split test --provider openai --model gpt-4o-mini --seed 123
"""

import argparse
import os
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "backend"))

from app.evaluation.research.runner import ResearchRunner


def main():
    parser = argparse.ArgumentParser(description="VietCSharpTutor Research Evaluation Runner CLI (APT-054)")
    parser.add_argument("--system", type=str, required=True, choices=["A", "B", "C", "D"], help="Hệ thống cần đánh giá: A, B, C, hoặc D")
    parser.add_argument("--split", type=str, default="dev", choices=["dev", "validation", "test"], help="Phân vùng dữ liệu: dev, validation, test")
    parser.add_argument("--model", type=str, default="gpt-4o-mini", help="Tên mô hình LLM thực tế")
    parser.add_argument("--provider", type=str, default="openai", choices=["openai", "azure"], help="Nhà cung cấp LLM thực tế (chỉ chấp nhận real provider)")
    parser.add_argument("--dataset", type=str, default=None, help="Đường dẫn file dataset")
    parser.add_argument("--output-dir", type=str, default=None, help="Thư mục xuất kết quả")
    parser.add_argument("--seed", type=int, default=42, help="Seed ngẫu nhiên")
    parser.add_argument("--allow-test-doubles", action="store_true", default=False, help=argparse.SUPPRESS)

    args = parser.parse_args()

    dataset_path = Path(args.dataset) if args.dataset else None
    output_dir = Path(args.output_dir) if args.output_dir else None

    runner = ResearchRunner(
        system=args.system,
        split=args.split,
        model=args.model,
        provider=args.provider,
        dataset_path=dataset_path,
        output_dir=output_dir,
        seed=args.seed,
        allow_test_doubles=args.allow_test_doubles,
    )

    result = runner.run()
    print(f"\n[HOÀN TẤT NGHIÊN CỨU] Run ID: {result['run_id']}")
    print(f"File dự đoán: {result['predictions_path']}")
    print(f"File manifest: {result['manifest_path']}")


if __name__ == "__main__":
    main()
