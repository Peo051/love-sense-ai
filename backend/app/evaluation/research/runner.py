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

from pydantic import BaseModel, ConfigDict, Field

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
    ResearchProviderError,
    ResearchProviderResponseError,
    ResearchProviderSchemaError,
    sanitize_error_message,
    validate_research_provider,
)
from app.evaluation.research.schemas import (
    ResearchMessage,
    ResearchModelRequest,
    ResearchProviderResponse,
    ResearchUsage,
)
from app.evaluation.schemas import GroundTruth, ModelInput, assert_not_ground_truth

logger = logging.getLogger(__name__)


class ResearchFailureRecord(BaseModel):
    """
    Bản ghi định kiểu chi tiết cho mẫu gặp lỗi trong nghiên cứu đánh giá (APT-056).
    Tuyệt đối không lưu trữ credentials, Authorization headers, hay toàn bộ code học sinh.
    """

    run_id: str
    sample_id: Optional[str] = None
    provider: str
    model: str
    attempts: int = 1
    failure_type: str  # "TIMEOUT", "NETWORK_ERROR", "RATE_LIMIT", "AUTHENTICATION_ERROR", "HTTP_5XX", "EMPTY_RESPONSE", "MALFORMED_RESPONSE", "SCHEMA_ERROR", "CONFIGURATION_ERROR"
    http_status: Optional[int] = None
    retryable: bool = False
    timestamp: str
    message_safe: str

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        str_strip_whitespace=True,
    )


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
        allow_partial: bool = True,
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
        self.allow_partial = allow_partial
        self.caching_enabled = False  # APT-056: cache disabled by default
        self.failures: List[ResearchFailureRecord] = []

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
        self.failures = []
        t0_total = time.time()

        for idx, sample in enumerate(samples, start=1):
            sample_id = None
            if isinstance(sample, dict):
                sample_id = sample.get("id") or sample.get("sample_id")
            elif hasattr(sample, "sample_id"):
                sample_id = sample.sample_id

            try:
                pred = self._predict_single(sample)
                predictions.append(pred)
            except ResearchProviderConfigurationError:
                # Configuration error aborts entire run immediately!
                raise
            except ResearchProviderError as exc:
                # Sample-level provider failure (APT-056)
                failure_rec = ResearchFailureRecord(
                    run_id=self.run_id,
                    sample_id=sample_id,
                    provider=self.provider,
                    model=self.model,
                    attempts=getattr(exc, "attempts", 1),
                    failure_type=getattr(exc, "failure_type", "PROVIDER_ERROR"),
                    http_status=getattr(exc, "http_status", None),
                    retryable=getattr(exc, "retryable", False),
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    message_safe=getattr(exc, "message_safe", sanitize_error_message(str(exc))),
                )
                self.failures.append(failure_rec)
                logger.warning(
                    "[SAMPLE FAILED] Mẫu %s thất bại: %s (%s). Không tạo prediction.",
                    sample_id,
                    failure_rec.failure_type,
                    failure_rec.message_safe,
                )
                if not self.allow_partial:
                    raise
            except Exception:
                # Integrity / firewall violation aborts run
                raise

            if idx % 30 == 0 or idx == len(samples):
                print(f"  Đã xử lý {idx}/{len(samples)} mẫu (thành công: {len(predictions)}, lỗi: {len(self.failures)})...")

        total_duration = time.time() - t0_total

        # 1. Ghi file predictions.jsonl (chỉ chứa các dự đoán thành công từ Real Provider)
        with open(predictions_file, "w", encoding="utf-8") as f:
            for pred in predictions:
                f.write(json.dumps(pred, ensure_ascii=False) + "\n")

        # 2. Xác định trạng thái run: COMPLETE, PARTIAL, FAILED (APT-056)
        total_samples_count = len(samples)
        successful_count = len(predictions)
        failed_count = len(self.failures)

        if failed_count == 0 and successful_count == total_samples_count:
            run_status = "COMPLETE"
        elif successful_count > 0 and failed_count > 0:
            run_status = "PARTIAL"
        else:
            run_status = "FAILED"

        # 3. Tạo artifact failure_report.json
        failure_report_file = self.output_dir / "failure_report.json"
        failure_report = {
            "run_id": self.run_id,
            "run_status": run_status,
            "total_samples": total_samples_count,
            "successful_samples": successful_count,
            "failed_samples": failed_count,
            "failures": [f.model_dump() for f in self.failures],
        }
        with open(failure_report_file, "w", encoding="utf-8") as f:
            json.dump(failure_report, f, ensure_ascii=False, indent=2)

        # 4. Tạo và ghi immutable run manifest (chứa provenance, run_status, failure_report)
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
            extra_config={
                "run_status": run_status,
                "successful_samples": successful_count,
                "failed_samples": failed_count,
                "failure_report_path": str(failure_report_file),
                "caching_enabled": self.caching_enabled,
            },
        )
        manifest["run_status"] = run_status
        manifest["successful_samples"] = successful_count
        manifest["failed_samples"] = failed_count

        with open(manifest_file, "w", encoding="utf-8") as f:
            json.dump(manifest, f, ensure_ascii=False, indent=2)

        print(f"\nĐÃ HOÀN THÀNH RUN THỰC NGHIỆM ({run_status}):")
        print(f"- Predictions: {predictions_file} ({successful_count} mẫu thành công)")
        print(f"- Failures: {failure_report_file} ({failed_count} mẫu thất bại)")
        print(f"- Manifest: {manifest_file}")

        return {
            "run_id": self.run_id,
            "run_status": run_status,
            "predictions_path": str(predictions_file),
            "manifest_path": str(manifest_file),
            "failure_report_path": str(failure_report_file),
            "total_samples": total_samples_count,
            "successful_samples": successful_count,
            "failed_samples": failed_count,
            "duration_sec": total_duration,
        }

    def _call_provider(
        self,
        request: ResearchModelRequest,
    ) -> ResearchProviderResponse:
        """Gửi ResearchModelRequest tới provider và nhận ResearchProviderResponse thực tế (APT-057)."""
        if self.provider_client is None:
            raise RuntimeError(
                f"System {self.system} cannot produce prediction without a configured LLM provider. "
                "Direct ground-truth copying has been completely removed (APT-053)."
            )

        if hasattr(self.provider_client, "generate"):
            gen = self.provider_client.generate(request)
        else:
            messages = [{"role": m.role, "content": m.content} for m in request.messages]
            gen = self.provider_client.generate_response(
                messages,
                temperature=request.temperature or 0.2,
                max_tokens=request.max_output_tokens or 1500,
            )

        if inspect.isawaitable(gen):
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = None

            if loop and loop.is_running():
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    result = executor.submit(asyncio.run, gen).result()
            else:
                result = asyncio.run(gen)
        else:
            result = gen

        if isinstance(result, ResearchProviderResponse):
            return result

        return ResearchProviderResponse(
            provider=self.provider,
            requested_model=self.model,
            returned_model=None,
            raw_text=str(result),
            request_id=None,
            provider_response_id=None,
            finish_reason=None,
            usage=None,
            provider_response_received=True,
            raw_metadata={},
            latency_ms=None,
            response_format_mode=request.response_format_mode,
        )

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

        research_messages = [
            ResearchMessage(role="system", content=system_prompt),
            ResearchMessage(role="user", content=user_prompt),
        ]

        temperature = 0.2 if self.system in ("C", "D") else 0.7
        format_mode = "json" if self.system in ("C", "D") else "text"
        model_request = ResearchModelRequest(
            run_id=self.run_id,
            sample_id=model_input.sample_id,
            system_name=self.system,
            model=self.model,
            messages=research_messages,
            temperature=temperature,
            max_output_tokens=1024,
            response_format_mode=format_mode,
        )

        # 5. Fail-Closed Firewall quét toàn bộ request trước khi gọi provider
        GroundTruthFirewall.default().inspect(
            model_request,
            sample_id=model_input.sample_id,
            run_id=self.run_id,
            base_path=f"runner.{self.system}.request",
        )

        # 6. Gọi Provider thực tế và nhận envelope ResearchProviderResponse
        t0 = time.time()
        provider_resp = self._call_provider(model_request)
        latency_ms = (
            provider_resp.latency_ms
            if provider_resp.latency_ms is not None
            else round((time.time() - t0) * 1000, 2)
        )

        raw_response = provider_resp.raw_text

        # 6.1. Từ chối phản hồi rỗng từ provider (APT-056)
        if raw_response is None or not isinstance(raw_response, str) or not raw_response.strip():
            raise ResearchProviderResponseError(
                "Empty provider response received.",
                http_status=200,
                failure_type="EMPTY_RESPONSE",
                attempts=getattr(self.provider_client, "last_attempts", 1),
            )

        # 6.2. Thu thập token usage chính thức từ provider (APT-057 - tuyệt đối không ước lượng)
        usage_dict = provider_resp.usage.model_dump() if provider_resp.usage else None
        prompt_tokens = provider_resp.usage.input_tokens if provider_resp.usage else None
        completion_tokens = provider_resp.usage.output_tokens if provider_resp.usage else None
        total_tokens = provider_resp.usage.total_tokens if provider_resp.usage else None

        # 7. Parser: Bóc tách cấu trúc từ chuỗi phản hồi thô của provider
        parsed, json_valid, parse_actions = parse_provider_output(raw_response, self.system)

        # 7.1. Hệ thống C và D bắt buộc định dạng JSON có cấu trúc (APT-056)
        if self.system in ("C", "D"):
            if not json_valid:
                raise ResearchProviderSchemaError(
                    f"System {self.system} requires structured JSON diagnosis, but provider returned unparseable text.",
                    http_status=200,
                    failure_type="MALFORMED_RESPONSE",
                    attempts=getattr(self.provider_client, "last_attempts", 1),
                )
            bug_status = parsed.get("bug_status")
            if bug_status not in ("has_bug", "no_bug", "insufficient_context"):
                raise ResearchProviderSchemaError(
                    f"System {self.system} output missing mandatory valid 'bug_status' (got '{bug_status}').",
                    http_status=200,
                    failure_type="SCHEMA_ERROR",
                    attempts=getattr(self.provider_client, "last_attempts", 1),
                )

        # 8. Non-Gold Validator: Kiểm định tính hợp lệ mà KHÔNG truy cập Ground Truth
        validated_data, validator_actions = validate_prediction_non_gold(
            parsed_data=parsed,
            model_input=model_input,
            parse_actions=parse_actions,
        )

        # 9. Đóng gói Prediction từ dữ liệu đã qua kiểm định với đầy đủ provenance (APT-056 / APT-057)
        return {
            "id": model_input.sample_id,
            "model": self.model,
            "requested_model": provider_resp.requested_model,
            "returned_model": provider_resp.returned_model,
            "provider": self.provider,
            "request_id": provider_resp.request_id,
            "provider_response_id": provider_resp.provider_response_id,
            "finish_reason": provider_resp.finish_reason,
            "provider_response_received": True,
            "prompt_version": self.prompt_version,
            "latency_ms": latency_ms,
            "usage": usage_dict,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens,
            "raw_response": raw_response,
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
    """CLI Runner cho Nghiên cứu thực nghiệm (Research Evaluation CLI) (APT-054 / APT-056 / APT-057)."""
    parser = argparse.ArgumentParser(
        description="VietCSharpTutor Research Evaluation Runner CLI (APT-054 / APT-056 / APT-057)"
    )
    parser.add_argument("--system", type=str, required=True, choices=["A", "B", "C", "D"], help="Hệ thống cần đánh giá: A, B, C, hoặc D")
    parser.add_argument("--split", type=str, default="dev", choices=["dev", "validation", "test"], help="Phân vùng dữ liệu: dev, validation, test")
    parser.add_argument("--model", type=str, default="gpt-4o-mini", help="Tên mô hình LLM thực tế")
    parser.add_argument("--provider", type=str, default="openai", choices=["openai"], help="Nhà cung cấp LLM thực tế (không hỗ trợ mock/fake)")
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
        print(f"Trạng thái run: {result['run_status']}")
        print(f"File dự đoán: {result['predictions_path']}")
        print(f"File thất bại: {result['failure_report_path']}")
        print(f"File manifest: {result['manifest_path']}")

        if result["run_status"] == "COMPLETE":
            sys.exit(0)
        elif result["run_status"] == "PARTIAL":
            sys.stderr.write(f"\n[RESEARCH RUN PARTIAL] {result['failed_samples']} mẫu gặp lỗi.\n")
            sys.exit(2)
        else:
            sys.stderr.write(f"\n[RESEARCH RUN FAILED] Toàn bộ mẫu thất bại hoặc run bị hủy.\n")
            sys.exit(1)

    except ResearchProviderConfigurationError as exc:
        sys.stderr.write(f"\n[RESEARCH CONFIGURATION ERROR] {str(exc)}\n")
        sys.exit(1)
    except Exception as exc:
        sys.stderr.write(f"\n[RESEARCH FATAL ERROR] {str(exc)}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
