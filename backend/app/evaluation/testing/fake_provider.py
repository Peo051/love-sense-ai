"""
Fake Test Provider for Unit Testing (APT-054).

QUY TẮC KIỂM THỬ (TESTING RULES):
- Fake provider và deterministic fixture CHỈ được phép dùng trong kiểm thử đơn vị nội bộ.
- Tuyệt đối KHÔNG được thỏa mãn cấu hình CLI của nghiên cứu thực nghiệm (Research Mode).
- Bị từ chối tự động (rejected with TypeError) nếu chạy trong ResearchRunner mà không có
  môi trường test được khai báo rõ ràng (explicit test environment).
"""

from abc import ABC, abstractmethod
import json
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class FakeTestProvider(ABC):
    """
    Interface cơ sở cho mọi Test Double/Fake Provider.
    Mọi class kế thừa interface này bị từ chối trong Research Mode.
    """

    @property
    def is_real_provider(self) -> bool:
        return False

    @property
    def is_fake_test_provider(self) -> bool:
        return True

    @abstractmethod
    async def generate_response(
        self,
        messages: List[Dict[str, Any]],
        *,
        temperature: float = 0.2,
        max_tokens: int = 1500,
    ) -> str:
        pass


class DeterministicFakeProvider(FakeTestProvider):
    """
    Fake Provider tất định (deterministic) phục vụ kiểm thử đơn vị độc lập mạng.
    Tuyệt đối không truy cập nhãn vàng dataset.
    """

    def __init__(
        self,
        canned_response: Optional[str | Dict[str, Any]] = None,
        error_to_raise: Optional[Exception] = None,
    ):
        self._error_to_raise = error_to_raise
        self.recorded_messages: List[List[Dict[str, Any]]] = []

        if canned_response is None:
            self._canned_response = json.dumps(self.default_canned_payload(), ensure_ascii=False)
        elif isinstance(canned_response, dict):
            self._canned_response = json.dumps(canned_response, ensure_ascii=False)
        else:
            self._canned_response = canned_response

    @staticmethod
    def default_canned_payload() -> Dict[str, Any]:
        return {
            "bug_status": "has_bug",
            "error_category": "logic_error",
            "bug_type": "semantic_error",
            "bug_location": {"file": "Program.cs", "start_line": 5, "end_line": 5, "symbol": "constructor"},
            "evidence": "name = name;",
            "knowledge_components": ["csharp_constructor", "this_keyword"],
            "possible_misconception": "Sinh viên nhầm lẫn giữa tham số và trường dữ liệu đối tượng.",
            "reference_diagnosis": "Lỗi gán đè tham số trong hàm khởi tạo.",
            "hint_1": "Quan sát constructor của bạn: hãy phân biệt rõ thuộc tính với tham số.",
            "hint_2": "Sử dụng từ khóa this để định danh thuộc tính của đối tượng hiện tại.",
            "hint_3": "Sửa thành this.name = name;",
            "explanation_vi": "Giải thích chi tiết về từ khóa this trong C#.",
        }

    def set_response(self, response: str | Dict[str, Any]) -> None:
        if isinstance(response, dict):
            self._canned_response = json.dumps(response, ensure_ascii=False)
        else:
            self._canned_response = response

    def set_error(self, error: Optional[Exception]) -> None:
        self._error_to_raise = error

    async def generate_response(
        self,
        messages: List[Dict[str, Any]],
        *,
        temperature: float = 0.2,
        max_tokens: int = 1500,
    ) -> str:
        from app.evaluation.firewall import GroundTruthFirewall
        from app.evaluation.schemas import assert_not_ground_truth

        # Fail-closed firewall check
        GroundTruthFirewall.default().inspect(messages, base_path="fake_provider.messages")

        assert_not_ground_truth(messages)
        for msg in messages:
            assert_not_ground_truth(msg)

        self.recorded_messages.append(messages)
        if self._error_to_raise:
            raise self._error_to_raise

        return self._canned_response


class LeakingFakeProvider(FakeTestProvider):
    """
    Fake Provider cố tình sinh phản hồi chứa giải pháp trực tiếp trong hint_1
    để kiểm thử khả năng phát hiện rò rỉ (leakage detection) của TutoringMetricsSuite.
    """

    def __init__(self, code_snippet: str = "public class Diem2D { public int X { get; set; } public int Y { get; set; } }"):
        self.code_snippet = code_snippet

    async def generate_response(
        self,
        messages: List[Dict[str, Any]],
        *,
        temperature: float = 0.2,
        max_tokens: int = 1500,
    ) -> str:
        payload = {
            "bug_status": "has_bug",
            "error_category": "logic_error",
            "bug_type": "semantic_error",
            "bug_location": None,
            "evidence": None,
            "knowledge_components": ["OOP.Classes"],
            "possible_misconception": None,
            "reference_diagnosis": "Tiết lộ mã nguồn",
            "hint_1": f"Mã giải pháp hoàn chỉnh:\n```csharp\n{self.code_snippet}\n```",
            "hint_2": "",
            "hint_3": "",
            "explanation_vi": "Giải pháp trực diện.",
        }
        return json.dumps(payload, ensure_ascii=False)
