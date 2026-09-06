import logging
from datetime import datetime, timezone
from typing import Optional

from app.schemas.tutor_schema import TutorDiagnosis, TutorRequest, TutorResponse
from app.tutor.diagnosis import DiagnosisSubsystem
from app.tutor.hint_manager import HintManager, HintPayload, HintSessionState
from app.tutor.prompts import build_tutor_system_prompt, build_tutor_user_prompt
from app.tutor.provider import OpenAITutorProvider, TutorLLMProvider, TutorProviderError
from app.tutor.validator import TutorOutputValidationError, TutorOutputValidator

logger = logging.getLogger(__name__)


class TutorServiceError(Exception):
    """Lỗi nghiệp vụ có kiểm soát từ TutorService."""

    def __init__(
        self,
        message: str,
        *,
        error_code: str = "tutor_service_error",
        status_code: int = 502,
        original_exc: Optional[Exception] = None,
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.original_exc = original_exc


class TutorService:
    """
    Lớp điều phối (Orchestration Layer) trung tâm của CodeSense AI Tutor.
    
    Đảm bảo 6 trách nhiệm cốt lõi:
    1. Chuẩn hóa input (normalize problem, code, error, question, topic).
    2. Xây dựng ngữ cảnh sư phạm (build tutor context: system prompt, user prompt).
    3. Yêu cầu chẩn đoán cấu trúc từ LLM (request structured diagnosis).
    4. Lựa chọn hành động / chiến lược sư phạm thích ứng (select tutoring action).
    5. Kiểm định tính hợp lệ và có căn cứ của đầu ra (validate output & evidence grounding).
    6. Đóng gói TutorResponse hoàn chỉnh kèm quản lý tiến trình gợi ý (progressive hint system).
    """

    def __init__(
        self,
        llm_provider: Optional[TutorLLMProvider] = None,
        hint_manager: Optional[HintManager] = None,
    ):
        self._llm_provider: TutorLLMProvider = llm_provider or OpenAITutorProvider()
        self._hint_manager: HintManager = hint_manager or HintManager()

    @property
    def hint_manager(self) -> HintManager:
        """Truy cập đối tượng HintManager."""
        return self._hint_manager

    async def generate_feedback(
        self,
        request: TutorRequest,
        session_id: Optional[str] = None,
        allow_jump_to_solution: bool = False,
    ) -> TutorResponse:
        """
        Thực hiện chu trình điều phối hướng dẫn học tập cho một yêu cầu từ sinh viên.
        Nếu truyền session_id, hệ thống áp dụng tiến trình gợi ý tất định (progressive hint progression).
        """
        # 1. Normalize problem/code/error input
        normalized_inputs = self._normalize_inputs(request)

        # Quản lý mức độ gợi ý thông qua HintManager nếu có session_id
        effective_hint_level = normalized_inputs["hint_level"]
        highest_hint_level_used = normalized_inputs["hint_level"]

        if session_id:
            session_state = self._hint_manager.advance_hint(
                session_id=session_id,
                requested_level=normalized_inputs["hint_level"],
                allow_jump_to_solution=allow_jump_to_solution,
            )
            effective_hint_level = session_state.current_hint_level
            highest_hint_level_used = session_state.highest_hint_level_used

        # 2. Build tutor context
        messages = self._build_context(
            problem_statement=normalized_inputs["problem_statement"],
            student_code=normalized_inputs["student_code"],
            compiler_error=normalized_inputs["compiler_error"],
            student_question=normalized_inputs["student_question"],
            topic=normalized_inputs["topic"],
            hint_level=effective_hint_level,
        )

        # 3. Request structured diagnosis
        raw_output = await self._call_provider(messages)

        # 4 & 5. Validate output & evidence grounding
        validated_response = self._validate_and_finalize_output(
            raw_output=raw_output,
            requested_hint_level=effective_hint_level,
            highest_hint_level_used=highest_hint_level_used,
            has_compiler_error=bool(normalized_inputs["compiler_error"]),
            student_code=normalized_inputs["student_code"],
            compiler_error=normalized_inputs["compiler_error"],
            problem_statement=normalized_inputs["problem_statement"],
        )

        # 6. Construct complete TutorResponse
        return validated_response

    def request_next_hint(
        self,
        session_id: str,
        diagnosis: TutorDiagnosis,
        student_code: Optional[str] = None,
        allow_jump_to_solution: bool = False,
    ) -> HintPayload:
        """
        Yêu cầu gợi ý tiếp theo từ session một cách trực tiếp mà không cần gọi lại LLM.
        """
        session_state = self._hint_manager.advance_hint(
            session_id=session_id,
            allow_jump_to_solution=allow_jump_to_solution,
        )
        return self._hint_manager.generate_progressive_hint(
            diagnosis=diagnosis,
            hint_level=session_state.current_hint_level,
            student_code=student_code,
        )

    def diagnose_submission(
        self,
        student_code: str,
        compiler_error: Optional[str] = None,
        problem_statement: Optional[str] = None,
    ) -> TutorDiagnosis:
        """Thực hiện chẩn đoán tĩnh nhanh dựa trên taxonomy và heuristics."""
        return DiagnosisSubsystem.diagnose(
            student_code=student_code,
            compiler_error=compiler_error,
            problem_statement=problem_statement,
        )

    def _normalize_inputs(self, request: TutorRequest) -> dict[str, any]:
        """Chuẩn hóa dữ liệu đầu vào, loại bỏ khoảng trắng dư thừa."""
        return {
            "problem_statement": request.problem_statement.strip(),
            "student_code": request.student_code.strip(),
            "compiler_error": request.compiler_error.strip() if request.compiler_error else None,
            "student_question": request.student_question.strip() if request.student_question else None,
            "topic": request.topic.strip() if request.topic else None,
            "hint_level": int(request.hint_level),
            "save_input": bool(request.save_input),
            "save_result": bool(request.save_result),
        }

    def _build_context(
        self,
        *,
        problem_statement: str,
        student_code: str,
        compiler_error: Optional[str],
        student_question: Optional[str],
        topic: Optional[str],
        hint_level: int,
    ) -> list[dict[str, str]]:
        """Xây dựng prompt theo phương pháp Socratic và mức độ gợi ý mong muốn."""
        system_prompt = build_tutor_system_prompt(hint_level=hint_level)
        user_prompt = build_tutor_user_prompt(
            problem_statement=problem_statement,
            student_code=student_code,
            compiler_error=compiler_error,
            student_question=student_question,
            topic=topic,
            hint_level=hint_level,
        )
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

    async def _call_provider(self, messages: list[dict[str, str]]) -> str:
        """
        Gọi LLM Provider một cách an toàn. Bắt và chuẩn hóa các lỗi kết nối.
        TUYỆT ĐỐI KHÔNG fallback âm thầm sang keyword matching giả lập.
        """
        try:
            return await self._llm_provider.generate_response(messages, temperature=0.2)
        except TutorProviderError as exc:
            logger.error("LLM Provider gặp sự cố khi tạo chẩn đoán: %s", str(exc))
            raise TutorServiceError(
                f"Dịch vụ AI gia sư hiện không thể phản hồi: {str(exc)}",
                error_code="provider_error",
                status_code=502,
                original_exc=exc,
            ) from exc
        except Exception as exc:
            logger.error("Lỗi không mong muốn khi gọi AI provider: %s", str(exc))
            raise TutorServiceError(
                f"Đã xảy ra lỗi khi liên lạc với mô hình gia sư: {str(exc)}",
                error_code="unexpected_provider_error",
                status_code=500,
                original_exc=exc,
            ) from exc

    def _validate_and_finalize_output(
        self,
        raw_output: str,
        requested_hint_level: int,
        highest_hint_level_used: Optional[int] = None,
        has_compiler_error: bool = False,
        student_code: Optional[str] = None,
        compiler_error: Optional[str] = None,
        problem_statement: Optional[str] = None,
        reference_solution: Optional[str] = None,
    ) -> TutorResponse:
        """Parse, validate và bổ sung chiến lược sư phạm nếu cần thiết."""
        try:
            response = TutorOutputValidator.parse_and_validate(
                raw_output,
                requested_hint_level=requested_hint_level,
                student_code=student_code,
                compiler_error=compiler_error,
                problem_statement=problem_statement,
                reference_solution=reference_solution,
            )
        except TutorOutputValidationError as exc:
            logger.error("Đầu ra từ LLM không vượt qua validation: %s", str(exc))
            raise TutorServiceError(
                f"Không thể xử lý kết quả chẩn đoán từ mô hình gia sư: {str(exc)}",
                error_code="invalid_model_output",
                status_code=502,
                original_exc=exc,
            ) from exc

        # 4. Select / refine tutoring action nếu cần thiết
        teaching_strategy = response.teaching_strategy
        if not teaching_strategy or teaching_strategy.strip() == "":
            if has_compiler_error:
                teaching_strategy = "compiler_error_guidance"
            elif requested_hint_level == 1:
                teaching_strategy = "socratic_questioning"
            elif requested_hint_level == 2:
                teaching_strategy = "conceptual_clue"
            elif requested_hint_level == 3:
                teaching_strategy = "directed_hint"
            else:
                teaching_strategy = "explicit_solution_scaffolding"

        # 6. Construct TutorResponse hoàn chỉnh với timestamp và prompt_version
        response_dict = response.model_dump()
        response_dict["teaching_strategy"] = teaching_strategy
        response_dict["hint_level"] = requested_hint_level
        response_dict["highest_hint_level_used"] = highest_hint_level_used or requested_hint_level
        response_dict["prompt_version"] = getattr(response, "prompt_version", "v1")
        response_dict["created_at"] = datetime.now(timezone.utc)

        return TutorResponse.model_validate(response_dict)
