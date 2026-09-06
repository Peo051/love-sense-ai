"""
Research Evaluation Package for Clean-Room Benchmarks (APT-054 / APT-055).

Chỉ cho phép Real LLM Providers, không truy cập nhãn vàng, không có cờ mock,
không có fallback ngầm và không sinh dự đoán tất định giả lập.
Bắt buộc kiểm tra tiền thực thi (preflight validation) trước khi xử lý bất kỳ mẫu nào.
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
    ResearchProviderAuthenticationError,
    ResearchProviderConfigurationError,
    ResearchProviderError,
    ResearchProviderNetworkError,
    ResearchProviderRateLimitError,
    ResearchProviderResponseError,
    ResearchProviderSchemaError,
    ResearchProviderTimeoutError,
    ResearchRetryPolicy,
    sanitize_error_message,
    validate_research_provider,
)
from app.evaluation.research.schemas import (
    ResearchMessage,
    ResearchModelRequest,
    ResearchProviderResponse,
    ResearchUsage,
)
from app.evaluation.research.runner import ResearchFailureRecord, ResearchRunner

__all__ = [
    "ResearchRunner",
    "ResearchFailureRecord",
    "ResearchMessage",
    "ResearchUsage",
    "ResearchModelRequest",
    "ResearchProviderResponse",
    "ResearchProvider",
    "OpenAIResearchProvider",
    "ResearchRetryPolicy",
    "ResearchProviderError",
    "ResearchProviderConfigurationError",
    "ResearchProviderTimeoutError",
    "ResearchProviderNetworkError",
    "ResearchProviderAuthenticationError",
    "ResearchProviderRateLimitError",
    "ResearchProviderResponseError",
    "ResearchProviderSchemaError",
    "sanitize_error_message",
    "validate_research_provider",
    "clean_json_string",
    "parse_provider_output",
    "validate_prediction_non_gold",
    "create_research_manifest",
    "get_git_commit",
    "compute_dataset_hashes",
]
