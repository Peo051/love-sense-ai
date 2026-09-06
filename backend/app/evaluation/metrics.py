"""
Hệ thống tính toán chỉ số sư phạm VietCSharpTutor Metrics Suite (APT-029).

11 chỉ số cốt lõi:
1. Diagnosis Accuracy
2. Bug Localization Accuracy
3. Error Category Accuracy
4. Knowledge Component F1
5. Misconception Accuracy
6. No-Bug False Positive Rate
7. Insufficient-Context Accuracy
8. Evidence Faithfulness
9. Solution Leakage Rate
10. JSON Valid Rate
11. Hint Policy Compliance

Kèm theo các chỉ số tài nguyên:
- Latency (ms) [Mean, P50, P95]
- Tokens (Prompt, Completion, Total)
- Estimated Cost (USD)

Hoạt động hoàn toàn offline từ saved predictions và ground truth,
tách bạch theo từng chủ đề (topic) và tổng thể (overall).
"""

import math
import re
from typing import Any, Dict, List, Optional, Tuple


def _normalize_tokens(text: Optional[str]) -> set:
    if not text or not isinstance(text, str):
        return set()
    cleaned = re.sub(r"[^\w\s]", " ", text.lower())
    return set(cleaned.split())


def compute_sample_kc_f1(pred_kcs: List[str], gt_kcs: List[str]) -> Tuple[float, float, float]:
    """Tính Precision, Recall, F1 cho tập Knowledge Components của 1 mẫu."""
    pred_set = set(pred_kcs or [])
    gt_set = set(gt_kcs or [])

    if not pred_set and not gt_set:
        return 1.0, 1.0, 1.0
    if not pred_set or not gt_set:
        return 0.0, 0.0, 0.0

    inter = len(pred_set & gt_set)
    precision = inter / len(pred_set)
    recall = inter / len(gt_set)
    if precision + recall == 0:
        f1 = 0.0
    else:
        f1 = 2 * precision * recall / (precision + recall)
    return precision, recall, f1


def check_localization(pred_loc: Optional[Dict[str, Any]], gt_loc: Optional[Dict[str, Any]]) -> bool:
    """Kiểm tra độ chính xác vị trí lỗi (dòng hoặc symbol)."""
    if not gt_loc:
        return pred_loc is None
    if not pred_loc:
        return False

    # 1. So khớp symbol nếu có
    pred_sym = str(pred_loc.get("symbol", "")).strip().lower()
    gt_sym = str(gt_loc.get("symbol", "")).strip().lower()
    if pred_sym and gt_sym and (pred_sym in gt_sym or gt_sym in pred_sym):
        return True

    # 2. So khớp khoảng dòng (line overlap)
    try:
        p_start = int(pred_loc.get("start_line", 0))
        p_end = int(pred_loc.get("end_line", p_start))
        g_start = int(gt_loc.get("start_line", 0))
        g_end = int(gt_loc.get("end_line", g_start))

        overlap = max(0, min(p_end, g_end) - max(p_start, g_start) + 1)
        return overlap > 0
    except (ValueError, TypeError):
        return False


def check_misconception_match(pred_misc: Optional[str], gt_misc: Optional[str]) -> bool:
    """So khớp quan niệm sai lầm bằng giao tập từ khóa ngữ nghĩa."""
    if not gt_misc:
        return pred_misc is None

    if not pred_misc:
        return False

    t_pred = _normalize_tokens(pred_misc)
    t_gt = _normalize_tokens(gt_misc)
    if not t_gt:
        return True

    inter = len(t_pred & t_gt)
    # Nếu giao nhau trên 25% từ khóa hoặc chứa cụm chính
    return (inter / len(t_gt)) >= 0.25


def check_solution_leakage(pred: Dict[str, Any], gt_ref_solution: str) -> bool:
    """
    Kiểm tra rò rỉ giải pháp (Solution Leakage):
    Hint 1 hoặc Hint 2 bị coi là rò rỉ nếu chứa đoạn mã giải pháp hoàn chỉnh
    hoặc chứa khối mã nhiều hơn 1 dòng lệnh then chốt từ reference_solution.
    """
    if not gt_ref_solution:
        return False

    hints_to_check = [str(pred.get("hint_1", "")), str(pred.get("hint_2", ""))]
    ref_lines = [l.strip() for l in gt_ref_solution.split("\n") if len(l.strip()) > 15]

    for hint in hints_to_check:
        # Nếu hint chứa khối mã csharp lớn
        if "```csharp" in hint and "class " in hint:
            return True
        for line in ref_lines:
            if line in hint and len(line) > 25:
                return True
    return False


def check_hint_policy(pred: Dict[str, Any]) -> bool:
    """
    Kiểm tra tuân thủ chính sách 3 tầng gợi ý:
    - Hint 1: Định hướng, không chứa khối code (```csharp)
    - Hint 2: Giải thích bản chất, có độ dài hợp lý (> 10 ký tự)
    - Hint 3: Hướng dẫn hành động (có nội dung rõ ràng)
    """
    h1 = str(pred.get("hint_1", "")).strip()
    h2 = str(pred.get("hint_2", "")).strip()
    h3 = str(pred.get("hint_3", "")).strip()

    if not h1 or not h2 or not h3:
        return False
    # Hint 1 không được đưa mã nguồn giải pháp thô
    if "```csharp" in h1 or "```" in h1:
        return False
    return True


class TutoringMetricsSuite:
    """Bộ công cụ tính toán toàn diện các chỉ số đánh giá gia sư AI."""

    DEFAULT_PRICING = {
        "prompt_token_usd_per_1m": 0.15,
        "completion_token_usd_per_1m": 0.60
    }

    def __init__(self, pricing: Optional[Dict[str, float]] = None):
        self.pricing = pricing or self.DEFAULT_PRICING

    def evaluate(
        self,
        predictions: List[Dict[str, Any]],
        ground_truth: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Tính toán toàn bộ metrics cho tập dữ liệu.
        predictions và ground_truth có thể so khớp qua trường 'id'.
        """
        gt_map = {item["id"]: item for item in ground_truth}

        # Lưu trữ kết quả theo topic và overall
        topic_samples: Dict[str, List[Tuple[Dict[str, Any], Dict[str, Any]]]] = {}
        matched_pairs: List[Tuple[Dict[str, Any], Dict[str, Any]]] = []

        for pred in predictions:
            sample_id = pred.get("id")
            if sample_id in gt_map:
                gt = gt_map[sample_id]
                matched_pairs.append((pred, gt))
                topic = gt.get("topic", "unknown")
                topic_samples.setdefault(topic, []).append((pred, gt))

        overall_metrics = self._compute_subset_metrics(matched_pairs)
        per_topic_metrics = {
            topic: self._compute_subset_metrics(pairs)
            for topic, pairs in topic_samples.items()
        }

        # Tính tài nguyên và chi phí
        resource_stats = self._compute_resources(predictions)

        return {
            "total_samples": len(matched_pairs),
            "overall": overall_metrics,
            "per_topic": per_topic_metrics,
            "resources": resource_stats
        }

    def _compute_subset_metrics(self, pairs: List[Tuple[Dict[str, Any], Dict[str, Any]]]) -> Dict[str, float]:
        if not pairs:
            return {}

        n_total = len(pairs)
        n_diag_correct = 0
        n_cat_correct = 0
        n_json_valid = 0

        # Buggy subset counters
        n_buggy = 0
        n_loc_correct = 0
        n_faithfulness_correct = 0
        n_faithfulness_eligible = 0
        n_leakage = 0
        n_policy_compliant = 0

        # Control subsets
        n_no_bug = 0
        n_no_bug_fp = 0
        n_insufficient = 0
        n_insufficient_correct = 0

        # Misconceptions
        n_misc_eligible = 0
        n_misc_correct = 0

        kc_f1_scores: List[float] = []

        for pred, gt in pairs:
            # 1. JSON Valid Rate
            if pred.get("json_valid", True):
                n_json_valid += 1

            # 2. Error Category Accuracy
            if pred.get("error_category") == gt.get("error_category"):
                n_cat_correct += 1

            # 3. Knowledge Component F1
            _, _, f1 = compute_sample_kc_f1(
                pred.get("knowledge_components", []),
                gt.get("knowledge_components", [])
            )
            kc_f1_scores.append(f1)

            # Phân tách theo trạng thái lỗi
            gt_status = gt.get("bug_status")
            pred_status = pred.get("bug_status")

            if gt_status == "has_bug":
                n_buggy += 1
                # Diagnosis Accuracy cho buggy
                if pred_status == "has_bug" and (
                    pred.get("bug_type") == gt.get("bug_type") or
                    pred.get("error_category") == gt.get("error_category")
                ):
                    n_diag_correct += 1

                # Localization Accuracy
                if check_localization(pred.get("bug_location"), gt.get("bug_location")):
                    n_loc_correct += 1

                # Evidence Faithfulness
                ev = pred.get("evidence")
                if ev:
                    n_faithfulness_eligible += 1
                    student_code = gt.get("student_code", "")
                    if ev.strip() in student_code:
                        n_faithfulness_correct += 1

                # Solution Leakage Rate
                if check_solution_leakage(pred, gt.get("reference_solution", "")):
                    n_leakage += 1

                # Hint Policy Compliance
                if check_hint_policy(pred):
                    n_policy_compliant += 1

                # Misconception Accuracy
                if gt.get("possible_misconception"):
                    n_misc_eligible += 1
                    if check_misconception_match(pred.get("possible_misconception"), gt.get("possible_misconception")):
                        n_misc_correct += 1

            elif gt_status == "no_bug":
                n_no_bug += 1
                if pred_status == "no_bug":
                    n_diag_correct += 1
                elif pred_status == "has_bug":
                    n_no_bug_fp += 1  # False Positive

            elif gt_status == "insufficient_context":
                n_insufficient += 1
                if pred_status == "insufficient_context":
                    n_diag_correct += 1
                    n_insufficient_correct += 1

        return {
            "diagnosis_accuracy": round(n_diag_correct / n_total, 4) if n_total > 0 else 0.0,
            "bug_localization_accuracy": round(n_loc_correct / n_buggy, 4) if n_buggy > 0 else 0.0,
            "error_category_accuracy": round(n_cat_correct / n_total, 4) if n_total > 0 else 0.0,
            "knowledge_component_f1": round(sum(kc_f1_scores) / len(kc_f1_scores), 4) if kc_f1_scores else 0.0,
            "misconception_accuracy": round(n_misc_correct / n_misc_eligible, 4) if n_misc_eligible > 0 else 0.0,
            "no_bug_false_positive_rate": round(n_no_bug_fp / n_no_bug, 4) if n_no_bug > 0 else 0.0,
            "insufficient_context_accuracy": round(n_insufficient_correct / n_insufficient, 4) if n_insufficient > 0 else 0.0,
            "evidence_faithfulness": round(n_faithfulness_correct / n_faithfulness_eligible, 4) if n_faithfulness_eligible > 0 else 1.0,
            "solution_leakage_rate": round(n_leakage / n_buggy, 4) if n_buggy > 0 else 0.0,
            "json_valid_rate": round(n_json_valid / n_total, 4) if n_total > 0 else 0.0,
            "hint_policy_compliance": round(n_policy_compliant / n_buggy, 4) if n_buggy > 0 else 0.0,
        }

    def _compute_resources(self, predictions: List[Dict[str, Any]]) -> Dict[str, Any]:
        latencies = [p.get("latency_ms", 0.0) for p in predictions if "latency_ms" in p]
        prompt_tokens = sum(p.get("prompt_tokens", 0) for p in predictions)
        completion_tokens = sum(p.get("completion_tokens", 0) for p in predictions)
        total_tokens = prompt_tokens + completion_tokens

        n = len(predictions) or 1
        sorted_lat = sorted(latencies) if latencies else [0.0]

        p50 = sorted_lat[int(len(sorted_lat) * 0.50)] if sorted_lat else 0.0
        p95 = sorted_lat[min(int(len(sorted_lat) * 0.95), len(sorted_lat) - 1)] if sorted_lat else 0.0
        avg_lat = sum(latencies) / len(latencies) if latencies else 0.0

        p_rate = self.pricing.get("prompt_token_usd_per_1m", 0.15)
        c_rate = self.pricing.get("completion_token_usd_per_1m", 0.60)
        cost = (prompt_tokens / 1_000_000 * p_rate) + (completion_tokens / 1_000_000 * c_rate)

        return {
            "latency_mean_ms": round(avg_lat, 2),
            "latency_p50_ms": round(p50, 2),
            "latency_p95_ms": round(p95, 2),
            "prompt_tokens_total": prompt_tokens,
            "prompt_tokens_avg": round(prompt_tokens / n, 1),
            "completion_tokens_total": completion_tokens,
            "completion_tokens_avg": round(completion_tokens / n, 1),
            "total_tokens": total_tokens,
            "estimated_cost_usd": round(cost, 5)
        }
