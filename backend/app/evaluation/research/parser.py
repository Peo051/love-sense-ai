"""
Clean-Room Parser & Non-Gold Validator (APT-054).

Nhiệm vụ:
- Bóc tách phản hồi JSON / Freeform text từ Provider mà không có bất kỳ giả định hay can thiệp từ nhãn vàng.
- Kiểm định tính hợp lệ của schema dự đoán và bằng chứng (evidence grounding) CHỈ dựa trên ModelInput.
- Tuyệt đối không nhận, không xử lý và không đối chiếu với GroundTruth.
"""

import json
import re
from typing import Any, Dict, List, Tuple

from app.evaluation.schemas import assert_not_ground_truth


def clean_json_string(raw_text: str) -> str:
    """Bóc tách chuỗi JSON nếu được bọc trong markdown code block (```json ... ```) hoặc văn bản tự do."""
    text = raw_text.strip()
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    first_brace = text.find("{")
    last_brace = text.rfind("}")
    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        return text[first_brace : last_brace + 1].strip()
    return text


def parse_provider_output(raw_output: str, system: str) -> Tuple[Dict[str, Any], bool, List[str]]:
    """
    Parser bóc tách phản hồi từ Provider mà không có bất kỳ can thiệp nào từ nhãn vàng.
    """
    actions: List[str] = []
    if not raw_output or not raw_output.strip():
        actions.append("empty_provider_output")
        return {}, False, actions

    cleaned = clean_json_string(raw_output)
    try:
        parsed = json.loads(cleaned)
        if isinstance(parsed, dict):
            actions.append("json_parsed_successfully")

            # Chuẩn hóa nếu output tuân theo format nested diagnosis (như TutorResponse)
            if "diagnosis" in parsed and isinstance(parsed["diagnosis"], dict):
                diag = parsed["diagnosis"]
                cat = str(diag.get("category") or "").strip()
                if "bug_status" not in parsed:
                    if cat == "no_bug":
                        parsed["bug_status"] = "no_bug"
                    elif cat == "insufficient_context":
                        parsed["bug_status"] = "insufficient_context"
                    elif cat:
                        parsed["bug_status"] = "has_bug"
                if "error_category" not in parsed and cat:
                    parsed["error_category"] = cat
                if "bug_type" not in parsed and diag.get("issue_type"):
                    parsed["bug_type"] = diag.get("issue_type")
                if "bug_location" not in parsed and diag.get("location"):
                    parsed["bug_location"] = diag.get("location")
                if "evidence" in parsed and isinstance(parsed["evidence"], dict):
                    parsed["evidence"] = parsed["evidence"].get("code")
                if "possible_misconception" in parsed and isinstance(parsed["possible_misconception"], dict):
                    parsed["possible_misconception"] = parsed["possible_misconception"].get("description")
                if "tutor_response" in parsed:
                    if "hint_1" not in parsed:
                        parsed["hint_1"] = parsed["tutor_response"]
                    if "explanation_vi" not in parsed:
                        parsed["explanation_vi"] = parsed["tutor_response"]

            return parsed, True, actions
        else:
            actions.append("json_not_a_dictionary")
            return {}, False, actions
    except Exception as exc:
        actions.append(f"json_decode_failed: {str(exc)[:50]}")
        if system in ("A", "B"):
            actions.append("freeform_text_parsed")
        return {"explanation_vi": raw_output}, False, actions


def validate_prediction_non_gold(
    parsed_data: Dict[str, Any],
    model_input: Any,
    parse_actions: List[str],
) -> Tuple[Dict[str, Any], List[str]]:
    """
    Non-gold Validator: Kiểm định tính hợp lệ của schema dự đoán và bằng chứng (evidence grounding)
    CHỈ dựa trên ModelInput (student_code, problem_statement, compiler_error),
    TUYỆT ĐỐI KHÔNG CÓ quyền truy cập vào nhãn vàng (GroundTruth).
    """
    assert_not_ground_truth(model_input)
    assert_not_ground_truth(parsed_data)

    actions = list(parse_actions)
    validated = dict(parsed_data)

    # 1. Kiểm định bug_status
    bug_status = validated.get("bug_status")
    if bug_status in ("has_bug", "no_bug", "insufficient_context"):
        actions.append("valid_bug_status_schema")
    elif bug_status is not None:
        actions.append("invalid_bug_status_schema")

    # 2. Chuẩn hóa knowledge_components
    kcs = validated.get("knowledge_components")
    if isinstance(kcs, list):
        actions.append("valid_kc_list")
    elif kcs is not None:
        validated["knowledge_components"] = [str(kcs)]
        actions.append("kc_converted_to_list")
    else:
        validated["knowledge_components"] = []

    # 3. Evidence Grounding kiểm tra đối chiếu mã nguồn học sinh (student_code từ ModelInput)
    ev = validated.get("evidence")
    student_code = getattr(model_input, "student_code", "") or ""
    if ev and isinstance(ev, str):
        if ev.strip() and ev.strip() in student_code:
            actions.append("evidence_grounded_in_student_code")
        else:
            actions.append("evidence_unverified_or_hallucinated")

    # 4. Kiểm tra bug_location
    loc = validated.get("bug_location")
    if isinstance(loc, dict) and "start_line" in loc:
        actions.append("bug_location_format_valid")

    actions.append("non_gold_validation_completed")
    return validated, actions
