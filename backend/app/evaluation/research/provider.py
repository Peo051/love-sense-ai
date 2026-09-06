"""
Research LLM Provider Interface & Implementations (APT-054).

QUY TẮC NGHIÊN CỨU (RESEARCH RULES):
- Real provider only (bắt buộc kết nối mạng tới LLM thực tế).
- Không có quyền truy cập nhãn vàng (no ground truth access).
- Không được phép sử dụng mock, fake hay synthetic response.
- Không có cơ chế silent fallback.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import logging

from app.evaluation.firewall import GroundTruthFirewall
from app.evaluation.schemas import assert_not_ground_truth
from app.services.llm_client import LLMClientError, OpenAICompatibleLLMClient

logger = logging.getLogger(__name__)


class ResearchProvider(ABC):
    """
    Interface bắt buộc cho mọi Provider phục vụ nghiên cứu thực nghiệm khoa học.
    Bất kỳ provider nào kế thừa interface này đều được coi là một Real Provider.
    """

    @property
    def is_real_provider(self) -> bool:
        return True

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

    def __init__(self, client: Optional[OpenAICompatibleLLMClient] = None):
        self._client = client or OpenAICompatibleLLMClient()

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
                temperature=temperature,
                max_tokens=max_tokens,
            )
        except LLMClientError as exc:
            logger.error("Lỗi LLM client trong ResearchProvider: %s", str(exc))
            raise RuntimeError(f"Research evaluation LLM call failed: {str(exc)}") from exc
        except Exception as exc:
            logger.error("Lỗi không lường trước trong ResearchProvider: %s", str(exc))
            raise RuntimeError(f"Unexpected error during research inference: {str(exc)}") from exc
