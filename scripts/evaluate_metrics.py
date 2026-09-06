#!/usr/bin/env python3
"""
CLI Evaluation Metrics Suite cho VietCSharpTutor (APT-029).

Tính toán toàn bộ 11 chỉ số sư phạm và chi phí offline từ saved predictions:
  python scripts/evaluate_metrics.py \
    --predictions runs/<run_id>/predictions.jsonl \
    --dataset data/vietcsharptutor/vietcsharptutor_600.jsonl \
    --output metrics/<run_id>_metrics.json \
    --report metrics/<run_id>_report.md
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "backend"))

from app.evaluation.metrics import TutoringMetricsSuite


def generate_markdown_report(metrics_data: Dict[str, Any], output_path: Path, run_id: str):
    overall = metrics_data.get("overall", {})
    per_topic = metrics_data.get("per_topic", {})
    resources = metrics_data.get("resources", {})
    n_samples = metrics_data.get("total_samples", 0)

    lines = [
        f"# Báo Cáo Đánh Giá Sư Phạm: {run_id}",
        "",
        f"- **Tổng số mẫu đánh giá:** `{n_samples}`",
        f"- **Thời gian phản hồi trung bình:** `{resources.get('latency_mean_ms', 0)} ms` (P50: `{resources.get('latency_p50_ms', 0)} ms`, P95: `{resources.get('latency_p95_ms', 0)} ms`)",
        f"- **Tổng Tokens tiêu thụ:** `{resources.get('total_tokens', 0)}` (Prompt: `{resources.get('prompt_tokens_total', 0)}`, Completion: `{resources.get('completion_tokens_total', 0)}`)",
        f"- **Ước tính chi phí:** `${resources.get('estimated_cost_usd', 0.0)} USD`",
        "",
        "---",
        "",
        "## 1. Các Chỉ Số Sư Phạm Cốt Lõi (Overall Metrics)",
        "| Chỉ Số Đánh Giá | Giá Trị Đạt Được | Ý Nghĩa Sư Phạm |",
        "| :--- | :--- | :--- |",
        f"| **Diagnosis Accuracy** | `{overall.get('diagnosis_accuracy', 0.0) * 100:.2f}%` | Độ chính xác nhận diện đúng lỗi |",
        f"| **Bug Localization Accuracy** | `{overall.get('bug_localization_accuracy', 0.0) * 100:.2f}%` | Định vị chính xác dòng và symbol lỗi |",
        f"| **Error Category Accuracy** | `{overall.get('error_category_accuracy', 0.0) * 100:.2f}%` | Phân loại đúng nhóm lỗi kỹ thuật |",
        f"| **Knowledge Component F1** | `{overall.get('knowledge_component_f1', 0.0):.4f}` | F1 gắn thẻ kiến thức thành phần (KCs) |",
        f"| **Misconception Accuracy** | `{overall.get('misconception_accuracy', 0.0) * 100:.2f}%` | Suy luận đúng quan niệm sai lầm của người học |",
        f"| **No-Bug False Positive Rate** | `{overall.get('no_bug_false_positive_rate', 0.0) * 100:.2f}%` | Tỷ lệ báo lỗi oan trên code đúng (càng thấp càng tốt) |",
        f"| **Insufficient-Context Accuracy** | `{overall.get('insufficient_context_accuracy', 0.0) * 100:.2f}%` | Khả năng phát hiện code bị khuyết ngữ cảnh |",
        f"| **Evidence Faithfulness** | `{overall.get('evidence_faithfulness', 0.0) * 100:.2f}%` | Bằng chứng trích xuất nguyên văn từ bài làm |",
        f"| **Solution Leakage Rate** | `{overall.get('solution_leakage_rate', 0.0) * 100:.2f}%` | Tỷ lệ lộ code giải pháp ở Hint 1 & 2 (càng thấp càng tốt) |",
        f"| **JSON Valid Rate** | `{overall.get('json_valid_rate', 0.0) * 100:.2f}%` | Tỷ lệ tuân thủ định dạng dữ liệu có cấu trúc |",
        f"| **Hint Policy Compliance** | `{overall.get('hint_policy_compliance', 0.0) * 100:.2f}%` | Tuân thủ 3 bậc thang gợi ý sư phạm |",
        "",
        "---",
        "",
        "## 2. Chi Tiết Theo Từng Chủ Đề OOP (Per-Topic Breakdown)",
        "| Chủ Đề (`topic`) | Diag Acc | Loc Acc | Error Cat | KC F1 | Leakage | Policy |",
        "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |"
    ]

    for topic, stats in sorted(per_topic.items()):
        diag = f"{stats.get('diagnosis_accuracy', 0.0) * 100:.1f}%"
        loc = f"{stats.get('bug_localization_accuracy', 0.0) * 100:.1f}%"
        cat = f"{stats.get('error_category_accuracy', 0.0) * 100:.1f}%"
        kc = f"{stats.get('knowledge_component_f1', 0.0):.3f}"
        leak = f"{stats.get('solution_leakage_rate', 0.0) * 100:.1f}%"
        pol = f"{stats.get('hint_policy_compliance', 0.0) * 100:.1f}%"
        lines.append(f"| `{topic}` | {diag} | {loc} | {cat} | {kc} | {leak} | {pol} |")

    lines.append("")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Đã xuất báo cáo Markdown tại: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="VietCSharpTutor Metrics Evaluator CLI (APT-029)")
    parser.add_argument("--predictions", type=str, required=True, help="Đường dẫn file predictions.jsonl")
    parser.add_argument("--dataset", type=str, default=None, help="Đường dẫn file dataset ground truth")
    parser.add_argument("--output", type=str, default=None, help="Đường dẫn file xuất metrics JSON")
    parser.add_argument("--report", type=str, default=None, help="Đường dẫn file xuất báo cáo Markdown")
    args = parser.parse_args()

    pred_path = Path(args.predictions)
    if not pred_path.exists():
        print(f"LỖI: Không tìm thấy file predictions: {pred_path}")
        sys.exit(1)

    ds_path = Path(args.dataset) if args.dataset else (ROOT_DIR / "data" / "vietcsharptutor" / "vietcsharptutor_600.jsonl")
    if not ds_path.exists():
        print(f"LỖI: Không tìm thấy file ground truth: {ds_path}")
        sys.exit(1)

    # Đọc predictions
    predictions: List[Dict[str, Any]] = []
    with open(pred_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                predictions.append(json.loads(line))

    # Đọc ground truth
    ground_truth: List[Dict[str, Any]] = []
    with open(ds_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                ground_truth.append(json.loads(line))

    print(f"Đang tính toán 11 chỉ số sư phạm cho {len(predictions)} dự đoán từ {pred_path}...")
    suite = TutoringMetricsSuite()
    metrics_result = suite.evaluate(predictions, ground_truth)

    # Xuất JSON
    out_path = Path(args.output) if args.output else (ROOT_DIR / "metrics" / f"{pred_path.parent.name}_metrics.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(metrics_result, f, ensure_ascii=False, indent=2)
    print(f"Đã xuất file metrics JSON tại: {out_path}")

    # Xuất Báo cáo Markdown nếu được yêu cầu
    if args.report:
        report_path = Path(args.report)
        generate_markdown_report(metrics_result, report_path, run_id=pred_path.parent.name)

    # In tóm tắt ra console
    overall = metrics_result.get("overall", {})
    print("\n--- TÓM TẮT KẾT QUẢ SƯ PHẠM CHÍNH ---")
    print(f"- Diagnosis Accuracy:           {overall.get('diagnosis_accuracy', 0.0) * 100:.2f}%")
    print(f"- Bug Localization Accuracy:    {overall.get('bug_localization_accuracy', 0.0) * 100:.2f}%")
    print(f"- Error Category Accuracy:      {overall.get('error_category_accuracy', 0.0) * 100:.2f}%")
    print(f"- Knowledge Component F1:       {overall.get('knowledge_component_f1', 0.0):.4f}")
    print(f"- Solution Leakage Rate:        {overall.get('solution_leakage_rate', 0.0) * 100:.2f}%")
    print(f"- Hint Policy Compliance:       {overall.get('hint_policy_compliance', 0.0) * 100:.2f}%")


if __name__ == "__main__":
    main()
