"""
Unit Tests for Enforcing Real Provider Configuration in Research Evaluation (APT-055).

Kiểm định các trường hợp bắt buộc:
1. Missing API key: Không có API key ném ra ResearchProviderConfigurationError.
2. Invalid provider: Provider rỗng, mock, fake, hoặc unsupported provider ném ra ResearchProviderConfigurationError.
3. Missing model: Model rỗng hoặc mock-tutor-v1 ném ra ResearchProviderConfigurationError.
4. Fake provider: FakeTestProvider bị từ chối trong research mode.
5. Valid mocked transport around REAL provider: Cho phép mock ở tầng HTTP transport với interface provider thật.
6. CLI non-zero exit: CLI trả về exit code 1 khi cấu hình provider không hợp lệ.
"""

import json
import os
from pathlib import Path
import subprocess
import sys
import httpx
import pytest

from app.core.config import settings
from app.evaluation.research.provider import (
    OpenAIResearchProvider,
    ResearchProvider,
    ResearchProviderConfigurationError,
    validate_research_provider,
)
from app.evaluation.research.runner import ResearchRunner
from app.evaluation.testing.fake_provider import (
    DeterministicFakeProvider,
    FakeTestProvider,
    LeakingFakeProvider,
)
from app.evaluation.testing.fixtures import (
    create_temp_dataset_file,
    get_test_dataset,
)
from app.services.llm_client import OpenAICompatibleLLMClient


def test_missing_api_key(monkeypatch):
    """
    Kiểm tra chắc chắn rằng nếu không có API key hợp lệ trong môi trường:
    - validate_research_provider ném ra ResearchProviderConfigurationError.
    - ResearchRunner ném ra ResearchProviderConfigurationError ngay khi khởi tạo.
    - Thông báo lỗi không bao giờ in credential.
    """
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("AZURE_OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("CODESENSE_EVAL_TEST_ENV", raising=False)
    monkeypatch.setattr(settings, "llm_api_key", "")

    # 1. validate_research_provider trực tiếp
    with pytest.raises(ResearchProviderConfigurationError, match="Missing required credential"):
        validate_research_provider(provider="openai", model="gpt-4o-mini")

    # 2. Khởi tạo ResearchRunner
    with pytest.raises(ResearchProviderConfigurationError, match="Missing required credential"):
        ResearchRunner(
            system="C",
            split="validation",
            provider="openai",
            model="gpt-4o-mini",
            allow_test_doubles=False,
        )


def test_invalid_provider():
    """
    Kiểm tra chắc chắn rằng provider rỗng, mock, fake hoặc không được hỗ trợ
    bị từ chối ngay lập tức với ResearchProviderConfigurationError.
    """
    # 1. Provider rỗng
    with pytest.raises(ResearchProviderConfigurationError, match="Research provider must be configured"):
        validate_research_provider(provider="", model="gpt-4o-mini")

    # 2. Provider mock
    with pytest.raises(ResearchProviderConfigurationError, match="strictly forbidden in research evaluation"):
        validate_research_provider(provider="mock", model="gpt-4o-mini")

    with pytest.raises(ResearchProviderConfigurationError, match="strictly forbidden in research evaluation"):
        validate_research_provider(provider="fake", model="gpt-4o-mini")

    # 3. Provider chưa được hỗ trợ (e.g. gemini, anthropic khi chưa có provider class)
    with pytest.raises(ResearchProviderConfigurationError, match="Unsupported research provider"):
        validate_research_provider(provider="unknown_llm", model="gpt-4o-mini")


def test_missing_model():
    """
    Kiểm tra chắc chắn rằng model rỗng, None hoặc mang định danh mock
    bị từ chối ngay lập tức với ResearchProviderConfigurationError.
    """
    # 1. Model rỗng hoặc None
    with pytest.raises(ResearchProviderConfigurationError, match="Model identifier must be configured"):
        validate_research_provider(provider="openai", model="")

    with pytest.raises(ResearchProviderConfigurationError, match="Model identifier must be configured"):
        validate_research_provider(provider="openai", model=None)

    # 2. Model định danh mock
    with pytest.raises(ResearchProviderConfigurationError, match="is a mock/fake identifier"):
        validate_research_provider(provider="openai", model="mock-tutor-v1")

    with pytest.raises(ResearchProviderConfigurationError, match="is a mock/fake identifier"):
        validate_research_provider(provider="openai", model="fake")


def test_fake_provider_rejected_by_preflight():
    """
    Kiểm tra chắc chắn rằng FakeTestProvider và DeterministicMockProvider
    bị từ chối dứt khoát bởi validate_research_provider nếu không có allow_test_doubles=True.
    """
    fake_provider = DeterministicFakeProvider()

    with pytest.raises(ResearchProviderConfigurationError, match="FakeTestProvider 'DeterministicFakeProvider' is strictly rejected"):
        validate_research_provider(
            provider="openai",
            model="gpt-4o-mini",
            provider_client=fake_provider,
            allow_test_doubles=False,
        )

    leaking_provider = LeakingFakeProvider()
    with pytest.raises(ResearchProviderConfigurationError, match="FakeTestProvider 'LeakingFakeProvider' is strictly rejected"):
        validate_research_provider(
            provider="openai",
            model="gpt-4o-mini",
            provider_client=leaking_provider,
            allow_test_doubles=False,
        )


def test_valid_mocked_transport_around_real_provider_interface(tmp_path):
    """
    Yêu cầu trọng tâm của APT-055:
    Mocked HTTP transport được phép sử dụng xung quanh interface Provider THẬT (OpenAIResearchProvider)
    để phục vụ kiểm thử đơn vị độc lập mạng, NHƯNG hoàn toàn không tương đương với chế độ mock suy luận.
    - Provider là Real Provider (is_real_provider=True, is_fake_test_provider=False).
    - Toàn bộ flow: serialization -> firewall -> request -> mock transport response -> parser -> validator -> prediction hoạt động chuẩn xác.
    """
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

    mock_chat_completion = {
        "id": "chatcmpl-unit-test-123",
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

    async def mock_handler(request: httpx.Request) -> httpx.Response:
        # Kiểm tra request gửi tới đúng endpoint và header
        assert "/chat/completions" in str(request.url)
        assert "Authorization" in request.headers
        assert request.headers["Authorization"].startswith("Bearer sk-")
        return httpx.Response(200, json=mock_chat_completion)

    transport = httpx.MockTransport(mock_handler)
    client = OpenAICompatibleLLMClient(transport=transport, api_key="sk-test-transport-key-valid")
    real_provider = OpenAIResearchProvider(
        client=client,
        api_key="sk-test-transport-key-valid",
        model="gpt-4o-mini",
    )

    # 1. Xác thực đây là một Real Provider chứ không phải FakeTestProvider
    assert isinstance(real_provider, ResearchProvider)
    assert real_provider.is_real_provider is True
    assert real_provider.is_fake_test_provider is False

    # 2. validate_research_provider chấp thuận provider này trong research mode (allow_test_doubles=False)
    validated = validate_research_provider(
        provider="openai",
        model="gpt-4o-mini",
        provider_client=real_provider,
        allow_test_doubles=False,
    )
    assert validated is real_provider

    # 3. Chạy qua ResearchRunner mà không cần bật allow_test_doubles
    test_samples = get_test_dataset(size=2, split="validation")
    dataset_file = create_temp_dataset_file(tmp_path, samples=test_samples)
    out_dir = tmp_path / "real_provider_transport_run"

    runner = ResearchRunner(
        system="C",
        split="validation",
        model="gpt-4o-mini",
        provider="openai",
        provider_client=real_provider,
        dataset_path=dataset_file,
        output_dir=out_dir,
        seed=42,
        allow_test_doubles=False,  # Bắt buộc Research Mode thuần túy
    )

    result = runner.run()
    assert Path(result["predictions_path"]).exists()
    assert Path(result["manifest_path"]).exists()
    assert result["total_samples"] == 2

    # 4. Kiểm tra predictions nhận được từ real provider interface
    with open(result["predictions_path"], "r", encoding="utf-8") as f:
        preds = [json.loads(line) for line in f if line.strip()]

    assert len(preds) == 2
    for p in preds:
        assert p["bug_status"] == "has_bug"
        assert p["error_category"] == "logic_error"
        assert p["hint_1"] == "Hãy kiểm tra lại việc gán biến trong constructor."
        assert p["prompt_version"] == "v1.0-structured-progressive"


def test_research_cli_exits_nonzero_on_missing_credentials(monkeypatch):
    """
    Kiểm tra chắc chắn rằng CLI scripts/run_evaluation.py thoát với mã khác 0 (non-zero)
    khi thiếu API key hoặc cấu hình provider không hợp lệ.
    """
    env = dict(os.environ)
    env.pop("OPENAI_API_KEY", None)
    env.pop("AZURE_OPENAI_API_KEY", None)
    env.pop("CODESENSE_EVAL_TEST_ENV", None)

    cmd = [
        sys.executable,
        "scripts/run_evaluation.py",
        "--system", "C",
        "--split", "validation",
        "--provider", "openai",
        "--model", "gpt-4o-mini",
    ]
    proc = subprocess.run(
        cmd,
        cwd=Path(__file__).resolve().parents[2],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    assert proc.returncode != 0
    assert "RESEARCH CONFIGURATION ERROR" in proc.stderr
    assert "Missing required credential" in proc.stderr
