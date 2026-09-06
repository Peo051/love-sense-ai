"""
Research LLM Provider Interface, Implementations & Preflight Validation (APT-054 / APT-055).

QUY TẮC NGHIÊN CỨU (RESEARCH RULES):
- Real provider only (bắt buộc kết nối mạng tới LLM thực tế).
- Không có quyền truy cập nhãn vàng (no ground truth access).
- Không được phép sử dụng mock, fake hay synthetic response trong research mode.
- Không có cơ chế silent fallback.
- Bắt buộc kiểm tra tiền thực thi (Preflight validation): Kiểm tra provider, model, API key trước khi xử lý.
- Tuyệt đối KHÔNG in hoặc ghi log API key/secrets ra màn hình hoặc manifest.
"""

from abc import ABC, abstractmethod
import logging
import os
from typing import Any, Dict, List, Optional

from app.core.config import settings
from app.evaluation.firewall import GroundTruthFirewall
from app.evaluation.schemas import assert_not_ground_truth
from app.services.llm_client import LLMClientError, OpenAICompatibleLLMClient

logger = logging.getLogger(__name__)


class ResearchProviderConfigurationError(TypeError, ValueError):
    """
    Ngoại lệ ném ra khi cấu hình LLM Provider phục vụ nghiên cứu không hợp lệ,
    thiếu thông tin xác thực (API key), hoặc cố tình sử dụng fake/mock provider trong research mode.
    Kế thừa TypeError và ValueError để đảm bảo tính tương thích hồi quy hoàn hảo.
    """
    pass


class ResearchProvider(ABC):
    """
    Interface bắt buộc cho mọi Provider phục vụ nghiên cứu thực nghiệm khoa học.
    Bất kỳ provider nào kế thừa interface này đều được coi là một Real Provider.
    """

    @property
    def is_real_provider(self) -> bool:
        return True

    @property
    def is_fake_test_provider(self) -> bool:
        return False

    @abstractmethod
    async def generate_response(
        self,
        messages: List[Dict[str, Any]],
        *,
        temperature: float = 0.2,
        max_tokens: int = 1500,
    ) -> str:
        """Gửi prompt tới LLM thực tế và nhận phản hồi thô."""
        pass


class OpenAIResearchProvider(ResearchProvider):
    """
    Triển khai ResearchProvider dựa trên OpenAI-compatible API.
    Tuyệt đối không hỗ trợ mock hay canned responses.
    """

    def __init__(
        self,
        client: Optional[OpenAICompatibleLLMClient] = None,
        *,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        transport: Optional[Any] = None,
    ):
        self._api_key = api_key
        self._base_url = base_url
        self._model = model
        if client is not None:
            self._client = client
        else:
            self._client = OpenAICompatibleLLMClient(
                transport=transport,
                api_key=api_key,
                base_url=base_url,
            )

    @property
    def api_key(self) -> Optional[str]:
        return self._api_key or getattr(self._client, "_api_key", None)

    async def generate_response(
        self,
        messages: List[Dict[str, Any]],
        *,
        temperature: float = 0.2,
        max_tokens: int = 1500,
    ) -> str:
        # 1. Fail-closed Firewall quét toàn bộ messages
        GroundTruthFirewall.default().inspect(messages, base_path="research_provider.messages")

        # 2. Kiểm tra type-level không có GroundTruth
        assert_not_ground_truth(messages)
        for msg in messages:
            assert_not_ground_truth(msg)
            if isinstance(msg, dict):
                assert_not_ground_truth(msg.get("content"))

        # 3. Lệnh gọi mạng thực tế tới LLM
        try:
            return await self._client.chat_completion(
                messages=messages,
                model=self._model,
                temperature=temperature,
                max_tokens=max_tokens,
            )
        except LLMClientError as exc:
            logger.error("Lỗi LLM client trong ResearchProvider: %s", str(exc))
            raise RuntimeError(f"Research evaluation LLM call failed: {str(exc)}") from exc
        except Exception as exc:
            logger.error("Lỗi không lường trước trong ResearchProvider: %s", str(exc))
            raise RuntimeError(f"Unexpected error during research inference: {str(exc)}") from exc


def validate_research_provider(
    provider: Optional[str] = None,
    model: Optional[str] = None,
    provider_client: Optional[Any] = None,
    *,
    api_key: Optional[str] = None,
    allow_test_doubles: bool = False,
) -> Any:
    """
    Hàm kiểm tra preflight bắt buộc trước khi thực thi nghiên cứu đánh giá (APT-055).

    QUY TẮC BẮT BUỘC:
    1. Provider configured: Không được rỗng, không phải mock/fake, phải là real provider ('openai', 'azure').
    2. Model configured: Không được rỗng, không phải mock/fake identifier ('mock-tutor-v1', v.v.).
    3. Research mode enabled: Từ chối dứt khoát FakeTestProvider trừ khi có allow_test_doubles=True.
    4. Required credential present: Phải có API key hợp lệ cho provider thực tế.
       TUYỆT ĐỐI KHÔNG in hoặc ghi log API key ra màn hình hoặc manifest.
    5. Provider client initialized: Đảm bảo client đã sẵn sàng phục vụ suy luận thực tế.

    Ném ra ResearchProviderConfigurationError nếu có bất kỳ vi phạm nào.
    """
    is_test_env = allow_test_doubles or os.environ.get("CODESENSE_EVAL_TEST_ENV") == "1"

    # 1. Kiểm tra Provider
    if not provider or not isinstance(provider, str) or not provider.strip():
        raise ResearchProviderConfigurationError("Research provider must be configured and cannot be empty.")

    norm_provider = provider.strip().lower()
    if not is_test_env:
        if norm_provider in ("mock", "fake"):
            raise ResearchProviderConfigurationError(
                f"Provider '{provider}' is strictly forbidden in research evaluation. "
                "Mock and fake providers are strictly prohibited in research mode (e.g., 'openai', 'azure' required)."
            )

        if norm_provider not in ("openai", "azure"):
            raise ResearchProviderConfigurationError(
                f"Unsupported research provider '{provider}'. Supported real providers are: 'openai', 'azure'."
            )

    # 2. Kiểm tra Model
    if not model or not isinstance(model, str) or not model.strip():
        raise ResearchProviderConfigurationError("Model identifier must be configured and cannot be empty.")

    norm_model = model.strip().lower()
    if not is_test_env:
        if norm_model in ("mock", "mock-tutor-v1", "fake", "canned"):
            raise ResearchProviderConfigurationError(
                f"Model identifier '{model}' is a mock/fake identifier. Research evaluation requires a valid real model identifier (e.g., 'gpt-4o', 'gpt-4o-mini')."
            )

    # 3. Kiểm tra Fake / Test Double
    if provider_client is not None:
        is_fake = (
            getattr(provider_client, "is_fake_test_provider", False)
            or not getattr(provider_client, "is_real_provider", True)
            or provider_client.__class__.__name__.startswith(("Fake", "DeterministicMock", "LeakingFake", "IndependentMock"))
        )
        if is_fake:
            if not is_test_env:
                raise ResearchProviderConfigurationError(
                    f"FakeTestProvider '{provider_client.__class__.__name__}' is strictly rejected in research evaluation mode. Research evaluation requires a real LLM provider (ResearchProvider)."
                )
            return provider_client

        if not getattr(provider_client, "is_real_provider", False):
            raise ResearchProviderConfigurationError(
                f"Provider client '{provider_client.__class__.__name__}' does not conform to ResearchProvider interface."
            )

    # 4. Kiểm tra Credential (chỉ khi không trong test environment)
    if not is_test_env:
        resolved_key = (
            api_key
            or getattr(provider_client, "api_key", None)
            or getattr(provider_client, "_api_key", None)
            or getattr(getattr(provider_client, "_client", None), "_api_key", None)
            or (os.environ.get("OPENAI_API_KEY") if norm_provider == "openai" else None)
            or (os.environ.get("AZURE_OPENAI_API_KEY") if norm_provider == "azure" else None)
            or (settings.llm_api_key if settings.llm_api_key and settings.llm_api_key.strip() else None)
        )

        if not resolved_key or not str(resolved_key).strip():
            raise ResearchProviderConfigurationError(
                f"Missing required credential: No API key configured for research provider '{provider}'. "
                f"Please set OPENAI_API_KEY or LLM_API_KEY in your environment."
            )

        if provider_client is None:
            provider_client = OpenAIResearchProvider(api_key=resolved_key, model=model)

    return provider_client
