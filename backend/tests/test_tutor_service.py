import json
import pytest
from unittest.mock import AsyncMock

from app.schemas.tutor_schema import TutorRequest
from app.services.llm_client import LLMClientError, OpenAICompatibleLLMClient
from app.tutor.provider import (
    DeterministicMockTutorProvider,
    OpenAITutorProvider,
    TutorProviderError,
)
from app.tutor.service import TutorService, TutorServiceError
from app.tutor.validator import TutorOutputValidationError, TutorOutputValidator


def sample_request(hint_level: int = 1) -> TutorRequest:
    return TutorRequest(
        problem_statement="Xây dựng lớp Rectangle có chiều dài và chiều rộng.",
        student_code="public class Rectangle { private int w; private int h; }",
        programming_language="csharp",
        compiler_error="CS0169: The field 'Rectangle.w' is never used",
        student_question="Em khai báo thuộc tính như thế này đúng chuẩn OOP chưa ạ?",
        topic="encapsulation",
        hint_level=hint_level,
        save_input=False,
        save_result=True,
    )


class TestTutorServiceOrchestration:
    @pytest.mark.anyio
    async def test_successful_feedback_generation_without_network(self):
        """Kiểm thử chu trình điều phối thành công 100% offline với DeterministicMockTutorProvider."""
        mock_provider = DeterministicMockTutorProvider()
        service = TutorService(llm_provider=mock_provider)

        request = sample_request(hint_level=1)
        response = await service.generate_feedback(request)

        # 1. Xác nhận response đúng schema
        assert response.diagnosis.issue_type == "semantic_error"
        assert response.diagnosis.confidence == 0.95
        assert response.hint_level == 1
        assert response.solution_revealed is False
        assert response.possible_misconception is not None
        assert response.possible_misconception.type == "parameter_shadowing_confusion"
        assert response.created_at is not None

        # 2. Xác nhận prompt context được xây dựng đầy đủ
        assert len(mock_provider.recorded_messages) == 1
        recorded = mock_provider.recorded_messages[0]
        assert recorded[0]["role"] == "system"
        assert "CodeSense AI" in recorded[0]["content"]
        assert "Mức 1" in recorded[0]["content"]

        user_content = recorded[1]["content"]
        assert "Xây dựng lớp Rectangle" in user_content
        assert "CS0169" in user_content
        assert "Em khai báo thuộc tính như thế này đúng chuẩn OOP chưa ạ?" in user_content
        assert "encapsulation" in user_content

    @pytest.mark.anyio
    async def test_input_normalization(self):
        """Kiểm thử việc làm sạch và chuẩn hóa khoảng trắng của dữ liệu đầu vào."""
        mock_provider = DeterministicMockTutorProvider()
        service = TutorService(llm_provider=mock_provider)

        request = TutorRequest(
            problem_statement="   Đề bài có khoảng trắng đầu cuối.   ",
            student_code="   class MyClass {}   ",
            compiler_error="   CS1002 ; expected   ",
            student_question="   Hỏi về lỗi dấu chấm phẩy   ",
            topic="   syntax   ",
            hint_level=2,
        )

        await service.generate_feedback(request)

        user_prompt = mock_provider.recorded_messages[0][1]["content"]
        assert "Đề bài có khoảng trắng đầu cuối." in user_prompt
        assert "class MyClass {}" in user_prompt
        assert "CS1002 ; expected" in user_prompt
        assert "Hỏi về lỗi dấu chấm phẩy" in user_prompt

    @pytest.mark.anyio
    async def test_provider_error_produces_controlled_service_error(self):
        """Acceptance: Provider errors produce a controlled service error."""
        mock_provider = DeterministicMockTutorProvider(
            error_to_raise=TutorProviderError("Kết nối timeout đến LLM provider", retryable=True, status_code=504)
        )
        service = TutorService(llm_provider=mock_provider)

        request = sample_request()
        with pytest.raises(TutorServiceError) as exc_info:
            await service.generate_feedback(request)

        err = exc_info.value
        assert err.error_code == "provider_error"
        assert err.status_code == 502
        assert "Dịch vụ AI gia sư hiện không thể phản hồi" in str(err)
        assert isinstance(err.original_exc, TutorProviderError)

    @pytest.mark.anyio
    async def test_no_hidden_keyword_fallback_on_failure(self):
        """Acceptance: No hidden keyword-based 'AI' silently pretends to be the LLM."""
        # Khi provider gặp lỗi, TutorService KHÔNG ĐƯỢC phép fallback ngầm thành keyword matching
        mock_provider = DeterministicMockTutorProvider(
            error_to_raise=TutorProviderError("Model quota exceeded")
        )
        service = TutorService(llm_provider=mock_provider)

        request = sample_request()
        with pytest.raises(TutorServiceError):
            await service.generate_feedback(request)

    @pytest.mark.anyio
    async def test_invalid_json_from_provider_raises_service_error(self):
        """Khi LLM trả về chuỗi văn bản không phải JSON hoặc hỏng, service phải báo lỗi có kiểm soát."""
        mock_provider = DeterministicMockTutorProvider(
            canned_response="Xin chào, tôi là AI! Đây là đoạn mã giải bài: ..."
        )
        service = TutorService(llm_provider=mock_provider)

        request = sample_request()
        with pytest.raises(TutorServiceError) as exc_info:
            await service.generate_feedback(request)

        err = exc_info.value
        assert err.error_code == "invalid_model_output"
        assert "Không thể xử lý kết quả chẩn đoán" in str(err)

    @pytest.mark.anyio
    async def test_markdown_wrapped_json_parsing(self):
        """Khi LLM bọc JSON trong ```json ... ```, validator tự động bóc tách thành công."""
        payload = DeterministicMockTutorProvider.default_canned_payload()
        dumped_json = json.dumps(payload, ensure_ascii=False)
        wrapped_text = f"```json\n{dumped_json}\n```"

        mock_provider = DeterministicMockTutorProvider(canned_response=wrapped_text)
        service = TutorService(llm_provider=mock_provider)

        request = sample_request()
        response = await service.generate_feedback(request)

        assert response.diagnosis.issue_type == "semantic_error"
        assert response.solution_revealed is False

    @pytest.mark.anyio
    @pytest.mark.parametrize("hint_lvl", [1, 2, 3])
    async def test_hint_levels_reflected_in_prompt_and_response(self, hint_lvl):
        mock_provider = DeterministicMockTutorProvider()
        service = TutorService(llm_provider=mock_provider)

        request = sample_request(hint_level=hint_lvl)
        response = await service.generate_feedback(request)

        assert response.hint_level == hint_lvl
        sys_prompt = mock_provider.recorded_messages[0][0]["content"]
        assert f"Mức {hint_lvl}" in sys_prompt


class TestOpenAITutorProvider:
    @pytest.mark.anyio
    async def test_wraps_llm_client_error(self):
        mock_llm_client = AsyncMock(spec=OpenAICompatibleLLMClient)
        mock_llm_client.chat_completion.side_effect = LLMClientError("503 Service Unavailable", retryable=True)

        provider = OpenAITutorProvider(client=mock_llm_client)

        with pytest.raises(TutorProviderError) as exc_info:
            await provider.generate_response([{"role": "user", "content": "hello"}])

        assert "503 Service Unavailable" in str(exc_info.value)
        assert exc_info.value.retryable is True
