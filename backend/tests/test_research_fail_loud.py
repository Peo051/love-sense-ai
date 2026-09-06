"""
Unit Tests for Enforcing Fail-Loud Provider Errors in Research Evaluation (APT-056).

Bộ kiểm thử toàn diện bảo đảm:
1. NO VALID REAL PROVIDER RESPONSE -> NO VALID RESEARCH PREDICTION.
2. Thử lại tất định có giới hạn đối với lỗi tạm thời (transient): timeout, 429, 500.
3. Không thử lại đối với lỗi xác thực (401, 403) hay lỗi cấu hình.
4. Không bao giờ fallback sang mock, cache, heuristic, default prediction, hay GroundTruth.
5. Không bao giờ âm thầm thay thế model (model substitution) hoặc provider.
6. Ghi nhận đầy đủ ResearchFailureRecord và failure_report.json.
7. Run chứa mẫu lỗi được đánh dấu PARTIAL hoặc FAILED, không bao giờ COMPLETE.
8. CLI nghiên cứu không để lộ bất kỳ cờ test double nào.
"""

import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any, Dict, List
import httpx
import pytest

from app.core.config import settings
from app.evaluation.research.provider import (
    OpenAIResearchProvider,
    ResearchProviderAuthenticationError,
    ResearchProviderConfigurationError,
    ResearchProviderError,
    ResearchProviderNetworkError,
    ResearchProviderRateLimitError,
    ResearchProviderResponseError,
    ResearchProviderSchemaError,
    ResearchProviderTimeoutError,
    ResearchRetryPolicy,
    validate_research_provider,
)
from app.evaluation.research.runner import ResearchFailureRecord, ResearchRunner
from app.evaluation.testing.fixtures import (
    create_temp_dataset_file,
    get_test_dataset,
)


def _build_valid_c_json_response(sample_id: str = "sample-test-01") -> Dict[str, Any]:
    canned_payload = {
        "bug_status": "has_bug",
        "error_category": "logic_error",
        "bug_type": "semantic_error",
        "bug_location": {"file": "Program.cs", "start_line": 5, "end_line": 5, "symbol": "constructor"},
        "evidence": "name = name;",
        "knowledge_components": ["csharp_constructor"],
        "possible_misconception": "Nhầm lẫn giữa tham số và trường.",
        "reference_diagnosis": "Lỗi gán đè tham số trong constructor.",
        "hint_1": "Hãy kiểm tra lại việc gán biến trong constructor.",
        "hint_2": "Sử dụng từ khóa this để định danh trường dữ liệu.",
        "hint_3": "Sửa thành this.name = name;",
        "explanation_vi": "Giải thích chi tiết về từ khóa this trong C#.",
    }
    return {
        "id": f"chatcmpl-{sample_id}",
        "object": "chat.completion",
        "created": 1700000000,
        "model": "gpt-4o-mini",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": json.dumps(canned_payload, ensure_ascii=False),
                },
                "finish_reason": "stop",
            }
        ],
    }


def test_timeout_retries_then_fails(tmp_path):
    """Scenario E: Timeout mạng thử lại 3 lần rồi thất bại, ghi nhận failure_type TIMEOUT."""
    call_count = 0

    async def mock_handler(request: httpx.Request) -> httpx.Response:
        nonlocal call_count
        call_count += 1
        raise httpx.ReadTimeout("Request timed out", request=request)

    transport = httpx.MockTransport(mock_handler)
    retry_policy = ResearchRetryPolicy(max_attempts=3, base_delay_seconds=0.01)
    provider = OpenAIResearchProvider(
        transport=transport,
        api_key="sk-test-key-12345",
        model="gpt-4o-mini",
        retry_policy=retry_policy,
    )

    test_samples = get_test_dataset(size=1, split="validation")
    dataset_file = create_temp_dataset_file(tmp_path, samples=test_samples)
    out_dir = tmp_path / "timeout_run"

    runner = ResearchRunner(
        system="C",
        split="validation",
        model="gpt-4o-mini",
        provider="openai",
        provider_client=provider,
        dataset_path=dataset_file,
        output_dir=out_dir,
    )

    result = runner.run()

    # Bắt buộc đã gọi đúng 3 lần (1 gốc + 2 retries)
    assert call_count == 3
    assert result["run_status"] == "FAILED"
    assert result["total_samples"] == 1
    assert result["successful_samples"] == 0
    assert result["failed_samples"] == 1

    # File predictions phải rỗng
    with open(result["predictions_path"], "r", encoding="utf-8") as f:
        preds = [line for line in f if line.strip()]
    assert len(preds) == 0

    # File failure_report ghi nhận TIMEOUT
    with open(result["failure_report_path"], "r", encoding="utf-8") as f:
        failure_report = json.load(f)
    assert failure_report["run_status"] == "FAILED"
    assert len(failure_report["failures"]) == 1
    fail_item = failure_report["failures"][0]
    assert fail_item["failure_type"] == "TIMEOUT"
    assert fail_item["attempts"] == 3
    assert fail_item["retryable"] is True
    assert "sk-" not in fail_item["message_safe"]


def test_network_error_retries_then_fails(tmp_path):
    """Lỗi mạng (ConnectError) thử lại 3 lần rồi thất bại, ghi nhận failure_type NETWORK_ERROR."""
    call_count = 0

    async def mock_handler(request: httpx.Request) -> httpx.Response:
        nonlocal call_count
        call_count += 1
        raise httpx.ConnectError("Connection refused by peer", request=request)

    transport = httpx.MockTransport(mock_handler)
    retry_policy = ResearchRetryPolicy(max_attempts=3, base_delay_seconds=0.01)
    provider = OpenAIResearchProvider(
        transport=transport,
        api_key="sk-test-key-12345",
        model="gpt-4o-mini",
        retry_policy=retry_policy,
    )

    test_samples = get_test_dataset(size=1, split="validation")
    dataset_file = create_temp_dataset_file(tmp_path, samples=test_samples)
    out_dir = tmp_path / "network_err_run"

    runner = ResearchRunner(
        system="C",
        split="validation",
        model="gpt-4o-mini",
        provider="openai",
        provider_client=provider,
        dataset_path=dataset_file,
        output_dir=out_dir,
    )

    result = runner.run()

    assert call_count == 3
    assert result["run_status"] == "FAILED"
    assert result["successful_samples"] == 0
    assert result["failed_samples"] == 1

    with open(result["failure_report_path"], "r", encoding="utf-8") as f:
        failure_report = json.load(f)
    assert failure_report["failures"][0]["failure_type"] == "NETWORK_ERROR"
    assert failure_report["failures"][0]["attempts"] == 3


def test_rate_limit_retries_then_fails(tmp_path):
    """Lỗi HTTP 429 Rate Limit thử lại 3 lần rồi thất bại, ghi nhận failure_type RATE_LIMIT."""
    call_count = 0

    async def mock_handler(request: httpx.Request) -> httpx.Response:
        nonlocal call_count
        call_count += 1
        return httpx.Response(429, json={"error": {"message": "Rate limit reached"}})

    transport = httpx.MockTransport(mock_handler)
    retry_policy = ResearchRetryPolicy(max_attempts=3, base_delay_seconds=0.01)
    provider = OpenAIResearchProvider(
        transport=transport,
        api_key="sk-test-key-12345",
        model="gpt-4o-mini",
        retry_policy=retry_policy,
    )

    test_samples = get_test_dataset(size=1, split="validation")
    dataset_file = create_temp_dataset_file(tmp_path, samples=test_samples)
    out_dir = tmp_path / "rate_limit_run"

    runner = ResearchRunner(
        system="C",
        split="validation",
        model="gpt-4o-mini",
        provider="openai",
        provider_client=provider,
        dataset_path=dataset_file,
        output_dir=out_dir,
    )

    result = runner.run()

    assert call_count == 3
    assert result["run_status"] == "FAILED"
    with open(result["failure_report_path"], "r", encoding="utf-8") as f:
        failure_report = json.load(f)
    fail_item = failure_report["failures"][0]
    assert fail_item["failure_type"] == "RATE_LIMIT"
    assert fail_item["http_status"] == 429
    assert fail_item["attempts"] == 3


def test_500_retries_then_fails(tmp_path):
    """Scenario A: HTTP 500 thử lại 3 lần rồi thất bại, không tạo prediction."""
    call_count = 0

    async def mock_handler(request: httpx.Request) -> httpx.Response:
        nonlocal call_count
        call_count += 1
        return httpx.Response(500, json={"error": {"message": "Internal server error"}})

    transport = httpx.MockTransport(mock_handler)
    retry_policy = ResearchRetryPolicy(max_attempts=3, base_delay_seconds=0.01)
    provider = OpenAIResearchProvider(
        transport=transport,
        api_key="sk-test-key-12345",
        model="gpt-4o-mini",
        retry_policy=retry_policy,
    )

    test_samples = get_test_dataset(size=1, split="validation")
    dataset_file = create_temp_dataset_file(tmp_path, samples=test_samples)
    out_dir = tmp_path / "http500_run"

    runner = ResearchRunner(
        system="C",
        split="validation",
        model="gpt-4o-mini",
        provider="openai",
        provider_client=provider,
        dataset_path=dataset_file,
        output_dir=out_dir,
    )

    result = runner.run()

    assert call_count == 3
    assert result["run_status"] == "FAILED"
    with open(result["failure_report_path"], "r", encoding="utf-8") as f:
        failure_report = json.load(f)
    fail_item = failure_report["failures"][0]
    assert fail_item["failure_type"] == "HTTP_5XX"
    assert fail_item["http_status"] == 500
    assert fail_item["attempts"] == 3


def test_401_fails_without_retry(tmp_path):
    """Scenario C: HTTP 401 Unauthorized thất bại ngay lập tức, tuyệt đối KHÔNG retry."""
    call_count = 0

    async def mock_handler(request: httpx.Request) -> httpx.Response:
        nonlocal call_count
        call_count += 1
        return httpx.Response(401, json={"error": {"message": "Invalid API key"}})

    transport = httpx.MockTransport(mock_handler)
    retry_policy = ResearchRetryPolicy(max_attempts=3, base_delay_seconds=0.01)
    provider = OpenAIResearchProvider(
        transport=transport,
        api_key="sk-test-key-12345",
        model="gpt-4o-mini",
        retry_policy=retry_policy,
    )

    test_samples = get_test_dataset(size=1, split="validation")
    dataset_file = create_temp_dataset_file(tmp_path, samples=test_samples)
    out_dir = tmp_path / "http401_run"

    runner = ResearchRunner(
        system="C",
        split="validation",
        model="gpt-4o-mini",
        provider="openai",
        provider_client=provider,
        dataset_path=dataset_file,
        output_dir=out_dir,
    )

    result = runner.run()

    # Chỉ gọi đúng 1 lần duy nhất, không thử lại
    assert call_count == 1
    assert result["run_status"] == "FAILED"
    with open(result["failure_report_path"], "r", encoding="utf-8") as f:
        failure_report = json.load(f)
    fail_item = failure_report["failures"][0]
    assert fail_item["failure_type"] == "AUTHENTICATION_ERROR"
    assert fail_item["http_status"] == 401
    assert fail_item["attempts"] == 1
    assert fail_item["retryable"] is False


def test_403_fails_without_retry(tmp_path):
    """HTTP 403 Forbidden thất bại ngay lần đầu, không retry."""
    call_count = 0

    async def mock_handler(request: httpx.Request) -> httpx.Response:
        nonlocal call_count
        call_count += 1
        return httpx.Response(403, json={"error": {"message": "Permission denied"}})

    transport = httpx.MockTransport(mock_handler)
    retry_policy = ResearchRetryPolicy(max_attempts=3, base_delay_seconds=0.01)
    provider = OpenAIResearchProvider(
        transport=transport,
        api_key="sk-test-key-12345",
        model="gpt-4o-mini",
        retry_policy=retry_policy,
    )

    test_samples = get_test_dataset(size=1, split="validation")
    dataset_file = create_temp_dataset_file(tmp_path, samples=test_samples)
    out_dir = tmp_path / "http403_run"

    runner = ResearchRunner(
        system="C",
        split="validation",
        model="gpt-4o-mini",
        provider="openai",
        provider_client=provider,
        dataset_path=dataset_file,
        output_dir=out_dir,
    )

    result = runner.run()

    assert call_count == 1
    assert result["run_status"] == "FAILED"
    with open(result["failure_report_path"], "r", encoding="utf-8") as f:
        failure_report = json.load(f)
    fail_item = failure_report["failures"][0]
    assert fail_item["failure_type"] == "AUTHENTICATION_ERROR"
    assert fail_item["http_status"] == 403
    assert fail_item["attempts"] == 1


def test_invalid_json_never_creates_default_prediction(tmp_path):
    """Scenario D: Phản hồi văn bản tự do (prose) khi yêu cầu JSON không bao giờ sinh default prediction."""
    async def mock_handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "id": "chatcmpl-test",
                "choices": [
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": "Here is your answer: The student forgot a semicolon on line 10.",
                        },
                    }
                ],
            },
        )

    transport = httpx.MockTransport(mock_handler)
    provider = OpenAIResearchProvider(
        transport=transport,
        api_key="sk-test-key-12345",
        model="gpt-4o-mini",
    )

    test_samples = get_test_dataset(size=1, split="validation")
    dataset_file = create_temp_dataset_file(tmp_path, samples=test_samples)
    out_dir = tmp_path / "invalid_json_run"

    runner = ResearchRunner(
        system="C",
        split="validation",
        model="gpt-4o-mini",
        provider="openai",
        provider_client=provider,
        dataset_path=dataset_file,
        output_dir=out_dir,
    )

    result = runner.run()

    assert result["run_status"] == "FAILED"
    assert result["successful_samples"] == 0
    assert result["failed_samples"] == 1

    # Không có file predictions hợp lệ
    with open(result["predictions_path"], "r", encoding="utf-8") as f:
        preds = [line for line in f if line.strip()]
    assert len(preds) == 0

    with open(result["failure_report_path"], "r", encoding="utf-8") as f:
        failure_report = json.load(f)
    assert failure_report["failures"][0]["failure_type"] == "MALFORMED_RESPONSE"


def test_empty_response_never_creates_prediction(tmp_path):
    """Phản hồi rỗng hoặc chỉ chứa khoảng trắng từ provider bị từ chối, không tạo prediction."""
    async def mock_handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "id": "chatcmpl-test",
                "choices": [
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": "   \n\t  ",
                        },
                    }
                ],
            },
        )

    transport = httpx.MockTransport(mock_handler)
    provider = OpenAIResearchProvider(
        transport=transport,
        api_key="sk-test-key-12345",
        model="gpt-4o-mini",
    )

    test_samples = get_test_dataset(size=1, split="validation")
    dataset_file = create_temp_dataset_file(tmp_path, samples=test_samples)
    out_dir = tmp_path / "empty_resp_run"

    runner = ResearchRunner(
        system="C",
        split="validation",
        model="gpt-4o-mini",
        provider="openai",
        provider_client=provider,
        dataset_path=dataset_file,
        output_dir=out_dir,
    )

    result = runner.run()

    assert result["run_status"] == "FAILED"
    with open(result["failure_report_path"], "r", encoding="utf-8") as f:
        failure_report = json.load(f)
    assert failure_report["failures"][0]["failure_type"] == "EMPTY_RESPONSE"


def test_schema_invalid_response_never_creates_prediction(tmp_path):
    """JSON hợp lệ nhưng thiếu trường bắt buộc 'bug_status' bị từ chối, không tạo prediction."""
    async def mock_handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "id": "chatcmpl-test",
                "choices": [
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": json.dumps({"explanation_vi": "Không có trường bug_status"}),
                        },
                    }
                ],
            },
        )

    transport = httpx.MockTransport(mock_handler)
    provider = OpenAIResearchProvider(
        transport=transport,
        api_key="sk-test-key-12345",
        model="gpt-4o-mini",
    )

    test_samples = get_test_dataset(size=1, split="validation")
    dataset_file = create_temp_dataset_file(tmp_path, samples=test_samples)
    out_dir = tmp_path / "schema_invalid_run"

    runner = ResearchRunner(
        system="C",
        split="validation",
        model="gpt-4o-mini",
        provider="openai",
        provider_client=provider,
        dataset_path=dataset_file,
        output_dir=out_dir,
    )

    result = runner.run()

    assert result["run_status"] == "FAILED"
    with open(result["failure_report_path"], "r", encoding="utf-8") as f:
        failure_report = json.load(f)
    assert failure_report["failures"][0]["failure_type"] == "SCHEMA_ERROR"


def test_provider_failure_does_not_use_mock(tmp_path):
    """Thất bại từ provider không bao giờ kích hoạt hoặc fallback sang Fake/Mock provider."""
    async def mock_handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, json={"error": "Server error"})

    transport = httpx.MockTransport(mock_handler)
    provider = OpenAIResearchProvider(
        transport=transport,
        api_key="sk-test-key-12345",
        model="gpt-4o-mini",
        retry_policy=ResearchRetryPolicy(max_attempts=1),
    )

    test_samples = get_test_dataset(size=1, split="validation")
    dataset_file = create_temp_dataset_file(tmp_path, samples=test_samples)
    out_dir = tmp_path / "no_mock_run"

    runner = ResearchRunner(
        system="C",
        split="validation",
        model="gpt-4o-mini",
        provider="openai",
        provider_client=provider,
        dataset_path=dataset_file,
        output_dir=out_dir,
    )

    result = runner.run()

    assert result["run_status"] == "FAILED"
    # Kiểm tra không có file predictions nào được tạo với mock values
    with open(result["predictions_path"], "r", encoding="utf-8") as f:
        preds = [line for line in f if line.strip()]
    assert len(preds) == 0


def test_provider_failure_does_not_use_ground_truth(tmp_path):
    """Thất bại từ provider không bao giờ sao chép Ground Truth từ dataset."""
    async def mock_handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, json={"error": "Server error"})

    transport = httpx.MockTransport(mock_handler)
    provider = OpenAIResearchProvider(
        transport=transport,
        api_key="sk-test-key-12345",
        model="gpt-4o-mini",
        retry_policy=ResearchRetryPolicy(max_attempts=1),
    )

    test_samples = get_test_dataset(size=1, split="validation")
    gold_explanation = test_samples[0].get("explanation_vi", "")
    assert gold_explanation, "Test sample must have gold explanation"

    dataset_file = create_temp_dataset_file(tmp_path, samples=test_samples)
    out_dir = tmp_path / "no_gt_run"

    runner = ResearchRunner(
        system="C",
        split="validation",
        model="gpt-4o-mini",
        provider="openai",
        provider_client=provider,
        dataset_path=dataset_file,
        output_dir=out_dir,
    )

    result = runner.run()

    with open(result["failure_report_path"], "r", encoding="utf-8") as f:
        report_text = f.read()

    # Tuyệt đối không chứa gold explanation trong báo cáo lỗi hay prediction
    assert gold_explanation not in report_text


def test_provider_failure_does_not_use_cached_prediction(tmp_path):
    """Thất bại từ provider không bao giờ đọc hoặc tái sử dụng prediction từ cache cũ."""
    # Tạo sẵn một file cache/prediction cũ giả lập
    fake_cache_dir = tmp_path / "old_cache"
    fake_cache_dir.mkdir(parents=True, exist_ok=True)
    fake_old_pred = fake_cache_dir / "predictions.jsonl"
    fake_old_pred.write_text(
        json.dumps({"id": "sample-01", "bug_status": "has_bug", "source": "old_cached_run"}),
        encoding="utf-8",
    )

    async def mock_handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, json={"error": "Server error"})

    transport = httpx.MockTransport(mock_handler)
    provider = OpenAIResearchProvider(
        transport=transport,
        api_key="sk-test-key-12345",
        model="gpt-4o-mini",
        retry_policy=ResearchRetryPolicy(max_attempts=1),
    )

    test_samples = get_test_dataset(size=1, split="validation")
    dataset_file = create_temp_dataset_file(tmp_path, samples=test_samples)
    out_dir = tmp_path / "no_cache_run"

    runner = ResearchRunner(
        system="C",
        split="validation",
        model="gpt-4o-mini",
        provider="openai",
        provider_client=provider,
        dataset_path=dataset_file,
        output_dir=out_dir,
    )

    result = runner.run()

    assert result["run_status"] == "FAILED"
    with open(result["predictions_path"], "r", encoding="utf-8") as f:
        content = f.read()
    assert "old_cached_run" not in content


def test_provider_failure_does_not_switch_model(tmp_path):
    """Scenario G: Khi model gpt-4o thất bại, tuyệt đối không ngầm chuyển sang gpt-4o-mini hay model khác."""
    requested_model = "gpt-4o"
    observed_models: List[str] = []

    async def mock_handler(request: httpx.Request) -> httpx.Response:
        body = json.loads(request.content)
        observed_models.append(body.get("model"))
        return httpx.Response(500, json={"error": "Model overloaded"})

    transport = httpx.MockTransport(mock_handler)
    provider = OpenAIResearchProvider(
        transport=transport,
        api_key="sk-test-key-12345",
        model=requested_model,
        retry_policy=ResearchRetryPolicy(max_attempts=3, base_delay_seconds=0.01),
    )

    test_samples = get_test_dataset(size=1, split="validation")
    dataset_file = create_temp_dataset_file(tmp_path, samples=test_samples)
    out_dir = tmp_path / "no_model_switch_run"

    runner = ResearchRunner(
        system="C",
        split="validation",
        model=requested_model,
        provider="openai",
        provider_client=provider,
        dataset_path=dataset_file,
        output_dir=out_dir,
    )

    runner.run()

    # Tất cả 3 lần gọi mạng đều phải giữ nguyên requested_model
    assert len(observed_models) == 3
    for m in observed_models:
        assert m == requested_model


def test_provider_failure_does_not_switch_provider(tmp_path):
    """Scenario F: Khi provider 'openai' thất bại, tuyệt đối không đổi sang provider khác."""
    async def mock_handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(503, json={"error": "Service unavailable"})

    transport = httpx.MockTransport(mock_handler)
    provider = OpenAIResearchProvider(
        transport=transport,
        api_key="sk-test-key-12345",
        model="gpt-4o-mini",
        retry_policy=ResearchRetryPolicy(max_attempts=1),
    )

    test_samples = get_test_dataset(size=1, split="validation")
    dataset_file = create_temp_dataset_file(tmp_path, samples=test_samples)
    out_dir = tmp_path / "no_provider_switch_run"

    runner = ResearchRunner(
        system="C",
        split="validation",
        model="gpt-4o-mini",
        provider="openai",
        provider_client=provider,
        dataset_path=dataset_file,
        output_dir=out_dir,
    )

    result = runner.run()

    assert runner.provider == "openai"
    with open(result["manifest_path"], "r", encoding="utf-8") as f:
        manifest = json.load(f)
    assert manifest["provider"] == "openai"


def test_failed_sample_is_recorded(tmp_path):
    """Mẫu gặp sự cố được ghi nhận vào failure_report.json với đầy đủ thông tin định kiểu và an toàn."""
    async def mock_handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(504, json={"error": "Gateway timeout"})

    transport = httpx.MockTransport(mock_handler)
    provider = OpenAIResearchProvider(
        transport=transport,
        api_key="sk-test-secret-key-9999",
        model="gpt-4o-mini",
        retry_policy=ResearchRetryPolicy(max_attempts=2, base_delay_seconds=0.01),
    )

    test_samples = get_test_dataset(size=1, split="validation")
    sample_id = test_samples[0]["id"]
    dataset_file = create_temp_dataset_file(tmp_path, samples=test_samples)
    out_dir = tmp_path / "failed_sample_record_run"

    runner = ResearchRunner(
        system="C",
        split="validation",
        model="gpt-4o-mini",
        provider="openai",
        provider_client=provider,
        dataset_path=dataset_file,
        output_dir=out_dir,
    )

    result = runner.run()

    with open(result["failure_report_path"], "r", encoding="utf-8") as f:
        report = json.load(f)

    assert report["run_status"] == "FAILED"
    assert len(report["failures"]) == 1
    fail = report["failures"][0]
    assert fail["sample_id"] == sample_id
    assert fail["provider"] == "openai"
    assert fail["model"] == "gpt-4o-mini"
    assert fail["attempts"] == 2
    assert fail["failure_type"] == "HTTP_5XX"
    assert fail["http_status"] == 504
    assert "sk-test-secret-key" not in fail["message_safe"]


def test_partial_run_not_marked_complete(tmp_path):
    """Run có 1 mẫu thành công và 1 mẫu lỗi phải có trạng thái PARTIAL, tuyệt đối KHÔNG là COMPLETE."""
    request_index = 0

    async def mock_handler(request: httpx.Request) -> httpx.Response:
        nonlocal request_index
        request_index += 1
        if request_index == 1:
            # Mẫu 1 thành công
            return httpx.Response(200, json=_build_valid_c_json_response("sample-01"))
        else:
            # Mẫu 2 lỗi 500
            return httpx.Response(500, json={"error": "Server error"})

    transport = httpx.MockTransport(mock_handler)
    provider = OpenAIResearchProvider(
        transport=transport,
        api_key="sk-test-key-12345",
        model="gpt-4o-mini",
        retry_policy=ResearchRetryPolicy(max_attempts=1),
    )

    test_samples = get_test_dataset(size=2, split="validation")
    dataset_file = create_temp_dataset_file(tmp_path, samples=test_samples)
    out_dir = tmp_path / "partial_run"

    runner = ResearchRunner(
        system="C",
        split="validation",
        model="gpt-4o-mini",
        provider="openai",
        provider_client=provider,
        dataset_path=dataset_file,
        output_dir=out_dir,
    )

    result = runner.run()

    # Trạng thái BẮT BUỘC là PARTIAL
    assert result["run_status"] == "PARTIAL"
    assert result["run_status"] != "COMPLETE"
    assert result["total_samples"] == 2
    assert result["successful_samples"] == 1
    assert result["failed_samples"] == 1

    # File predictions có đúng 1 mẫu thành công
    with open(result["predictions_path"], "r", encoding="utf-8") as f:
        preds = [json.loads(line) for line in f if line.strip()]
    assert len(preds) == 1
    assert preds[0]["provider_response_received"] is True

    # File failure_report có đúng 1 mẫu thất bại
    with open(result["failure_report_path"], "r", encoding="utf-8") as f:
        report = json.load(f)
    assert report["run_status"] == "PARTIAL"
    assert len(report["failures"]) == 1

    # Manifest phản ánh đúng trạng thái
    with open(result["manifest_path"], "r", encoding="utf-8") as f:
        manifest = json.load(f)
    assert manifest["run_status"] == "PARTIAL"


def test_configuration_failure_aborts_run(monkeypatch, tmp_path):
    """Lỗi cấu hình (thiếu API key) ném ResearchProviderConfigurationError và hủy toàn bộ run."""
    from app.core.config import settings

    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("AZURE_OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("CODESENSE_EVAL_TEST_ENV", raising=False)
    monkeypatch.setattr(settings, "llm_api_key", "")

    with pytest.raises(ResearchProviderConfigurationError):
        ResearchRunner(
            system="C",
            split="validation",
            model="gpt-4o-mini",
            provider="openai",
            provider_client=None,
        )


def test_research_cli_exposes_no_test_double_flag():
    """Kiểm tra CLI scripts/run_evaluation.py tuyệt đối không chấp nhận các cờ test double."""
    cli_path = Path(__file__).resolve().parents[2] / "scripts" / "run_evaluation.py"
    repo_root = Path(__file__).resolve().parents[2]

    for flag in ["--allow-test-doubles", "--mock", "--fake"]:
        cmd = [
            sys.executable,
            str(cli_path),
            "--system", "C",
            "--split", "validation",
            flag,
        ]
        proc = subprocess.run(
            cmd,
            cwd=repo_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        assert proc.returncode != 0
        assert "unrecognized arguments" in proc.stderr or "error" in proc.stderr.lower()


def test_scenario_b_rate_limit_then_success(tmp_path):
    """Scenario B: Lần 1 bị 429, lần 2 trả 200 thành công -> 1 retry, prediction hợp lệ, attempts=2."""
    call_count = 0

    async def mock_handler(request: httpx.Request) -> httpx.Response:
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return httpx.Response(429, json={"error": "Rate limit exceeded"})
        return httpx.Response(200, json=_build_valid_c_json_response("sample-b-01"))

    transport = httpx.MockTransport(mock_handler)
    provider = OpenAIResearchProvider(
        transport=transport,
        api_key="sk-test-key-12345",
        model="gpt-4o-mini",
        retry_policy=ResearchRetryPolicy(max_attempts=3, base_delay_seconds=0.01),
    )

    test_samples = get_test_dataset(size=1, split="validation")
    dataset_file = create_temp_dataset_file(tmp_path, samples=test_samples)
    out_dir = tmp_path / "scenario_b_run"

    runner = ResearchRunner(
        system="C",
        split="validation",
        model="gpt-4o-mini",
        provider="openai",
        provider_client=provider,
        dataset_path=dataset_file,
        output_dir=out_dir,
    )

    result = runner.run()

    assert call_count == 2
    assert result["run_status"] == "COMPLETE"
    assert result["successful_samples"] == 1
    assert result["failed_samples"] == 0

    with open(result["predictions_path"], "r", encoding="utf-8") as f:
        preds = [json.loads(line) for line in f if line.strip()]
    assert len(preds) == 1
    assert preds[0]["bug_status"] == "has_bug"
    assert preds[0]["provider_response_received"] is True
    assert provider.last_attempts == 2
