from typing import Any

from app.services.llm_client import OpenAICompatibleLLMClient


class AIService:
    """Generic AI service for CodeSense AI tutor system."""

    def __init__(self, llm_client: OpenAICompatibleLLMClient | None = None):
        self.llm_client = llm_client or OpenAICompatibleLLMClient()

    async def generate_response(self, messages: list[dict[str, Any]], **kwargs: Any) -> str:
        """Sinh câu trả lời thông qua LLM client."""
        return await self.llm_client.chat_completion(messages, **kwargs)

