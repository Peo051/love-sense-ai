"""
Research Evaluation Package for Clean-Room Benchmarks (APT-054).

Chỉ cho phép Real LLM Providers, không truy cập nhãn vàng, không có cờ mock,
không có fallback ngầm và không sinh dự đoán tất định giả lập.
"""

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
from app.evaluation.research.provider import (
    OpenAIResearchProvider,
    ResearchProvider,
)
from app.evaluation.research.runner import ResearchRunner

__all__ = [
    "ResearchRunner",
    "ResearchProvider",
    "OpenAIResearchProvider",
    "clean_json_string",
    "parse_provider_output",
    "validate_prediction_non_gold",
    "create_research_manifest",
    "get_git_commit",
    "compute_dataset_hashes",
]
