"""
Unit Tests for Architecture Separation of Research and Testing Harness (APT-054).

Kiểm định 3 yêu cầu bắt buộc:
1. test_fake_provider_rejected_in_research_mode: Fake provider bị từ chối tuyệt đối trong Research Mode.
2. test_test_harness_still_supports_unit_tests: Test harness vẫn hỗ trợ đầy đủ việc chạy kiểm thử offline.
3. test_research_runner_has_no_mock_flag: ResearchRunner tuyệt đối không có cờ mock trong signature và manifest.
"""

import inspect
import json
import os
from pathlib import Path
import pytest

from app.evaluation.research.runner import ResearchRunner
from app.evaluation.research.provider import ResearchProvider, OpenAIResearchProvider
from app.evaluation.testing.fake_provider import (
    DeterministicFakeProvider,
    FakeTestProvider,
    LeakingFakeProvider,
)
from app.evaluation.testing.fixtures import (
    create_temp_dataset_file,
    get_clean_test_model_input,
    get_sample_test_record,
    get_test_dataset,
)


def test_research_runner_has_no_mock_flag():
    """
    Kiểm tra chắc chắn rằng ResearchRunner không có cờ mock hay mock_mode trong signature:
    - inspect.signature(ResearchRunner.__init__) không chứa 'mock'.
    - inspect.signature(ResearchRunner.__init__) không chứa 'mock_mode'.
    - Manifest tạo ra từ ResearchRunner không chứa trường 'mock_mode'.
    """
    sig = inspect.signature(ResearchRunner.__init__)
    assert "mock" not in sig.parameters, "ResearchRunner không được phép chứa tham số 'mock' trong __init__."
    assert "mock_mode" not in sig.parameters, "ResearchRunner không được phép chứa tham số 'mock_mode' trong __init__."

    # Khởi tạo runner với explicit test double để kiểm tra cấu trúc manifest
    fake_provider = DeterministicFakeProvider()
    runner = ResearchRunner(
        system="C",
        split="validation",
        provider_client=fake_provider,
        allow_test_doubles=True,
    )

    # Kiểm tra manifest không có mock_mode
    from app.evaluation.research.provenance import create_research_manifest
    manifest = create_research_manifest(
        run_id="test_run",
        system="C",
        system_description="Proposed C",
        model="gpt-4o-mini",
        provider="openai",
        prompt_version="v1.0-structured-progressive",
        dataset_path=Path("dummy.jsonl"),
        dataset_hash="dummy_hash",
        split="validation",
        split_hash="dummy_split_hash",
        total_samples=10,
        seed=42,
        execution_duration_sec=1.5,
        temperature=0.2,
    )
    assert "mock_mode" not in manifest["config"], "Research manifest config không được chứa 'mock_mode'."


def test_fake_provider_rejected_in_research_mode(tmp_path):
    """
    Kiểm tra chắc chắn rằng FakeTestProvider bị từ chối dứt khoát trong Research Mode:
    - Khi allow_test_doubles=False (mặc định), truyền FakeTestProvider phải raise TypeError.
    - Truyền provider='mock' hoặc provider='fake' phải raise ValueError.
    """
    fake_provider = DeterministicFakeProvider()

    # 1. Truyền FakeTestProvider vào ResearchRunner mà không có cờ test double
    with pytest.raises(TypeError, match="FakeTestProvider 'DeterministicFakeProvider' is strictly rejected in research evaluation mode"):
        ResearchRunner(
            system="C",
            split="validation",
            output_dir=tmp_path,
            provider_client=fake_provider,
            allow_test_doubles=False,
        )

    # 2. Truyền LeakingFakeProvider
    leaking_provider = LeakingFakeProvider()
    with pytest.raises(TypeError, match="FakeTestProvider 'LeakingFakeProvider' is strictly rejected in research evaluation mode"):
        ResearchRunner(
            system="C",
            split="validation",
            output_dir=tmp_path,
            provider_client=leaking_provider,
            allow_test_doubles=False,
        )

    # 3. Chỉ định provider="mock" hoặc "fake" trong research mode
    with pytest.raises(ValueError, match="Provider 'mock' is strictly forbidden in research evaluation"):
        ResearchRunner(
            system="C",
            split="validation",
            provider="mock",
            allow_test_doubles=False,
        )

    with pytest.raises(ValueError, match="Provider 'fake' is strictly forbidden in research evaluation"):
        ResearchRunner(
            system="C",
            split="validation",
            provider="fake",
            allow_test_doubles=False,
        )


def test_test_harness_still_supports_unit_tests(tmp_path):
    """
    Kiểm tra chắc chắn rằng khi chạy trong môi trường kiểm thử (allow_test_doubles=True hoặc CODESENSE_EVAL_TEST_ENV=1),
    harness kiểm thử với FakeTestProvider vẫn hoạt động bình thường, độc lập mạng:
    - Có thể chạy _predict_single thành công.
    - Có thể thực thi toàn bộ test dataset từ fixtures.
    - Sinh file predictions.jsonl và manifest.json hợp lệ.
    """
    # 1. Tạo dataset tạm thời từ fixtures
    test_samples = get_test_dataset(size=3, split="validation")
    dataset_file = create_temp_dataset_file(tmp_path, samples=test_samples)

    # 2. Khởi tạo fake provider với canned payload chuẩn
    fake_provider = DeterministicFakeProvider()

    out_dir = tmp_path / "test_run_output"
    runner = ResearchRunner(
        system="C",
        split="validation",
        dataset_path=dataset_file,
        output_dir=out_dir,
        seed=42,
        provider_client=fake_provider,
        allow_test_doubles=True,
    )

    # 3. Chạy đơn lẻ _predict_single
    single_pred = runner._predict_single(test_samples[0])
    assert single_pred["id"] == test_samples[0]["id"]
    assert single_pred["bug_status"] == "has_bug"
    assert single_pred["error_category"] == "logic_error"
    assert single_pred["hint_1"] is not None

    # 4. Chạy toàn bộ runner.run()
    run_result = runner.run()
    assert Path(run_result["predictions_path"]).exists()
    assert Path(run_result["manifest_path"]).exists()
    assert run_result["total_samples"] == 3

    # 5. Kiểm tra predictions ghi đúng
    with open(run_result["predictions_path"], "r", encoding="utf-8") as f:
        lines = [json.loads(line) for line in f if line.strip()]
    assert len(lines) == 3

    # 6. Kiểm tra kích hoạt qua biến môi trường CODESENSE_EVAL_TEST_ENV
    old_env = os.environ.get("CODESENSE_EVAL_TEST_ENV")
    try:
        os.environ["CODESENSE_EVAL_TEST_ENV"] = "1"
        runner_env = ResearchRunner(
            system="A",
            split="validation",
            dataset_path=dataset_file,
            output_dir=tmp_path / "env_run",
            provider_client=fake_provider,
            allow_test_doubles=False,  # phụ thuộc vào env var
        )
        assert runner_env.provider_client is fake_provider
    finally:
        if old_env is not None:
            os.environ["CODESENSE_EVAL_TEST_ENV"] = old_env
        else:
            os.environ.pop("CODESENSE_EVAL_TEST_ENV", None)


def test_research_cli_rejects_mock_and_fake_providers():
    """
    Kiểm tra chắc chắn rằng Research Evaluation CLI (scripts/run_evaluation.py)
    từ chối cờ --mock và từ chối các provider giả lập (mock/fake).
    """
    import subprocess
    import sys

    # 1. Chạy CLI với cờ --mock bị cấm
    cmd_mock = [
        sys.executable,
        "scripts/run_evaluation.py",
        "--system", "C",
        "--split", "validation",
        "--mock",
    ]
    proc = subprocess.run(
        cmd_mock,
        cwd=Path(__file__).resolve().parents[2],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    assert proc.returncode != 0
    assert "unrecognized arguments: --mock" in proc.stderr

    # 2. Chạy CLI với --provider mock
    cmd_prov_mock = [
        sys.executable,
        "scripts/run_evaluation.py",
        "--system", "C",
        "--split", "validation",
        "--provider", "mock",
    ]
    proc_prov = subprocess.run(
        cmd_prov_mock,
        cwd=Path(__file__).resolve().parents[2],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    assert proc_prov.returncode != 0
    assert "invalid choice: 'mock'" in proc_prov.stderr

