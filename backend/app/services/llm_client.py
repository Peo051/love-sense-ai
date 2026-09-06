import asyncio
import base64
import json
import os
from typing import Any

import httpx
from pydantic import ValidationError

from app.core.config import settings
from app.schemas.ocr_schema import VisionOcrResponse


class LLMClientError(Exception):
    """Raised when the configured LLM provider cannot return a valid response."""

    def __init__(self, message: str, *, retryable: bool = False, status_code: int | None = None):
        super().__init__(message)
        self.retryable = retryable
        self.status_code = status_code


class OpenAICompatibleLLMClient:
    """Client tối giản cho các provider tương thích OpenAI Chat Completions như 9router."""

    def __init__(
        self,
        transport: httpx.AsyncBaseTransport | None = None,
        api_key: str | None = None,
        base_url: str | None = None,
    ):
        self._transport = transport
        self._api_key = api_key
        self._base_url = base_url

    def _get_api_key(self) -> str:
        return self._api_key or os.environ.get("OPENAI_API_KEY") or settings.llm_api_key or ""

    def _get_base_url(self) -> str:
        return self._base_url or os.environ.get("OPENAI_BASE_URL") or settings.llm_base_url or ""

    async def chat_completion(
        self,
        messages: list[dict[str, Any]],
        *,
        model: str | None = None,
        temperature: float = 0.2,
        max_tokens: int = 1000,
    ) -> str:
        """Thực hiện gọi generic Chat Completion với retry và timeout."""
        self._validate_settings()

        payload = {
            "model": model or settings.llm_model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        response_body = await self._post_with_retries(payload)
        return self._extract_choice_content(response_body)

    async def extract_programming_text_from_image(self, image_bytes: bytes, mime_type: str) -> VisionOcrResponse:
        model_name = settings.vision_ocr_model.strip() or settings.llm_model.strip()
        self._validate_vision_settings(model_name)

        encoded_image = base64.b64encode(image_bytes).decode("ascii")
        payload = {
            "model": model_name,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Bạn là chuyên gia OCR và phân tích tài liệu lập trình C# OOP. "
                        "Nhiệm vụ của bạn là nhận diện chính xác văn bản từ ảnh chụp màn hình bài tập, đoạn mã C#, hoặc thông báo lỗi biên dịch/terminal. "
                        "Chỉ trích xuất nội dung nhìn thấy trong ảnh, không tự ý sửa lỗi code của học viên, "
                        "không thêm kết luận và không tạo thông tin không có trong ảnh. "
                        "Giữ nguyên thụt lề mã nguồn và các ký tự cú pháp C#."
                    ),
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                "Hãy đọc ảnh chụp và trích xuất thành JSON hợp lệ theo cấu trúc sau:\n"
                                "{\n"
                                '  "text": "toàn bộ văn bản nhìn thấy trong ảnh",\n'
                                '  "problem_statement": "yêu cầu đề bài hoặc đặc tả bài toán nếu có trong ảnh (hoặc null)",\n'
                                '  "student_code": "đoạn mã nguồn C# nếu có trong ảnh, giữ nguyên định dạng dòng và thụt lề (hoặc null)",\n'
                                '  "compiler_error": "thông báo lỗi biên dịch/terminal hoặc mã lỗi CSxxxx nếu có trong ảnh (hoặc null)",\n'
                                '  "confidence": 0-100,\n'
                                '  "warnings": ["cảnh báo nếu ảnh mờ, bị cắt chữ, hoặc code khó đọc"]\n'
                                "}\n"
                                "Nếu ảnh chỉ chứa một phần (ví dụ chỉ có mã C# hoặc chỉ có lỗi compiler), hãy điền trường tương ứng và để các trường khác là null."
                            ),
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:{mime_type};base64,{encoded_image}"},
                        },
                    ],
                },
            ],
            "temperature": 0,
            "max_tokens": 1200,
        }

        response_body = await self._post_with_retries(payload)
        return self._parse_vision_response(response_body)

    async def extract_chat_text_from_image(self, image_bytes: bytes, mime_type: str) -> VisionOcrResponse:
        """Alias tương thích ngược cho extract_programming_text_from_image."""
        return await self.extract_programming_text_from_image(image_bytes, mime_type)

    async def _post_with_retries(self, payload: dict[str, Any]) -> dict[str, Any]:
        max_retries = max(0, settings.llm_max_retries)
        total_attempts = max_retries + 1

        for attempt_index in range(total_attempts):
            try:
                return await self._post_once(payload)
            except LLMClientError as exc:
                is_last_attempt = attempt_index >= total_attempts - 1
                if is_last_attempt or not exc.retryable:
                    raise

                delay_seconds = max(0.0, settings.llm_retry_base_delay_seconds) * (2**attempt_index)
                if delay_seconds > 0:
                    await asyncio.sleep(delay_seconds)

        raise LLMClientError("Không thể kết nối LLM provider.", retryable=True)

    async def _post_once(self, payload: dict[str, Any]) -> dict[str, Any]:
        base_url = self._get_base_url().rstrip("/")
        api_key = self._get_api_key()
        try:
            async with httpx.AsyncClient(timeout=settings.llm_timeout_seconds, transport=self._transport) as client:
                response = await client.post(
                    f"{base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                )
                response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            status_code = exc.response.status_code
            message = self._provider_error_message(exc.response, payload)
            raise LLMClientError(
                message or f"LLM provider trả lỗi HTTP {status_code}.",
                retryable=self._is_retryable_status_code(status_code),
                status_code=502,
            ) from exc
        except httpx.TimeoutException as exc:
            raise LLMClientError("LLM provider phản hồi quá thời gian chờ.", retryable=True) from exc
        except httpx.TransportError as exc:
            raise LLMClientError("Không thể kết nối LLM provider.", retryable=True) from exc

        try:
            return response.json()
        except ValueError as exc:
            raise LLMClientError("LLM provider không trả HTTP JSON hợp lệ.") from exc

    def _extract_choice_content(self, response_body: dict[str, Any]) -> str:
        try:
            content = response_body["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise LLMClientError("LLM provider trả response không đúng định dạng chat completions.") from exc

        if not isinstance(content, str) or not content.strip():
            raise LLMClientError("LLM provider không trả nội dung văn bản.")

        return content

    def _validate_settings(self) -> None:
        missing_fields = [
            field
            for field, value in {
                "LLM_BASE_URL": self._get_base_url(),
                "LLM_API_KEY": self._get_api_key(),
                "LLM_MODEL": settings.llm_model,
            }.items()
            if not value
        ]
        if missing_fields:
            raise LLMClientError(f"Thiếu cấu hình LLM: {', '.join(missing_fields)}.")

    def _validate_vision_settings(self, model_name: str) -> None:
        if not settings.llm_base_url:
            raise LLMClientError("Missing LLM_BASE_URL for AI Vision.", status_code=503)
        if not settings.llm_api_key:
            raise LLMClientError("Missing LLM_API_KEY for AI Vision.", status_code=503)
        if not model_name:
            raise LLMClientError("Missing VISION_MODEL or LLM_MODEL for AI Vision.", status_code=503)

    def _is_retryable_status_code(self, status_code: int) -> bool:
        return status_code in {408, 429} or 500 <= status_code <= 599

    def _provider_error_message(self, response: httpx.Response, payload: dict[str, Any]) -> str | None:
        if self._is_vision_payload(payload) and self._response_mentions_unsupported_image(response):
            return "Current model does not support image input."
        return None

    def _is_vision_payload(self, payload: dict[str, Any]) -> bool:
        for message in payload.get("messages", []):
            content = message.get("content") if isinstance(message, dict) else None
            if isinstance(content, list):
                for part in content:
                    if isinstance(part, dict) and part.get("type") == "image_url":
                        return True
        return False

    def _response_mentions_unsupported_image(self, response: httpx.Response) -> bool:
        try:
            response_text = response.text.lower()
        except Exception:
            return False

        unsupported_terms = ("not support image", "does not support image", "image input", "unsupported image")
        model_terms = ("model", "modality", "vision", "input")
        return any(term in response_text for term in unsupported_terms) and any(term in response_text for term in model_terms)

    def _parse_vision_response(self, response_body: dict[str, Any]) -> VisionOcrResponse:
        content = self._extract_choice_content(response_body)

        try:
            raw_result = json.loads(self._extract_json(content))
            result = VisionOcrResponse.model_validate(raw_result)
        except (json.JSONDecodeError, ValidationError) as exc:
            raise LLMClientError("Vision provider không trả JSON hợp lệ theo schema OCR.") from exc

        confidence = min(100.0, max(0.0, float(result.confidence)))
        warnings = result.warnings
        if confidence < 60 and not warnings:
            warnings = ["Vision AI không chắc chắn với ảnh này. Vui lòng kiểm tra lại nội dung trước khi phân tích."]

        return VisionOcrResponse(
            text=result.text,
            problem_statement=result.problem_statement,
            student_code=result.student_code,
            compiler_error=result.compiler_error,
            confidence=confidence,
            warnings=warnings,
            provider="vision",
        )

    def _extract_json(self, content: str) -> str:
        cleaned = content.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.removeprefix("```json").removeprefix("```").removesuffix("```").strip()

        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise json.JSONDecodeError("No JSON object found", cleaned, 0)
        return cleaned[start : end + 1]

