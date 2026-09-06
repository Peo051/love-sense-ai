"""
Testing Harness Package for Evaluation Components (APT-054).

Cung cấp Test Doubles, Mocks và Fixtures phục vụ kiểm thử đơn vị.
TUYỆT ĐỐI KHÔNG SỬ DỤNG TRONG RESEARCH EVALUATION RUNNER.
"""

from app.evaluation.testing.fake_provider import (
    DeterministicFakeProvider,
    FakeTestProvider,
    LeakingFakeProvider,
)
from app.evaluation.testing.fixtures import (
    create_temp_dataset_file,
    get_clean_test_ground_truth,
    get_clean_test_model_input,
    get_sample_test_record,
    get_test_dataset,
)

__all__ = [
    "FakeTestProvider",
    "DeterministicFakeProvider",
    "LeakingFakeProvider",
    "get_sample_test_record",
    "get_clean_test_model_input",
    "get_clean_test_ground_truth",
    "get_test_dataset",
    "create_temp_dataset_file",
]
