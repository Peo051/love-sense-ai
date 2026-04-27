import asyncio
import base64
import json
from typing import Any

import httpx
from pydantic import ValidationError

from app.core.config import settings
from app.schemas.analyze_schema import AnalyzeResponse
from app.schemas.ocr_schema import VisionOcrResponse
from app.services.analysis_policy import SYSTEM_PROMPT, WARNING_MESSAGE


class LLMClientError(Exception):
    """Raised when the configured LLM provider cannot return a valid analysis."""

    def __init__(self, message: str, *, retryable: bool = False):
        super().__init__(message)
        self.retryable = retryable


class OpenAICompatibleLLMClient:
    """Client tối giản cho các provider tương thích OpenAI Chat Completions như 9router."""

    def __init__(self, transport: httpx.AsyncBaseTransport | None = None):
        self._transport = transport

    async def analyze_emotion(self, chat_text: str, profile_context: str = "") -> AnalyzeResponse:
        self._validate_settings()

        payload = {
            "model": settings.llm_model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": self._build_user_prompt(chat_text, profile_context),
                },
            ],
            "temperature": 0.2,
            "max_tokens": 900,
        }

        response_body = await self._post_with_retries(payload)
        return self._parse_response(response_body)

    async def extract_chat_text_from_image(self, image_bytes: bytes, mime_type: str) -> VisionOcrResponse:
        model_name = settings.vision_ocr_model.strip() or settings.llm_model.strip()
        self._validate_vision_settings(model_name)

        encoded_image = base64.b64encode(image_bytes).decode("ascii")
        payload = {
            "model": model_name,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Bạn là bộ trích xuất chữ từ ảnh chụp đoạn chat. "
                        "Chỉ trích xuất nội dung nhìn thấy trong ảnh, không suy đoán cảm xúc, "
                        "không thêm kết luận và không tạo thông tin không có trong ảnh."
                    ),
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                "Hãy đọc ảnh chụp đoạn hội thoại và trả về JSON hợp lệ theo schema: "
                                '{"text":"...", "confidence": 0-100, "warnings":["..."]}. '
                                "Giữ xuống dòng giữa các tin nhắn. Nếu không chắc người gửi, không tự gán tên. "
                                "Nếu ảnh mờ, chữ nhỏ, emoji hoặc nền làm khó đọc, thêm cảnh báo ngắn trong warnings."
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
            "max_tokens": 900,
        }

        response_body = await self._post_with_retries(payload)
        return self._parse_vision_response(response_body)

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
        try:
            async with httpx.AsyncClient(timeout=settings.llm_timeout_seconds, transport=self._transport) as client:
                response = await client.post(
                    f"{settings.llm_base_url.rstrip('/')}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {settings.llm_api_key}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                )
                response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            status_code = exc.response.status_code
            raise LLMClientError(
                f"LLM provider trả lỗi HTTP {status_code}.",
                retryable=self._is_retryable_status_code(status_code),
            ) from exc
        except httpx.TimeoutException as exc:
            raise LLMClientError("LLM provider phản hồi quá thời gian chờ.", retryable=True) from exc
        except httpx.TransportError as exc:
            raise LLMClientError("Không thể kết nối LLM provider.", retryable=True) from exc

        try:
            return response.json()
        except ValueError as exc:
            raise LLMClientError("LLM provider không trả HTTP JSON hợp lệ.") from exc

    def _validate_settings(self) -> None:
        missing_fields = [
            field
            for field, value in {
                "LLM_BASE_URL": settings.llm_base_url,
                "LLM_API_KEY": settings.llm_api_key,
                "LLM_MODEL": settings.llm_model,
            }.items()
            if not value
        ]
        if missing_fields:
            raise LLMClientError(f"Thiếu cấu hình LLM: {', '.join(missing_fields)}.")

    def _validate_vision_settings(self, model_name: str) -> None:
        missing_fields = [
            field
            for field, value in {
                "LLM_BASE_URL": settings.llm_base_url,
                "LLM_API_KEY": settings.llm_api_key,
                "VISION_OCR_MODEL or LLM_MODEL": model_name,
            }.items()
            if not value
        ]
        if missing_fields:
            raise LLMClientError(f"Thiếu cấu hình Vision OCR: {', '.join(missing_fields)}.")

    def _is_retryable_status_code(self, status_code: int) -> bool:
        return status_code in {408, 429} or 500 <= status_code <= 599

    def _build_user_prompt(self, chat_text: str, profile_context: str) -> str:
        return (
            "Hãy phân tích đoạn chat sau và trả về JSON đúng schema.\n\n"
            f"Đoạn chat:\n{chat_text}\n\n"
            f"Bối cảnh cá nhân hóa:\n{profile_context or 'Không có bối cảnh bổ sung.'}"
        )

    def _parse_response(self, response_body: dict[str, Any]) -> AnalyzeResponse:
        try:
            content = response_body["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise LLMClientError("LLM provider trả response không đúng định dạng chat completions.") from exc

        if not isinstance(content, str) or not content.strip():
            raise LLMClientError("LLM provider không trả nội dung phân tích.")

        try:
            raw_result = json.loads(self._extract_json(content))
            result = AnalyzeResponse.model_validate(raw_result)
        except (json.JSONDecodeError, ValidationError) as exc:
            raise LLMClientError("LLM provider không trả JSON hợp lệ theo schema phân tích.") from exc

        return self._normalize_result(result)

    def _parse_vision_response(self, response_body: dict[str, Any]) -> VisionOcrResponse:
        try:
            content = response_body["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise LLMClientError("Vision provider trả response không đúng định dạng chat completions.") from exc

        if not isinstance(content, str) or not content.strip():
            raise LLMClientError("Vision provider không trả nội dung OCR.")

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

    def _normalize_result(self, result: AnalyzeResponse) -> AnalyzeResponse:
        confidence = min(1.0, max(0.0, float(result.confidence)))
        distribution = {
            emotion: min(1.0, max(0.0, float(score)))
            for emotion, score in result.emotion_distribution.items()
        }

        # Backend là lớp bảo vệ cuối cùng cho thông điệp an toàn, kể cả khi LLM trả thiếu hoặc sửa cảnh báo.
        warning = result.warning if "tham khảo" in result.warning.lower() else WARNING_MESSAGE

        return AnalyzeResponse(
            overall_emotion=result.overall_emotion,
            confidence=confidence,
            emotion_distribution=distribution or {"trung_lập": 1.0},
            summary=result.summary,
            context_note=result.context_note,
            suggested_reply=result.suggested_reply,
            warning=warning,
        )
