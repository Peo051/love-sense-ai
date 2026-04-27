import json
from typing import Any

import httpx
from pydantic import ValidationError

from app.core.config import settings
from app.schemas.analyze_schema import AnalyzeResponse
from app.services.analysis_policy import SYSTEM_PROMPT, WARNING_MESSAGE


class LLMClientError(Exception):
    """Raised when the configured LLM provider cannot return a valid analysis."""


class OpenAICompatibleLLMClient:
    """Client tối giản cho các provider tương thích OpenAI Chat Completions như 9router."""

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

        try:
            async with httpx.AsyncClient(timeout=settings.llm_timeout_seconds) as client:
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
            raise LLMClientError(f"LLM provider trả lỗi HTTP {status_code}.") from exc
        except httpx.HTTPError as exc:
            raise LLMClientError("Không thể kết nối LLM provider.") from exc

        try:
            response_body = response.json()
        except ValueError as exc:
            raise LLMClientError("LLM provider không trả HTTP JSON hợp lệ.") from exc

        return self._parse_response(response_body)

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
