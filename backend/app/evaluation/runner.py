"""
Evaluation Runner cho VietCSharpTutor (APT-028).

Hỗ trợ 4 hệ thống:
- Baseline A: Direct LLM debugging prompt
- Baseline B: Generic tutor prompt
- Proposed C: Structured diagnosis + progressive hints
- Proposed D: Structured diagnosis + progressive hints + student context

Ghi nhận toàn diện:
- model, provider, prompt_version, dataset_version, sample_id
- latency, token usage, raw structured prediction, validator actions
- Tuyệt đối không ghi nhận API keys vào logs hay manifests.
- Hỗ trợ deterministic run manifests và seed để tái lập 100%.
"""

import argparse
import hashlib
import json
import os
import random
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# Thêm đường dẫn để import
CURRENT_DIR = Path(__file__).resolve().parent
ROOT_DIR = CURRENT_DIR.parent.parent.parent if CURRENT_DIR.name == "evaluation" else CURRENT_DIR.parent

try:
    from app.evaluation.prompts import (
        PROMPT_VERSIONS,
        SYSTEM_PROMPT_A,
        SYSTEM_PROMPT_B,
        SYSTEM_PROMPT_C,
        SYSTEM_PROMPT_D,
        build_prompt_a,
        build_prompt_b,
        build_prompt_c,
        build_prompt_d,
    )
except ImportError:
    from backend.app.evaluation.prompts import (
        PROMPT_VERSIONS,
        SYSTEM_PROMPT_A,
        SYSTEM_PROMPT_B,
        SYSTEM_PROMPT_C,
        SYSTEM_PROMPT_D,
        build_prompt_a,
        build_prompt_b,
        build_prompt_c,
        build_prompt_d,
    )


def get_git_commit() -> str:
    """Lấy commit hash hiện tại của repository một cách an toàn."""
    try:
        res = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        return res.stdout.strip()
    except Exception:
        return "unknown_commit"


class EvaluationRunner:
    """Runner chịu trách nhiệm thực thi thí nghiệm đánh giá theo protocol đóng băng."""

    def __init__(
        self,
        system: str,
        split: str,
        model: str = "mock-tutor-v1",
        provider: str = "mock",
        dataset_path: Optional[Path] = None,
        output_dir: Optional[Path] = None,
        seed: int = 42,
        mock: bool = False,
        provider_client: Optional[Any] = None,
        student_context: Optional[Dict[str, Any]] = None,
    ):
        self.system = system.upper()
        if self.system not in ("A", "B", "C", "D"):
            raise ValueError(f"Hệ thống không hợp lệ: {system}. Phải là A, B, C, hoặc D.")

        self.split = split.lower()
        if self.split not in ("dev", "validation", "test"):
            raise ValueError(f"Split không hợp lệ: {split}. Phải là dev, validation, hoặc test.")

        self.model = model
        self.provider = provider
        self.seed = seed
        self.mock = mock
        self.prompt_version = PROMPT_VERSIONS[self.system]
        self.provider_client = provider_client
        self.student_context = student_context

        if self.provider_client is None and not self.mock and self.provider in ("openai", "azure"):
            try:
                from app.tutor.provider import OpenAITutorProvider
                self.provider_client = OpenAITutorProvider()
            except Exception:
                self.provider_client = None

        root = Path(__file__).resolve().parents[3]
        self.dataset_path = dataset_path or (root / "data" / "vietcsharptutor" / "vietcsharptutor_600.jsonl")
        
        timestamp_str = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        self.run_id = f"run_{self.system}_{self.split}_{timestamp_str}"
        self.output_dir = output_dir or (root / "runs" / self.run_id)

    def load_dataset(self) -> Tuple[List[Dict[str, Any]], str, str]:
        """Tải dataset, lọc theo split và tính hash toàn vẹn."""
        if not self.dataset_path.exists():
            raise FileNotFoundError(f"Không tìm thấy file dataset: {self.dataset_path}")

        all_samples: List[Dict[str, Any]] = []
        with open(self.dataset_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    all_samples.append(json.loads(line))

        full_dump = "\n".join(json.dumps(s, sort_keys=True) for s in all_samples)
        dataset_hash = hashlib.sha256(full_dump.encode("utf-8")).hexdigest()

        split_samples = [s for s in all_samples if s.get("split") == self.split]
        split_dump = "\n".join(json.dumps(s, sort_keys=True) for s in split_samples)
        split_hash = hashlib.sha256(split_dump.encode("utf-8")).hexdigest()

        return split_samples, dataset_hash, split_hash

    def run(self) -> Dict[str, Any]:
        """Thực thi toàn bộ pipeline đánh giá cho split đã chọn."""
        random.seed(self.seed)
        samples, dataset_hash, split_hash = self.load_dataset()

        print(f"=== BẮT ĐẦU CHẠY ĐÁNH GIÁ ===")
        print(f"- Run ID: {self.run_id}")
        print(f"- Hệ thống: {self.system} ({self.prompt_version})")
        print(f"- Split: {self.split} ({len(samples)} mẫu)")
        print(f"- Model: {self.model} (Provider: {self.provider})")
        print(f"- SHA256 Split Hash: {split_hash}")

        self.output_dir.mkdir(parents=True, exist_ok=True)
        predictions_file = self.output_dir / "predictions.jsonl"
        manifest_file = self.output_dir / "manifest.json"

        predictions: List[Dict[str, Any]] = []
        t0_total = time.time()

        for idx, sample in enumerate(samples, start=1):
            pred = self._predict_single(sample)
            predictions.append(pred)
            if idx % 30 == 0 or idx == len(samples):
                print(f"  Đã hoàn thành {idx}/{len(samples)} mẫu...")

        total_duration = time.time() - t0_total

        # 1. Ghi file predictions.jsonl
        with open(predictions_file, "w", encoding="utf-8") as f:
            for pred in predictions:
                f.write(json.dumps(pred, ensure_ascii=False) + "\n")

        # 2. Tạo và ghi immutable run manifest
        manifest = {
            "run_id": self.run_id,
            "system": self.system,
            "system_description": {
                "A": "Baseline A: Direct LLM Debugging Prompt",
                "B": "Baseline B: Generic Tutor Prompt",
                "C": "Proposed C: Structured Diagnosis + Progressive Hints",
                "D": "Proposed D: Structured Diagnosis + Progressive Hints + Student Context"
            }[self.system],
            "model": self.model,
            "provider": self.provider,
            "prompt_version": self.prompt_version,
            "dataset_version": "1.0.0",
            "dataset_path": str(self.dataset_path),
            "dataset_hash": dataset_hash,
            "split": self.split,
            "split_hash": split_hash,
            "total_samples": len(samples),
            "random_seed": self.seed,
            "git_commit": get_git_commit(),
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "execution_duration_sec": round(total_duration, 2),
            "config": {
                "temperature": 0.2 if self.system in ("C", "D") else 0.7,
                "top_p": 0.95,
                "max_output_tokens": 1024,
                "mock_mode": self.mock
            }
        }

        with open(manifest_file, "w", encoding="utf-8") as f:
            json.dump(manifest, f, ensure_ascii=False, indent=2)

        print(f"\nĐÃ HOÀN THÀNH RUN THỰC NGHIỆM:")
        print(f"- Predictions: {predictions_file}")
        print(f"- Manifest: {manifest_file}")

        return {
            "run_id": self.run_id,
            "predictions_path": str(predictions_file),
            "manifest_path": str(manifest_file),
            "total_samples": len(samples),
            "duration_sec": total_duration
        }

    def _call_provider(self, messages: List[Dict[str, Any]], temperature: float, max_tokens: int) -> str:
        """Gửi prompt tới provider và nhận phản hồi văn bản thực tế."""
        if self.provider_client is None:
            raise RuntimeError(
                f"System {self.system} cannot produce prediction without a configured LLM provider. "
                "Direct ground-truth copying has been completely removed (APT-053)."
            )

        if hasattr(self.provider_client, "generate_response_sync"):
            return self.provider_client.generate_response_sync(messages, temperature=temperature, max_tokens=max_tokens)

        import asyncio
        import inspect

        gen = self.provider_client.generate_response(messages, temperature=temperature, max_tokens=max_tokens)
        if inspect.isawaitable(gen):
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = None

            if loop and loop.is_running():
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    return executor.submit(
                        asyncio.run,
                        self.provider_client.generate_response(messages, temperature=temperature, max_tokens=max_tokens)
                    ).result()
            else:
                return asyncio.run(gen)
        return str(gen)

    def _predict_single(self, sample: Any) -> Dict[str, Any]:
        """
        Dự đoán cho từng mẫu độc lập qua quy trình Clean-Room:
        ModelInput -> Prompt -> Firewall -> Provider -> Parser -> Non-Gold Validator -> Prediction.

        Tuyệt đối không truy cập hoặc sao chép nhãn vàng (Ground Truth).
        """
        from app.evaluation.schemas import GroundTruth, ModelInput, assert_not_ground_truth
        from app.evaluation.firewall import GroundTruthFirewall

        # 1. Bảo vệ tầng đầu vào: Từ chối dứt khoát GroundTruth và sentinels
        if isinstance(sample, GroundTruth):
            raise TypeError("EvaluationRunner cannot accept GroundTruth objects directly as model input. Pass ModelInput instead.")
        assert_not_ground_truth(sample)

        # 2. Chuẩn hóa sang ModelInput chỉ chứa 4 trường danh sách trắng (Whitelist)
        if isinstance(sample, ModelInput):
            model_input = sample
        elif hasattr(sample, "model_input"):
            model_input = sample.model_input
        elif isinstance(sample, dict):
            model_input = ModelInput.from_dataset_record(sample)
        else:
            raise TypeError(f"EvaluationRunner cannot process input of type {type(sample).__name__}")

        # 3. Chốt chặn Provider: Không thể sinh prediction nếu thiếu provider
        if self.provider_client is None:
            raise RuntimeError(
                f"System {self.system} cannot produce prediction without a configured LLM provider. "
                "Direct ground-truth copying has been completely removed (APT-053)."
            )

        # 4. Xây dựng prompt tương ứng từng hệ thống từ ModelInput thuần khiết
        if self.system == "A":
            system_prompt = SYSTEM_PROMPT_A
            user_prompt = build_prompt_a(model_input)
        elif self.system == "B":
            system_prompt = SYSTEM_PROMPT_B
            user_prompt = build_prompt_b(model_input)
        elif self.system == "C":
            system_prompt = SYSTEM_PROMPT_C
            user_prompt = build_prompt_c(model_input)
        elif self.system == "D":
            system_prompt = SYSTEM_PROMPT_D
            ctx = None
            if isinstance(self.student_context, dict):
                ctx = self.student_context.get(model_input.sample_id, self.student_context)
            if ctx is not None:
                assert_not_ground_truth(ctx)
            user_prompt = build_prompt_d(model_input, student_context=ctx)
        else:
            raise ValueError(f"Hệ thống không xác định: {self.system}")

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        # 5. Fail-Closed Firewall quét toàn bộ messages trước khi gọi provider
        GroundTruthFirewall.default().inspect(messages, base_path=f"runner.{self.system}.messages")

        # 6. Gọi Provider thực tế và đo đạc độ trễ
        t0 = time.time()
        temperature = 0.2 if self.system in ("C", "D") else 0.7
        raw_response = self._call_provider(messages, temperature=temperature, max_tokens=1024)
        latency_ms = round((time.time() - t0) * 1000, 2)

        prompt_chars = sum(len(m.get("content", "")) for m in messages)
        prompt_tokens = max(1, prompt_chars // 4)
        completion_tokens = max(1, len(raw_response) // 4)

        # 7. Parser: Bóc tách cấu trúc từ chuỗi phản hồi thô của provider
        parsed, json_valid, parse_actions = parse_provider_output(raw_response, self.system)

        # 8. Non-Gold Validator: Kiểm định tính hợp lệ mà KHÔNG truy cập Ground Truth
        validated_data, validator_actions = validate_prediction_non_gold(
            parsed_data=parsed,
            model_input=model_input,
            parse_actions=parse_actions,
        )

        # 9. Đóng gói Prediction từ dữ liệu đã qua kiểm định
        return {
            "id": model_input.sample_id,
            "model": self.model,
            "provider": self.provider,
            "prompt_version": self.prompt_version,
            "latency_ms": latency_ms,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "bug_status": validated_data.get("bug_status"),
            "error_category": validated_data.get("error_category"),
            "bug_type": validated_data.get("bug_type"),
            "bug_location": validated_data.get("bug_location"),
            "evidence": validated_data.get("evidence"),
            "knowledge_components": validated_data.get("knowledge_components") if isinstance(validated_data.get("knowledge_components"), list) else [],
            "possible_misconception": validated_data.get("possible_misconception"),
            "hint_1": validated_data.get("hint_1"),
            "hint_2": validated_data.get("hint_2"),
            "hint_3": validated_data.get("hint_3"),
            "reference_diagnosis": validated_data.get("reference_diagnosis"),
            "explanation_vi": validated_data.get("explanation_vi") or raw_response,
            "json_valid": json_valid,
            "validator_actions": validator_actions,
        }


def clean_json_string(raw_text: str) -> str:
    """Bóc tách chuỗi JSON nếu được bọc trong markdown code block hoặc văn bản tự do."""
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
    Parser bóc tách phản hồi từ Provider mà không có bất kỳ giả định hay can thiệp từ nhãn vàng.
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
    from app.evaluation.schemas import assert_not_ground_truth
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
