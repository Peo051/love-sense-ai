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
import asyncio
import logging
import os
import re
import time
from typing import Any, Dict, List, Optional

import httpx

from app.core.config import settings
from app.evaluation.firewall import GroundTruthFirewall
from app.evaluation.research.schemas import (
    ResearchMessage,
    ResearchModelRequest,
    ResearchProviderResponse,
    ResearchUsage,
)
from app.evaluation.schemas import assert_not_ground_truth
from app.services.llm_client import LLMClientError, OpenAICompatibleLLMClient

logger = logging.getLogger(__name__)


def sanitize_error_message(message: str) -> str:
    """Loại bỏ credentials, Authorization header, mã học sinh, sentinels khỏi log lỗi."""
    if not message:
        return ""
    # Redact Bearer tokens & OpenAI keys
    cleaned = re.sub(r"(Bearer\s+)[A-Za-z0-9_\-\.]+", r"\1[REDACTED]", message, flags=re.IGNORECASE)
    cleaned = re.sub(r"sk-[A-Za-z0-9_\-]{8,}", "sk-[REDACTED]", cleaned)
    cleaned = re.sub(r"(api[_-]?key[:=]\s*)[^\s,;&]+", r"\1[REDACTED]", cleaned, flags=re.IGNORECASE)
    # Redact GroundTruth sentinel if present
    cleaned = cleaned.replace("SENTINEL_71F2_GROUND_TRUTH_DO_NOT_LEAK", "[GROUND_TRUTH_REDACTED]")
    return cleaned


class ResearchProviderError(Exception):
    """
    Lớp ngoại lệ cơ sở cho mọi lỗi xảy ra ở tầng Real Research Provider (APT-056).
    Đảm bảo phân biệt rạch ròi giữa lỗi cấu hình, transport, provider, và schema response.
    """

    def __init__(
        self,
        message: str,
        *,
        retryable: bool = False,
        http_status: Optional[int] = None,
        sample_id: Optional[str] = None,
        attempts: int = 1,
        failure_type: str = "PROVIDER_ERROR",
        message_safe: Optional[str] = None,
    ):
        super().__init__(message)
        self.retryable = retryable
        self.http_status = http_status
        self.sample_id = sample_id
        self.attempts = attempts
        self.failure_type = failure_type
        self.message_safe = message_safe or sanitize_error_message(message)


class ResearchProviderConfigurationError(ResearchProviderError, TypeError, ValueError):
    """
    Lỗi cấu hình LLM Provider phục vụ nghiên cứu (thiếu API key, provider fake/mock, model rỗng).
    Kế thừa TypeError và ValueError để đảm bảo tính tương thích hồi quy hoàn hảo với APT-054/055.
    Không retryable. Dẫn đến dừng toàn bộ run nghiên cứu.
    """

    def __init__(self, message: str):
        super().__init__(
            message,
            retryable=False,
            http_status=None,
            failure_type="CONFIGURATION_ERROR",
            attempts=0,
        )


class ResearchProviderTimeoutError(ResearchProviderError):
    """Timeout mạng hoặc timeout chờ phản hồi từ LLM provider. Cho phép retry."""

    def __init__(
        self,
        message: str = "Research provider timed out",
        *,
        http_status: Optional[int] = 408,
        attempts: int = 1,
    ):
        super().__init__(
            message,
            retryable=True,
            http_status=http_status,
            failure_type="TIMEOUT",
            attempts=attempts,
        )


class ResearchProviderNetworkError(ResearchProviderError):
    """Lỗi kết nối transport, DNS, TLS, reset/refuse. Cho phép retry."""

    def __init__(
        self,
        message: str = "Research provider network transport error",
        *,
        http_status: Optional[int] = None,
        attempts: int = 1,
    ):
        super().__init__(
            message,
            retryable=True,
            http_status=http_status,
            failure_type="NETWORK_ERROR",
            attempts=attempts,
        )


class ResearchProviderAuthenticationError(ResearchProviderError):
    """Lỗi 401 Unauthorized / 403 Forbidden. Tuyệt đối KHÔNG retry. Dừng ngay."""

    def __init__(
        self,
        message: str = "Research provider authentication failed (401/403)",
        *,
        http_status: int = 401,
        attempts: int = 1,
    ):
        super().__init__(
            message,
            retryable=False,
            http_status=http_status,
            failure_type="AUTHENTICATION_ERROR",
            attempts=attempts,
        )


class ResearchProviderRateLimitError(ResearchProviderError):
    """Lỗi HTTP 429 Rate Limit. Cho phép retry với bounded exponential backoff."""

    def __init__(
        self,
        message: str = "Research provider rate limited (HTTP 429)",
        *,
        http_status: int = 429,
        attempts: int = 1,
    ):
        super().__init__(
            message,
            retryable=True,
            http_status=http_status,
            failure_type="RATE_LIMIT",
            attempts=attempts,
        )


class ResearchProviderResponseError(ResearchProviderError):
    """Lỗi HTTP 5xx, nội dung phản hồi rỗng, hoặc HTTP error payload từ provider."""

    def __init__(
        self,
        message: str = "Research provider response error",
        *,
        retryable: bool = False,
        http_status: Optional[int] = None,
        failure_type: str = "RESPONSE_ERROR",
        attempts: int = 1,
    ):
        super().__init__(
            message,
            retryable=retryable,
            http_status=http_status,
            failure_type=failure_type,
            attempts=attempts,
        )


class ResearchProviderSchemaError(ResearchProviderError):
    """Mô hình trả JSON sai cấu trúc hoặc không parse được khi bắt buộc cấu trúc. Không fallback sang default prediction."""

    def __init__(
        self,
        message: str = "Research provider returned malformed or invalid schema response",
        *,
        retryable: bool = False,
        http_status: Optional[int] = None,
        failure_type: str = "SCHEMA_ERROR",
        attempts: int = 1,
    ):
        super().__init__(
            message,
            retryable=retryable,
            http_status=http_status,
            failure_type=failure_type,
            attempts=attempts,
        )


class ResearchRetryPolicy:
    """
    Chính sách thử lại tất định và có giới hạn cho Research Evaluation (APT-056).
    Chỉ retry đối với các lỗi tạm thời (transient errors):
    - Timeout (408 hoặc network timeout)
    - Rate limit (429)
    - 5xx server errors (500, 502, 503, 504)
    - Network/connection errors
    Tuyệt đối KHÔNG retry đối với:
    - 401 Unauthorized, 403 Forbidden
    - 400 Bad Request, 404 Not Found
    - Lỗi cấu hình (missing API key, invalid provider/model)
    - Vi phạm Ground Truth firewall
    - Response rỗng hoặc sai schema
    """

    def __init__(
        self,
        max_attempts: int = 3,
        base_delay_seconds: float = 0.1,
        backoff_factor: float = 2.0,
        max_delay_seconds: float = 5.0,
    ):
        self.max_attempts = max(1, max_attempts)
        self.base_delay_seconds = max(0.0, base_delay_seconds)
        self.backoff_factor = max(1.0, backoff_factor)
        self.max_delay_seconds = max(0.0, max_delay_seconds)

    def is_retryable_status(self, status_code: Optional[int]) -> bool:
        if status_code is None:
            return False
        return status_code in (408, 429, 500, 502, 503, 504)

    def get_delay_seconds(self, attempt_index: int) -> float:
        delay = self.base_delay_seconds * (self.backoff_factor ** attempt_index)
        return min(delay, self.max_delay_seconds)


class ResearchProvider(ABC):
    """
    Interface bắt buộc cho mọi Provider phục vụ nghiên cứu thực nghiệm khoa học (APT-057).
    Bất kỳ provider nào kế thừa interface này đều được coi là một Real Provider.
    """

    @property
    def is_real_provider(self) -> bool:
        return True

    @property
    def is_fake_test_provider(self) -> bool:
        return False

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Tên định danh chuẩn tắc của provider (ví dụ: 'openai')."""
        pass

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Định danh mô hình được cấu hình bất biến cho run."""
        pass

    @abstractmethod
    async def generate(
        self,
        request: ResearchModelRequest,
    ) -> ResearchProviderResponse:
        """
        Gửi yêu cầu đã được thẩm định tới LLM thực tế và nhận phản hồi envelope bảo toàn.
        """
        pass

    async def generate_response(
        self,
        messages: List[Dict[str, Any]],
        *,
        temperature: float = 0.2,
        max_tokens: int = 1500,
    ) -> str:
        """
        Cơ chế tương thích ngược (backwards-compatible) cho các caller truyền thống.
        Chuyển tiếp qua generate() sau khi bọc vào ResearchModelRequest.
        """
        # 1. Fail-closed Firewall quét toàn bộ messages
        GroundTruthFirewall.default().inspect(messages, base_path="research_provider.messages")

        # 2. Kiểm tra type-level không có GroundTruth
        assert_not_ground_truth(messages)
        for msg in messages:
            assert_not_ground_truth(msg)
            if isinstance(msg, dict):
                assert_not_ground_truth(msg.get("content"))

        typed_msgs: List[ResearchMessage] = []
        for m in messages:
            if isinstance(m, ResearchMessage):
                typed_msgs.append(m)
            elif isinstance(m, dict):
                role = str(m.get("role") or "user")
                if role not in ("system", "user", "assistant"):
                    role = "user"
                content = str(m.get("content") or "")
                typed_msgs.append(ResearchMessage(role=role, content=content))
            else:
                typed_msgs.append(ResearchMessage(role="user", content=str(m)))

        req = ResearchModelRequest(
            run_id="compat_run",
            sample_id="compat_sample",
            system_name="COMPAT",
            model=self.model_name,
            messages=typed_msgs,
            temperature=temperature,
            max_output_tokens=max_tokens,
            response_format_mode="text",
        )
        resp = await self.generate(req)
        return resp.raw_text


class OpenAIResearchProvider(ResearchProvider):
    """
    Triển khai ResearchProvider dựa trên OpenAI-compatible API với Fail-Loud Provider Error Policy (APT-056 / APT-057).
    Tuyệt đối không hỗ trợ mock hay canned responses.
    Thực thi bounded deterministic retries cho các lỗi transient và dừng ngay lập tức khi gặp fatal errors.
    """

    def __init__(
        self,
        client: Optional[OpenAICompatibleLLMClient] = None,
        *,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        transport: Optional[Any] = None,
        retry_policy: Optional[ResearchRetryPolicy] = None,
    ):
        self._api_key = api_key
        self._base_url = base_url
        self._model = model
        self._transport = transport
        if client is not None:
            self._client = client
            if self._transport is None:
                self._transport = getattr(client, "_transport", None)
            if self._api_key is None:
                self._api_key = getattr(client, "_api_key", None)
            if self._base_url is None:
                self._base_url = getattr(client, "_base_url", None)
        else:
            self._client = OpenAICompatibleLLMClient(
                transport=self._transport,
                api_key=self._api_key,
                base_url=self._base_url,
            )
        self.retry_policy = retry_policy or ResearchRetryPolicy()
        self.last_attempts: int = 0

    @property
    def provider_name(self) -> str:
        return "openai"

    @property
    def model_name(self) -> str:
        return self._model or "gpt-4o-mini"

    @property
    def api_key(self) -> Optional[str]:
        return self._api_key or getattr(self._client, "_api_key", None)

    @property
    def model(self) -> Optional[str]:
        return self._model

    def _get_api_key(self) -> str:
        return (
            self._api_key
            or getattr(self._client, "_api_key", None)
            or os.environ.get("OPENAI_API_KEY")
            or settings.llm_api_key
            or ""
        )

    def _get_base_url(self) -> str:
        url = (
            self._base_url
            or getattr(self._client, "_base_url", None)
            or os.environ.get("OPENAI_BASE_URL")
            or settings.llm_base_url
            or "https://api.openai.com/v1"
        )
        return url.rstrip("/")

    async def generate(
        self,
        request: ResearchModelRequest,
    ) -> ResearchProviderResponse:
        # 0. Kiểm tra type của request
        if not isinstance(request, ResearchModelRequest):
            raise TypeError(
                f"ResearchProvider.generate requires ResearchModelRequest, got {type(request).__name__}. "
                "Direct dataset records or generic dicts are strictly forbidden."
            )

        # 1. Fail-closed Firewall quét toàn bộ request
        GroundTruthFirewall.default().inspect(
            request,
            sample_id=request.sample_id,
            run_id=request.run_id,
            base_path="research_provider.request",
        )

        # 2. Type-level ground truth assertion
        assert_not_ground_truth(request)

        # 3. Model identifier verification (No silent model substitution)
        if not self.model_name or not isinstance(self.model_name, str) or not self.model_name.strip():
            raise ResearchProviderConfigurationError("Model identifier must be configured and cannot be empty.")

        if request.model != self.model_name:
            raise ResearchProviderConfigurationError(
                f"Model mismatch: request model '{request.model}' != provider configured model '{self.model_name}'. "
                "Silent model substitution is strictly prohibited."
            )

        payload: Dict[str, Any] = {
            "model": self.model_name,
            "messages": [{"role": m.role, "content": m.content} for m in request.messages],
            "temperature": request.temperature,
            "max_tokens": request.max_output_tokens,
        }
        if request.response_format_mode == "json":
            payload["response_format"] = {"type": "json_object"}

        api_key = self._get_api_key()
        base_url = self._get_base_url()
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        max_attempts = self.retry_policy.max_attempts
        last_exception: Optional[ResearchProviderError] = None

        for attempt in range(1, max_attempts + 1):
            self.last_attempts = attempt
            t_start = time.time()
            try:
                async with httpx.AsyncClient(
                    timeout=settings.llm_timeout_seconds,
                    transport=self._transport,
                ) as client:
                    response = await client.post(
                        f"{base_url}/chat/completions",
                        headers=headers,
                        json=payload,
                    )
                latency_ms = round((time.time() - t_start) * 1000, 2)
                status_code = response.status_code

                # Fatal non-retryable authentication failures
                if status_code in (401, 403):
                    raise ResearchProviderAuthenticationError(
                        f"Research provider authentication rejected with HTTP {status_code}.",
                        http_status=status_code,
                        attempts=attempt,
                    )
                elif status_code == 429:
                    raise ResearchProviderRateLimitError(
                        "Research provider rate limit exceeded (HTTP 429).",
                        http_status=429,
                        attempts=attempt,
                    )
                elif status_code == 408:
                    raise ResearchProviderTimeoutError(
                        "Research provider request timeout (HTTP 408).",
                        http_status=408,
                        attempts=attempt,
                    )
                elif 500 <= status_code <= 599:
                    raise ResearchProviderResponseError(
                        f"Research provider server error (HTTP {status_code}).",
                        retryable=True,
                        http_status=status_code,
                        failure_type="HTTP_5XX",
                        attempts=attempt,
                    )
                elif status_code >= 400:
                    raise ResearchProviderResponseError(
                        f"Research provider returned HTTP {status_code}.",
                        retryable=False,
                        http_status=status_code,
                        failure_type="RESPONSE_ERROR",
                        attempts=attempt,
                    )

                # Parse JSON
                try:
                    res_json = response.json()
                except Exception as exc:
                    raise ResearchProviderResponseError(
                        "Research provider did not return valid JSON.",
                        retryable=False,
                        http_status=status_code,
                        failure_type="MALFORMED_RESPONSE",
                        attempts=attempt,
                    ) from exc

                # Extract choices and content
                choices = res_json.get("choices")
                if not choices or not isinstance(choices, list) or len(choices) == 0:
                    raise ResearchProviderResponseError(
                        "Research provider returned response with missing or empty choices.",
                        retryable=False,
                        http_status=status_code,
                        failure_type="EMPTY_RESPONSE",
                        attempts=attempt,
                    )

                choice_obj = choices[0]
                if not isinstance(choice_obj, dict):
                    raise ResearchProviderResponseError(
                        "Research provider returned malformed choice object.",
                        retryable=False,
                        http_status=status_code,
                        failure_type="MALFORMED_RESPONSE",
                        attempts=attempt,
                    )

                msg_obj = choice_obj.get("message", {})
                if not isinstance(msg_obj, dict):
                    raise ResearchProviderResponseError(
                        "Research provider returned malformed message object.",
                        retryable=False,
                        http_status=status_code,
                        failure_type="MALFORMED_RESPONSE",
                        attempts=attempt,
                    )

                content = msg_obj.get("content")
                if content is None or not isinstance(content, str) or not content.strip():
                    raise ResearchProviderResponseError(
                        "Research provider returned empty or whitespace-only response.",
                        retryable=False,
                        http_status=status_code,
                        failure_type="EMPTY_RESPONSE",
                        attempts=attempt,
                    )

                # Trích xuất metadata một cách trung thực (không bịa đặt hay ước tính)
                request_id = (
                    response.headers.get("x-request-id")
                    or response.headers.get("request-id")
                    or None
                )
                provider_response_id = res_json.get("id") or None
                returned_model = res_json.get("model") or None
                finish_reason = choice_obj.get("finish_reason") or None

                usage: Optional[ResearchUsage] = None
                usage_raw = res_json.get("usage")
                if isinstance(usage_raw, dict) and "prompt_tokens" in usage_raw and "completion_tokens" in usage_raw:
                    usage = ResearchUsage(
                        input_tokens=int(usage_raw.get("prompt_tokens", 0)),
                        output_tokens=int(usage_raw.get("completion_tokens", 0)),
                        total_tokens=int(
                            usage_raw.get(
                                "total_tokens",
                                usage_raw.get("prompt_tokens", 0) + usage_raw.get("completion_tokens", 0),
                            )
                        ),
                    )

                # Lưu safe metadata (loại trừ authorization hay api keys)
                safe_metadata: Dict[str, Any] = {}
                for safe_key in ("system_fingerprint", "created", "object"):
                    if safe_key in res_json:
                        safe_metadata[safe_key] = res_json[safe_key]

                return ResearchProviderResponse(
                    provider=self.provider_name,
                    requested_model=request.model,
                    returned_model=returned_model,
                    raw_text=content,
                    request_id=request_id,
                    provider_response_id=provider_response_id,
                    finish_reason=finish_reason,
                    usage=usage,
                    provider_response_received=True,
                    raw_metadata=safe_metadata,
                    latency_ms=latency_ms,
                    response_format_mode=request.response_format_mode,
                )

            except (httpx.TimeoutException, asyncio.TimeoutError) as exc:
                last_exception = ResearchProviderTimeoutError(
                    f"Research provider connection timed out: {sanitize_error_message(str(exc))}",
                    http_status=408,
                    attempts=attempt,
                )
            except (httpx.ConnectError, httpx.NetworkError, httpx.TransportError) as exc:
                last_exception = ResearchProviderNetworkError(
                    f"Research provider network transport error: {sanitize_error_message(str(exc))}",
                    http_status=None,
                    attempts=attempt,
                )
            except ResearchProviderError as exc:
                last_exception = exc

            # Kiểm tra retry policy
            if attempt < max_attempts and last_exception.retryable:
                delay = self.retry_policy.get_delay_seconds(attempt - 1)
                logger.warning(
                    "Research provider attempt %d/%d failed with %s (%s). Retrying in %.2fs...",
                    attempt,
                    max_attempts,
                    last_exception.failure_type,
                    last_exception.message_safe,
                    delay,
                )
                if delay > 0:
                    await asyncio.sleep(delay)
            else:
                break

        if last_exception is not None:
            raise last_exception

        raise ResearchProviderResponseError(
            "Research provider call failed with no response.",
            attempts=max_attempts,
        )


def validate_research_provider(
    provider: Optional[str] = None,
    model: Optional[str] = None,
    provider_client: Optional[Any] = None,
    *,
    api_key: Optional[str] = None,
    allow_test_doubles: bool = False,
) -> Any:
    """
    Hàm kiểm tra preflight bắt buộc trước khi thực thi nghiên cứu đánh giá (APT-055 / APT-057).

    QUY TẮC BẮT BUỘC:
    1. Provider configured: Không được rỗng, không phải mock/fake, chỉ chấp nhận real provider ('openai').
       Provider 'azure' bị từ chối rõ ràng cho đến khi có adapter chuyên biệt.
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
                "Mock and fake providers are strictly prohibited in research mode ('openai' required)."
            )

        if norm_provider == "azure":
            raise ResearchProviderConfigurationError(
                "Unsupported research provider 'azure'. Only 'openai' currently has an active real provider adapter. "
                "Azure support is deferred until a dedicated AzureResearchProvider is implemented."
            )

        if norm_provider != "openai":
            raise ResearchProviderConfigurationError(
                f"Unsupported research provider '{provider}'. Supported real provider is: 'openai'."
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
