"""
Ablation Study Configurations & Engine (APT-030).

5 cấu hình thực nghiệm triệt tiêu:
1. FULL:
   - Structured diagnosis
   - Progressive hints (3 tiers)
   - Student context (mastery, attempts, prior misconceptions)
2. NO_STUDENT_MODEL:
   - Structured diagnosis
   - Progressive hints
   - (Loại bỏ student context)
3. NO_PROGRESSIVE_HINT:
   - Structured diagnosis
   - Student context
   - (Loại bỏ gợi ý tăng dần 3 bậc -> cung cấp 1 hint trực diện giải pháp)
4. NO_STRUCTURED_DIAGNOSIS:
   - Progressive hints
   - Student context
   - (Loại bỏ chẩn đoán cấu trúc JSON -> prompt tự do)
5. DIRECT_BASELINE:
   - Direct LLM debugging prompt only (chỉ hỏi tìm lỗi và sửa code)

Mỗi cấu hình chỉ thay đổi duy nhất một thành phần để đảm bảo tính công bằng khoa học.
"""

import hashlib
import json
import random
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

ROOT_DIR = Path(__file__).resolve().parents[3]

try:
    from app.evaluation.runner import (
        EvaluationRunner,
        get_git_commit,
        clean_json_string,
        parse_provider_output,
        validate_prediction_non_gold,
    )
    from app.evaluation.prompts import (
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
    from backend.app.evaluation.runner import (
        EvaluationRunner,
        get_git_commit,
        clean_json_string,
        parse_provider_output,
        validate_prediction_non_gold,
    )
    from backend.app.evaluation.prompts import (
        SYSTEM_PROMPT_A,
        SYSTEM_PROMPT_B,
        SYSTEM_PROMPT_C,
        SYSTEM_PROMPT_D,
        build_prompt_a,
        build_prompt_b,
        build_prompt_c,
        build_prompt_d,
    )

ABLATION_CONFIGS = {
    "FULL": {
        "description": "Full CodeSense: Structured Diagnosis + Progressive Hints + Student Context",
        "has_structured_diagnosis": True,
        "has_progressive_hints": True,
        "has_student_context": True,
        "prompt_version": "v1.0-ablation-full"
    },
    "NO_STUDENT_MODEL": {
        "description": "Ablation: Loai bo Student Context, chi giu Structured Diagnosis + Progressive Hints",
        "has_structured_diagnosis": True,
        "has_progressive_hints": True,
        "has_student_context": False,
        "prompt_version": "v1.0-ablation-no-student-model"
    },
    "NO_PROGRESSIVE_HINT": {
        "description": "Ablation: Loai bo 3 bac goi y tang dan, dua truc tiep goi y giai phap duy nhat",
        "has_structured_diagnosis": True,
        "has_progressive_hints": False,
        "has_student_context": True,
        "prompt_version": "v1.0-ablation-no-progressive-hint"
    },
    "NO_STRUCTURED_DIAGNOSIS": {
        "description": "Ablation: Loai bo chan doan cau truc JSON, su dung prompt tu do khong rang buoc schema",
        "has_structured_diagnosis": False,
        "has_progressive_hints": True,
        "has_student_context": True,
        "prompt_version": "v1.0-ablation-no-structured-diagnosis"
    },
    "DIRECT_BASELINE": {
        "description": "Baseline: Direct LLM Debugging khong chan doan, khong goi y, khong context",
        "has_structured_diagnosis": False,
        "has_progressive_hints": False,
        "has_student_context": False,
        "prompt_version": "v1.0-ablation-direct-baseline"
    }
}


class AblationRunner:
    """Runner thực thi các cấu hình triệt tiêu có thể tái lập hoàn toàn."""

    def __init__(
        self,
        config_name: str,
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
        name_upper = config_name.upper()
        if name_upper not in ABLATION_CONFIGS:
            raise ValueError(f"Cấu hình ablation không hợp lệ: {config_name}. Hỗ trợ: {list(ABLATION_CONFIGS.keys())}")

        self.config_name = name_upper
        self.config_details = ABLATION_CONFIGS[name_upper]
        self.split = split.lower()
        if self.split not in ("dev", "validation", "test"):
            raise ValueError(f"Split không hợp lệ: {split}")

        self.model = model
        self.provider = provider
        self.seed = seed
        self.mock = mock
        self.provider_client = provider_client
        self.student_context = student_context

        if self.provider_client is None and not self.mock and self.provider in ("openai", "azure"):
            try:
                from app.tutor.provider import OpenAITutorProvider
                self.provider_client = OpenAITutorProvider()
            except Exception:
                self.provider_client = None

        root = ROOT_DIR
        self.dataset_path = dataset_path or (root / "data" / "vietcsharptutor" / "vietcsharptutor_600.jsonl")
        timestamp_str = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        self.run_id = f"ablation_{self.config_name}_{self.split}_{timestamp_str}"
        self.output_dir = output_dir or (ROOT_DIR / "runs" / self.run_id)
        self.manifest_dir = ROOT_DIR / "manifests"

    def run(self) -> Dict[str, Any]:
        random.seed(self.seed)
        runner_helper = EvaluationRunner(system="C", split=self.split, dataset_path=self.dataset_path)
        samples, dataset_hash, split_hash = runner_helper.load_dataset()

        print(f"=== BẮT ĐẦU CHẠY ABLATION: {self.config_name} ===")
        print(f"- Mô tả: {self.config_details['description']}")
        print(f"- Split: {self.split} ({len(samples)} mẫu)")
        print(f"- Split Hash: {split_hash}")

        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.manifest_dir.mkdir(parents=True, exist_ok=True)
        predictions_file = self.output_dir / "predictions.jsonl"
        manifest_file = self.output_dir / "manifest.json"
        copy_manifest_file = self.manifest_dir / f"{self.run_id}_manifest.json"

        predictions: List[Dict[str, Any]] = []
        t0 = time.time()

        for idx, sample in enumerate(samples, start=1):
            pred = self._predict_sample(sample)
            predictions.append(pred)

        duration = time.time() - t0

        # Ghi predictions
        with open(predictions_file, "w", encoding="utf-8") as f:
            for p in predictions:
                f.write(json.dumps(p, ensure_ascii=False) + "\n")

        # Ghi immutable manifest
        manifest = {
            "run_id": self.run_id,
            "ablation_config": self.config_name,
            "config_details": self.config_details,
            "model": self.model,
            "provider": self.provider,
            "prompt_version": self.config_details["prompt_version"],
            "dataset_version": "1.0.0",
            "dataset_path": str(self.dataset_path),
            "dataset_hash": dataset_hash,
            "split": self.split,
            "split_hash": split_hash,
            "total_samples": len(samples),
            "random_seed": self.seed,
            "git_commit": get_git_commit(),
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "duration_sec": round(duration, 2)
        }

        with open(manifest_file, "w", encoding="utf-8") as f:
            json.dump(manifest, f, ensure_ascii=False, indent=2)

        with open(copy_manifest_file, "w", encoding="utf-8") as f:
            json.dump(manifest, f, ensure_ascii=False, indent=2)

        print(f"Đã hoàn thành {self.config_name}: {predictions_file}")
        return {
            "run_id": self.run_id,
            "predictions_path": str(predictions_file),
            "manifest_path": str(manifest_file),
            "total_samples": len(samples)
        }

    def _call_provider(self, messages: List[Dict[str, Any]], temperature: float, max_tokens: int) -> str:
        """Gửi prompt tới provider và nhận phản hồi văn bản thực tế."""
        if self.provider_client is None:
            raise RuntimeError(
                f"Ablation configuration {self.config_name} cannot produce predictions without an LLM provider. "
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

    def _predict_sample(self, sample: Any) -> Dict[str, Any]:
        """
        Dự đoán cho từng mẫu độc lập trong nghiên cứu triệt tiêu (ablation study)
        tuân thủ nghiêm ngặt quy trình Clean-Room không sao chép nhãn vàng.
        """
        from app.evaluation.schemas import GroundTruth, ModelInput, assert_not_ground_truth
        from app.evaluation.firewall import GroundTruthFirewall

        # 1. Bảo vệ tầng đầu vào: Từ chối dứt khoát GroundTruth và sentinels
        if isinstance(sample, GroundTruth):
            raise TypeError("AblationRunner cannot accept GroundTruth objects directly as model input. Pass ModelInput instead.")
        assert_not_ground_truth(sample)

        # 2. Chuẩn hóa sang ModelInput chỉ chứa 4 trường danh sách trắng (Whitelist)
        if isinstance(sample, ModelInput):
            model_input = sample
        elif hasattr(sample, "model_input"):
            model_input = sample.model_input
        elif isinstance(sample, dict):
            model_input = ModelInput.from_dataset_record(sample)
        else:
            raise TypeError(f"AblationRunner cannot process input of type {type(sample).__name__}")

        # 3. Chốt chặn Provider: Bắt buộc phải có provider thực tế
        if self.provider_client is None:
            raise RuntimeError(
                f"Ablation configuration {self.config_name} cannot produce predictions without an LLM provider. "
                "Direct ground-truth copying has been completely removed (APT-053)."
            )

        # 4. Xây dựng prompt tương ứng cấu hình triệt tiêu
        if self.config_name == "FULL":
            system_prompt = SYSTEM_PROMPT_D
            ctx = None
            if isinstance(self.student_context, dict):
                ctx = self.student_context.get(model_input.sample_id, self.student_context)
            if ctx is not None:
                assert_not_ground_truth(ctx)
            user_prompt = build_prompt_d(model_input, student_context=ctx)
        elif self.config_name == "NO_STUDENT_MODEL":
            system_prompt = SYSTEM_PROMPT_C
            user_prompt = build_prompt_c(model_input)
        elif self.config_name == "NO_PROGRESSIVE_HINT":
            system_prompt = SYSTEM_PROMPT_C
            user_prompt = build_prompt_c(model_input)
        elif self.config_name == "NO_STRUCTURED_DIAGNOSIS":
            system_prompt = SYSTEM_PROMPT_B
            user_prompt = build_prompt_b(model_input)
        elif self.config_name == "DIRECT_BASELINE":
            system_prompt = SYSTEM_PROMPT_A
            user_prompt = build_prompt_a(model_input)
        else:
            raise ValueError(f"Không nhận diện cấu hình: {self.config_name}")

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        # 5. Fail-Closed Firewall quét toàn bộ messages trước khi gọi provider
        GroundTruthFirewall.default().inspect(messages, base_path=f"ablation.{self.config_name}.messages")

        # 6. Gọi Provider thực tế và đo đạc độ trễ
        t0 = time.time()
        temperature = 0.2 if self.config_details.get("has_structured_diagnosis", True) else 0.7
        raw_response = self._call_provider(messages, temperature=temperature, max_tokens=1024)
        latency_ms = round((time.time() - t0) * 1000, 2)

        prompt_chars = sum(len(m.get("content", "")) for m in messages)
        prompt_tokens = max(1, prompt_chars // 4)
        completion_tokens = max(1, len(raw_response) // 4)

        # 7. Parser: Bóc tách cấu trúc từ chuỗi phản hồi thô của provider
        sys_type = "C" if self.config_details.get("has_structured_diagnosis", True) else "B"
        parsed, json_valid, parse_actions = parse_provider_output(raw_response, sys_type)

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
            "prompt_version": self.config_details["prompt_version"],
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
