"""
Evaluation Runner cho VietCSharpTutor (APT-028 / APT-053 / APT-054).

Module này duy trì lớp tương thích ngược (Backward Compatibility) EvaluationRunner,
đồng thời định tuyến toàn bộ logic nghiên cứu Clean-Room tới:
- app.evaluation.research (ResearchRunner, ResearchProvider, Clean-Room Parser)
- app.evaluation.testing (FakeTestProvider, Deterministic Test Fixtures)
"""

import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional

from app.evaluation.research.parser import (
    clean_json_string,
    parse_provider_output,
    validate_prediction_non_gold,
)
from app.evaluation.research.provenance import (
    compute_dataset_hashes,
    create_research_manifest,
    get_git_commit,
)
from app.evaluation.research.runner import ResearchRunner

logger = logging.getLogger(__name__)


class EvaluationRunner(ResearchRunner):
    """
    Runner đánh giá duy trì khả năng tương thích ngược (Backward Compatible).
    Kế thừa trực tiếp từ ResearchRunner nhưng cho phép cờ mock và test doubles
    trong môi trường kiểm thử đơn vị.
    """

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
        *,
        allow_test_doubles: bool = False,
    ):
        # Tự động kích hoạt allow_test_doubles nếu phát hiện cờ mock hoặc test double provider
        if mock:
            allow_test_doubles = True
        if provider in ("mock", "fake"):
            allow_test_doubles = True
        if provider_client is not None and (
            getattr(provider_client, "is_fake_test_provider", False)
            or not getattr(provider_client, "is_real_provider", True)
            or provider_client.__class__.__name__.startswith("Fake")
            or provider_client.__class__.__name__.startswith("DeterministicMock")
            or provider_client.__class__.__name__.startswith("IndependentMock")
        ):
            allow_test_doubles = True

        super().__init__(
            system=system,
            split=split,
            model=model,
            provider=provider,
            dataset_path=dataset_path,
            output_dir=output_dir,
            seed=seed,
            provider_client=provider_client,
            student_context=student_context,
            allow_test_doubles=allow_test_doubles,
        )
        self.mock = mock


__all__ = [
    "EvaluationRunner",
    "ResearchRunner",
    "clean_json_string",
    "parse_provider_output",
    "validate_prediction_non_gold",
    "get_git_commit",
    "compute_dataset_hashes",
    "create_research_manifest",
]
