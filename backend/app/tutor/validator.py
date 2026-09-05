import json
import re
from typing import Any

from pydantic import ValidationError

from app.schemas.tutor_schema import TutorResponse


class TutorOutputValidationError(Exception):
    """Lỗi khi cấu trúc đầu ra từ mô hình AI không hợp lệ hoặc không parse được JSON."""

    def __init__(self, message: str, raw_output: str | None = None):
        super().__init__(message)
        self.raw_output = raw_output


class TutorOutputValidator:
    """Validator kiểm tra tính toàn vẹn và hợp lệ của phản hồi gia sư từ LLM."""

    @classmethod
    def clean_json_string(cls, raw_text: str) -> str:
        """Bóc tách chuỗi JSON nếu được bọc trong markdown code block (```json ... ```)."""
        text = raw_text.strip()

        # Tìm kiếm code block ```json ... ``` hoặc ``` ... ```
        match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text, re.IGNORECASE)
        if match:
            return match.group(1).strip()

        # Nếu có tiền tố/hậu tố văn bản tự do ngoài JSON object {...}
        first_brace = text.find("{")
        last_brace = text.rfind("}")
        if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
            return text[first_brace : last_brace + 1].strip()

        return text

    @classmethod
    def parse_and_validate(
        cls,
        raw_output: str,
        *,
        requested_hint_level: int = 1,
    ) -> TutorResponse:
        """
        Parse chuỗi văn bản từ LLM thành JSON và validate qua Pydantic schema TutorResponse.
        """
        if not raw_output or not raw_output.strip():
            raise TutorOutputValidationError("LLM trả về phản hồi rỗng.", raw_output=raw_output)

        cleaned_json = cls.clean_json_string(raw_output)

        try:
            parsed_data = json.loads(cleaned_json)
        except json.JSONDecodeError as exc:
            raise TutorOutputValidationError(
                f"Phản hồi từ LLM không phải là chuỗi JSON hợp lệ: {str(exc)}",
                raw_output=raw_output,
            ) from exc

        if not isinstance(parsed_data, dict):
            raise TutorOutputValidationError(
                "Dữ liệu JSON từ LLM phải là một JSON object/dictionary.",
                raw_output=raw_output,
            )

        # Đảm bảo hint_level đồng nhất với yêu cầu nếu LLM trả thiếu hoặc lệch
        if "hint_level" not in parsed_data or parsed_data["hint_level"] not in (1, 2, 3, 4):
            parsed_data["hint_level"] = requested_hint_level

        # Kiểm tra nguyên tắc sư phạm: chỉ cho phép solution_revealed = True khi hint_level = 4
        if requested_hint_level < 4:
            parsed_data["solution_revealed"] = False
        elif "solution_revealed" not in parsed_data:
            parsed_data["solution_revealed"] = True

        # Đảm bảo metadata prompt_version
        if "prompt_version" not in parsed_data or not parsed_data["prompt_version"]:
            parsed_data["prompt_version"] = "v1"

        try:
            response_model = TutorResponse.model_validate(parsed_data)
        except ValidationError as exc:
            raise TutorOutputValidationError(
                f"Cấu trúc phản hồi từ LLM không khớp schema TutorResponse: {str(exc)}",
                raw_output=raw_output,
            ) from exc

        return response_model
