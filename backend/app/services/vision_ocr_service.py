from app.core.config import settings
from app.schemas.ocr_schema import VisionOcrResponse
from app.services.llm_client import LLMClientError, OpenAICompatibleLLMClient


class VisionOcrServiceError(Exception):
    """Raised when Vision OCR cannot produce safe extractable text."""

    def __init__(self, message: str, *, status_code: int = 502):
        super().__init__(message)
        self.status_code = status_code


class VisionOcrService:
    def __init__(self, llm_client: OpenAICompatibleLLMClient | None = None):
        self.llm_client = llm_client or OpenAICompatibleLLMClient()

    async def extract_programming_text_from_image(self, image_bytes: bytes, mime_type: str) -> VisionOcrResponse:
        """
        Trích xuất đề bài, mã nguồn C# và lỗi biên dịch từ ảnh chụp trong bộ nhớ RAM.
        Ảnh không được lưu vào đĩa cứng hoặc cơ sở dữ liệu (Privacy by Design).
        """
        if self._should_use_mock():
            raise VisionOcrServiceError("AI Vision đang tắt trong cấu hình backend.", status_code=503)

        try:
            return await self.llm_client.extract_programming_text_from_image(image_bytes, mime_type)
        except LLMClientError as exc:
            raise VisionOcrServiceError(str(exc) or "Vision AI chưa sẵn sàng.", status_code=exc.status_code or 502) from exc

    async def extract_chat_text_from_image(self, image_bytes: bytes, mime_type: str) -> VisionOcrResponse:
        """Alias tương thích ngược."""
        return await self.extract_programming_text_from_image(image_bytes, mime_type)

    def _should_use_mock(self) -> bool:
        return settings.llm_mock_mode or settings.llm_provider.lower() in {"", "mock", "none"}
