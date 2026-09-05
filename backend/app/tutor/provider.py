import json
from typing import Any, Protocol, runtime_checkable

from app.services.llm_client import LLMClientError, OpenAICompatibleLLMClient


class TutorProviderError(Exception):
    """Lỗi phát sinh từ nhà cung cấp LLM (timeout, kết nối mạng, lỗi HTTP 5xx, v.v.)."""

    def __init__(self, message: str, *, retryable: bool = False, status_code: int | None = None):
        super().__init__(message)
        self.retryable = retryable
        self.status_code = status_code


@runtime_checkable
class TutorLLMProvider(Protocol):
    """Giao diện trừu tượng tối giản cho LLM Provider phục vụ TutorService."""

    async def generate_response(
        self,
        messages: list[dict[str, Any]],
        *,
        temperature: float = 0.2,
        max_tokens: int = 1500,
    ) -> str:
        """Thực hiện gọi mô hình ngôn ngữ và trả về chuỗi nội dung phản hồi thô."""
        ...


class OpenAITutorProvider:
    """Hiện thực TutorLLMProvider tái sử dụng OpenAICompatibleLLMClient có sẵn."""

    def __init__(self, client: OpenAICompatibleLLMClient | None = None):
        self._client = client or OpenAICompatibleLLMClient()

    async def generate_response(
        self,
        messages: list[dict[str, Any]],
        *,
        temperature: float = 0.2,
        max_tokens: int = 1500,
    ) -> str:
        try:
            return await self._client.chat_completion(
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
        except LLMClientError as exc:
            raise TutorProviderError(
                str(exc),
                retryable=exc.retryable,
                status_code=exc.status_code,
            ) from exc
        except Exception as exc:
            raise TutorProviderError(
                f"Lỗi không xác định từ LLM provider: {str(exc)}",
                retryable=False,
            ) from exc


class DeterministicMockTutorProvider:
    """Test double xác định (deterministic) phục vụ kiểm thử đơn vị độc lập với mạng."""

    def __init__(
        self,
        canned_response: str | dict[str, Any] | None = None,
        error_to_raise: Exception | None = None,
    ):
        self._error_to_raise = error_to_raise
        self.recorded_messages: list[list[dict[str, Any]]] = []

        if canned_response is None:
            self._canned_response = json.dumps(self.default_canned_payload(), ensure_ascii=False)
        elif isinstance(canned_response, dict):
            self._canned_response = json.dumps(canned_response, ensure_ascii=False)
        else:
            self._canned_response = canned_response

    @staticmethod
    def default_canned_payload() -> dict[str, Any]:
        return {
            "diagnosis": {
                "issue_type": "semantic_error",
                "severity": "warning",
                "location": "Student.cs: constructor",
                "confidence": 0.95,
            },
            "knowledge_components": [
                "csharp_constructor",
                "this_keyword",
                "variable_shadowing",
            ],
            "possible_misconception": {
                "type": "parameter_shadowing_confusion",
                "description": "Sinh viên có thể đang nhầm lẫn giữa tham số hàm và biến thành viên (field) khi chúng có cùng tên gọi.",
                "confidence": 0.85,
            },
            "evidence": {
                "code": "name = name;",
                "reason": "Phép gán tham số vào chính nó không làm thay đổi giá trị của thuộc tính đối tượng.",
            },
            "teaching_strategy": "socratic_questioning",
            "tutor_response": "Quan sát constructor của bạn: khi viết 'name = name', C# sẽ ưu tiên tham chiếu tới biến nào? Bạn có nhớ từ khóa nào dùng để phân biệt rõ thuộc tính của đối tượng hiện tại không?",
            "hint_level": 1,
            "solution_revealed": False,
            "next_action": "Thử tìm hiểu vai trò của từ khóa 'this' khi gán giá trị trong constructor.",
        }

    def set_response(self, response: str | dict[str, Any]) -> None:
        if isinstance(response, dict):
            self._canned_response = json.dumps(response, ensure_ascii=False)
        else:
            self._canned_response = response

    def set_error(self, error: Exception | None) -> None:
        self._error_to_raise = error

    async def generate_response(
        self,
        messages: list[dict[str, Any]],
        *,
        temperature: float = 0.2,
        max_tokens: int = 1500,
    ) -> str:
        self.recorded_messages.append(messages)
        if self._error_to_raise:
            raise self._error_to_raise
        return self._canned_response
