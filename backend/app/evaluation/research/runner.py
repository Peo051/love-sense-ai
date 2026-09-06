"""
Research Evaluation Runner (APT-054).

QUY TẮC NGHIÊN CỨU (RESEARCH EVALUATION RULES):
- Real provider only (Bắt buộc kết nối thực tế tới LLM, sử dụng ResearchProvider).
- Không truy cập nhãn vàng (No Ground Truth access).
- Không có cờ mock (No mock flag in runner or CLI).
- Không cho phép dự đoán tất định giả lập (No deterministic synthetic prediction).
- Không có fallback ngầm (Fail-closed on provider errors).
- FakeTestProvider bị từ chối tuyệt đối trong Research Mode.
"""

import argparse
import asyncio
import concurrent.futures
import inspect
import json
import logging
import os
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

from app.evaluation.firewall import GroundTruthFirewall
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
from app.evaluation.research.parser import parse_provider_output, validate_prediction_non_gold
from app.evaluation.research.provenance import compute_dataset_hashes, create_research_manifest, get_git_commit
from app.evaluation.research.provider import (
    OpenAIResearchProvider,
    ResearchProvider,
    ResearchProviderConfigurationError,
    validate_research_provider,
)
from app.evaluation.schemas import GroundTruth, ModelInput, assert_not_ground_truth

logger = logging.getLogger(__name__)


class ResearchRunner:
    """
    Bộ thực thi đánh giá nghiên cứu thực nghiệm khoa học độc lập.
    Tuyệt đối không hỗ trợ mock hay canned responses trong môi trường nghiên cứu.
    """

    def __init__(
        self,
        system: str,
        split: str,
        model: str = "gpt-4o-mini",
        provider: str = "openai",
        dataset_path: Optional[Path] = None,
        output_dir: Optional[Path] = None,
        seed: int = 42,
        provider_client: Optional[Any] = None,
        student_context: Optional[Dict[str, Any]] = None,
        *,
        allow_test_doubles: bool = False,
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
        self.prompt_version = PROMPT_VERSIONS[self.system]
        self.student_context = student_context
        self.allow_test_doubles = allow_test_doubles

        # Preflight validation bắt buộc trước khi thực thi nghiên cứu (APT-055)
        self.provider_client = validate_research_provider(
            provider=self.provider,
            model=self.model,
            provider_client=provider_client,
            allow_test_doubles=self.allow_test_doubles,
        )

        root = Path(__file__).resolve().parents[4]
        self.dataset_path = dataset_path or (root / "data" / "vietcsharptutor" / "vietcsharptutor_600.jsonl")

        timestamp_str = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        self.run_id = f"run_{self.system}_{self.split}_{timestamp_str}"
        self.output_dir = output_dir or (root / "runs" / self.run_id)

    def load_dataset(self) -> Tuple[List[Dict[str, Any]], str, str]:
        """Tải dataset, lọc theo split và tính hash toàn vẹn SHA256."""
        if not self.dataset_path.exists():
            raise FileNotFoundError(f"Không tìm thấy file dataset: {self.dataset_path}")

        all_samples: List[Dict[str, Any]] = []
        with open(self.dataset_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    all_samples.append(json.loads(line))

        split_samples = [s for s in all_samples if s.get("split") == self.split]
        dataset_hash, split_hash = compute_dataset_hashes(all_samples, split_samples)

        return split_samples, dataset_hash, split_hash

    def run(self) -> Dict[str, Any]:
        """Thực thi toàn bộ pipeline đánh giá cho split đã chọn."""
        # Preflight verification bắt buộc trước khi tải dataset và xử lý mẫu (APT-055)
        validate_research_provider(
            provider=self.provider,
            model=self.model,
            provider_client=self.provider_client,
            allow_test_doubles=self.allow_test_doubles,
        )

        random.seed(self.seed)
        samples, dataset_hash, split_hash = self.load_dataset()

        print(f"=== BẮT ĐẦU CHẠY ĐÁNH GIÁ NGHIÊN CỨU (CLEAN-ROOM) ===")
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

        # 2. Tạo và ghi immutable run manifest (hoàn toàn không có mock_mode)
        system_descriptions = {
            "A": "Baseline A: Direct LLM Debugging Prompt",
            "B": "Baseline B: Generic Tutor Prompt",
            "C": "Proposed C: Structured Diagnosis + Progressive Hints",
            "D": "Proposed D: Structured Diagnosis + Progressive Hints + Student Context",
        }
        manifest = create_research_manifest(
            run_id=self.run_id,
            system=self.system,
            system_description=system_descriptions[self.system],
            model=self.model,
            provider=self.provider,
            prompt_version=self.prompt_version,
            dataset_path=self.dataset_path,
            dataset_hash=dataset_hash,
            split=self.split,
            split_hash=split_hash,
            total_samples=len(samples),
            seed=self.seed,
            execution_duration_sec=total_duration,
            temperature=0.2 if self.system in ("C", "D") else 0.7,
            max_output_tokens=1024,
        )

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
            "duration_sec": total_duration,
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

        gen = self.provider_client.generate_response(messages, temperature=temperature, max_tokens=max_tokens)
        if inspect.isawaitable(gen):
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = None

            if loop and loop.is_running():
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    return executor.submit(
                        asyncio.run,
                        self.provider_client.generate_response(messages, temperature=temperature, max_tokens=max_tokens),
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
        # 1. Bảo vệ tầng đầu vào: Từ chối dứt khoát GroundTruth và sentinels
        if isinstance(sample, GroundTruth):
            raise TypeError(f"{self.__class__.__name__} cannot accept GroundTruth objects directly as model input. Pass ModelInput instead.")
        assert_not_ground_truth(sample)

        # 2. Chuẩn hóa sang ModelInput chỉ chứa các trường danh sách trắng (Whitelist)
        if isinstance(sample, ModelInput):
            model_input = sample
        elif hasattr(sample, "model_input"):
            model_input = sample.model_input
        elif isinstance(sample, dict):
            model_input = ModelInput.from_dataset_record(sample)
        else:
            raise TypeError(f"{self.__class__.__name__} cannot process input of type {type(sample).__name__}")

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
            {"role": "user", "content": user_prompt},
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


def main():
    """CLI Runner cho Nghiên cứu thực nghiệm (Research Evaluation CLI)."""
    parser = argparse.ArgumentParser(
        description="VietCSharpTutor Research Evaluation Runner CLI (APT-054)"
    )
    parser.add_argument("--system", type=str, required=True, choices=["A", "B", "C", "D"], help="Hệ thống cần đánh giá: A, B, C, hoặc D")
    parser.add_argument("--split", type=str, default="dev", choices=["dev", "validation", "test"], help="Phân vùng dữ liệu: dev, validation, test")
    parser.add_argument("--model", type=str, default="gpt-4o-mini", help="Tên mô hình LLM thực tế")
    parser.add_argument("--provider", type=str, default="openai", choices=["openai", "azure"], help="Nhà cung cấp LLM thực tế (không hỗ trợ mock/fake)")
    parser.add_argument("--dataset", type=str, default=None, help="Đường dẫn file dataset")
    parser.add_argument("--output-dir", type=str, default=None, help="Thư mục xuất kết quả")
    parser.add_argument("--seed", type=int, default=42, help="Seed ngẫu nhiên")

    args = parser.parse_args()

    dataset_path = Path(args.dataset) if args.dataset else None
    output_dir = Path(args.output_dir) if args.output_dir else None

    try:
        runner = ResearchRunner(
            system=args.system,
            split=args.split,
            model=args.model,
            provider=args.provider,
            dataset_path=dataset_path,
            output_dir=output_dir,
            seed=args.seed,
        )
        result = runner.run()
        print(f"\n[HOÀN TẤT NGHIÊN CỨU] Run ID: {result['run_id']}")
        print(f"File dự đoán: {result['predictions_path']}")
        print(f"File manifest: {result['manifest_path']}")
    except ResearchProviderConfigurationError as exc:
        sys.stderr.write(f"\n[RESEARCH CONFIGURATION ERROR] {str(exc)}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
