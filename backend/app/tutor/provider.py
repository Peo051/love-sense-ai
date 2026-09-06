import json
import logging
import re
from abc import ABC, abstractmethod
from typing import Any, Optional

from app.services.llm_client import LLMClientError, OpenAICompatibleLLMClient

logger = logging.getLogger(__name__)


class TutorProviderError(Exception):
    """Lỗi ngoại lệ khi giao tiếp với LLM Provider."""

    def __init__(self, message: str, retryable: bool = False, status_code: int = 502):
        super().__init__(message)
        self.message = message
        self.retryable = retryable
        self.status_code = status_code


class TutorLLMProvider(ABC):
    """Interface trừu tượng cho nhà cung cấp LLM phục vụ AI Tutor."""

    @abstractmethod
    async def generate_response(
        self,
        messages: list[dict[str, Any]],
        *,
        temperature: float = 0.2,
        max_tokens: int = 1500,
    ) -> str:
        """Gửi danh sách tin nhắn tới LLM và nhận về chuỗi phản hồi thô."""
        pass


class OpenAITutorProvider(TutorLLMProvider):
    """Triển khai LLM Provider tái sử dụng OpenAICompatibleLLMClient hiện có."""

    def __init__(self, client: Optional[OpenAICompatibleLLMClient] = None):
        self._client = client or OpenAICompatibleLLMClient()

    async def generate_response(
        self,
        messages: list[dict[str, Any]],
        *,
        temperature: float = 0.2,
        max_tokens: int = 1500,
    ) -> str:
        from app.evaluation.firewall import GroundTruthFirewall
        from app.evaluation.schemas import assert_not_ground_truth

        # Fail-closed runtime firewall check immediately before provider invocation
        GroundTruthFirewall.default().inspect(messages, base_path="messages")

        assert_not_ground_truth(messages)
        for msg in messages:
            assert_not_ground_truth(msg)
            if isinstance(msg, dict):
                assert_not_ground_truth(msg.get("content"))

        try:
            return await self._client.chat_completion(
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
        except LLMClientError as exc:
            logger.error("Lỗi từ OpenAICompatibleLLMClient trong TutorProvider: %s", str(exc))
            raise TutorProviderError(
                str(exc),
                retryable=exc.retryable,
                status_code=exc.status_code or 502,
            ) from exc
        except Exception as exc:
            logger.error("Lỗi không lường trước từ LLM client: %s", str(exc))
            raise TutorProviderError(
                f"Lỗi không xác định từ mô hình: {str(exc)}",
                retryable=False,
                status_code=500,
            ) from exc


class DeterministicMockTutorProvider(TutorLLMProvider):
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
                "category": "logic_error",
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
            "prompt_version": "v1",
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
        from app.evaluation.firewall import GroundTruthFirewall
        from app.evaluation.schemas import assert_not_ground_truth

        # Fail-closed runtime firewall check immediately before provider invocation
        GroundTruthFirewall.default().inspect(messages, base_path="messages")

        assert_not_ground_truth(messages)
        for msg in messages:
            assert_not_ground_truth(msg)
            if isinstance(msg, dict):
                assert_not_ground_truth(msg.get("content"))

        self.recorded_messages.append(messages)
        if self._error_to_raise:
            raise self._error_to_raise

        response_text = self._canned_response
        user_msg = next((m.get("content", "") for m in messages if m.get("role") == "user"), "")

        # Nếu canned response chứa placeholder 'name = name;' nhưng đề bài/code của test gửi lên
        # là một đoạn mã khác (như Rectangle), thích ứng evidence code để grounded vào request
        if "name = name;" in response_text and "name = name;" not in user_msg:
            code_match = re.search(r"<untrusted_student_code>\s*([\s\S]*?)\s*</untrusted_student_code>", user_msg)
            err_match = re.search(r"<untrusted_compiler_error>\s*([\s\S]*?)\s*</untrusted_compiler_error>", user_msg)
            replacement_code = None
            if err_match and err_match.group(1).strip() and err_match.group(1).strip() != "None":
                replacement_code = err_match.group(1).strip().splitlines()[0]
            elif code_match and code_match.group(1).strip():
                lines = [l.strip() for l in code_match.group(1).strip().splitlines() if l.strip() and not l.strip().startswith("class ")]
                replacement_code = lines[0] if lines else code_match.group(1).strip()

            if replacement_code:
                response_text = response_text.replace("name = name;", replacement_code)

        return response_text
