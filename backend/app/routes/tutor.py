import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.database.connection import get_db
from app.deps.auth import CurrentUser, get_optional_user
from app.schemas.tutor_schema import (
    TutorDiagnosis,
    TutorHintRequest,
    TutorHintResponse,
    TutorRequest,
    TutorResponse,
    TutorVerifyRequest,
    TutorVerifyResponse,
    VerificationStatus,
)
from app.services.db_store import ConsentRepository, HistoryRepository
from app.services.rate_limiter import analyze_rate_limiter
from app.tutor.context_builder import StudentContextBuilder
from app.tutor.guest_context import GuestContextError, GuestContextSigner, GuestContextTamperedError
from app.tutor.hint_manager import HintManager
from app.tutor.service import TutorService, TutorServiceError
from app.tutor.verification import VerificationService

logger = logging.getLogger(__name__)

router = APIRouter()


def get_tutor_service() -> TutorService:
    """Dependency cung cấp instance của TutorService (hỗ trợ override trong unit tests)."""
    return TutorService()


def get_verification_service() -> VerificationService:
    """Dependency cung cấp instance của VerificationService (hỗ trợ override trong unit tests)."""
    return VerificationService()


def _build_rate_limit_key(request: Request, user_id: Optional[str]) -> str:
    """Sinh khóa định danh rate limiter dựa trên User ID hoặc IP Client."""
    if user_id:
        return f"tutor:user:{user_id}"
    client_host = request.client.host if request.client else "unknown"
    return f"tutor:ip:{client_host}"


@router.post("/analyze", response_model=TutorResponse)
async def analyze_code(
    http_request: Request,
    request: TutorRequest,
    current_user: Optional[CurrentUser] = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db),
    tutor_service: TutorService = Depends(get_tutor_service),
) -> TutorResponse:
    """
    POST /api/tutor/analyze
    
    Quy trình điều phối (Flow):
    request
    → validate (Pydantic validation, ngôn ngữ csharp, độ dài)
    → normalize (làm sạch khoảng trắng trong TutorService)
    → optional authentication (CurrentUser hoặc Guest)
    → rate limit (kiểm tra tần suất theo User ID hoặc IP)
    → TutorService (xây dựng prompt, chẩn đoán, lựa chọn chiến lược sư phạm)
    → output validation (kiểm tra an toàn sư phạm, không lộ giải pháp ở level < 4)
    → optional persistence when consent permits (chỉ lưu cho Authenticated user có consent; Guest không lưu)
    → response
    """
    # 1. Bảo mật: Tuyệt đối không log raw student code
    logger.info(
        "Nhận yêu cầu gia sư: user_id=%s, hint_level=%d, problem_len=%d, code_len=%d, has_error=%s",
        current_user.id if current_user else "guest",
        request.hint_level,
        len(request.problem_statement),
        len(request.student_code),
        bool(request.compiler_error),
    )

    # 2. Kiểm tra Rate Limit
    rate_limit_key = _build_rate_limit_key(http_request, current_user.id if current_user else None)
    rate_decision = analyze_rate_limiter.check(
        rate_limit_key,
        limit=settings.analyze_rate_limit_requests,
        window_seconds=settings.analyze_rate_limit_window_seconds,
    )
    if not rate_decision.allowed:
        logger.warning("Rate limit exceeded for key=%s", rate_limit_key)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Bạn đang gửi yêu cầu quá nhanh. Vui lòng chờ một chút trước khi thử lại.",
            headers={"Retry-After": str(rate_decision.retry_after_seconds)},
        )

    # 3. Điều phối qua TutorService
    learner_context = None
    if current_user:
        try:
            target_skills = [request.topic] if request.topic else []
            learner_context = await StudentContextBuilder.load_and_build_learner_context(
                db=db,
                user_id=current_user.id,
                relevant_skills=target_skills,
            )
        except Exception as exc:
            logger.warning("Không thể tải learner context cho user %s: %s", current_user.id, str(exc))

    try:
        feedback_result = await tutor_service.generate_feedback(
            request,
            learner_context=learner_context,
        )
    except TutorServiceError as exc:
        logger.error("TutorService báo lỗi [%s]: %s", exc.error_code, exc.message)
        if exc.error_code == "provider_error":
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=exc.message or "Mô hình AI gia sư hiện không thể phản hồi.",
            ) from exc
        elif exc.error_code == "invalid_model_output":
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=exc.message or "Dữ liệu trả về từ mô hình gia sư không hợp lệ.",
            ) from exc
        else:
            raise HTTPException(
                status_code=exc.status_code or status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=exc.message or "Đã xảy ra sự cố trong quá trình gia sư lập trình.",
            ) from exc
    except Exception as exc:
        logger.error("Lỗi không lường trước trong quá trình gia sư: %s", str(exc), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Hệ thống gia sư gặp sự cố nội bộ. Vui lòng thử lại sau.",
        ) from exc

    # 4. Lưu trữ có điều kiện (Optional persistence when consent permits)
    # GUEST USERS KHÔNG BAO GIỜ ĐƯỢC LƯU LỊCH SỬ VÀO DATABASE
    session_id: Optional[str] = None
    if current_user and (request.save_input or request.save_result):
        try:
            # Cập nhật consent phiên phân tích
            await ConsentRepository.accept_analysis_consent(
                db,
                current_user.id,
                save_input=request.save_input,
                save_result=request.save_result,
            )
            # Lưu session vào database
            saved_item = await HistoryRepository.save_tutor_session(
                db,
                current_user.id,
                problem_statement=request.problem_statement,
                student_code=request.student_code,
                topic=request.topic,
                result=feedback_result,
                save_input=request.save_input,
                save_result=request.save_result,
            )
            if saved_item:
                session_id = saved_item.id
                logger.info("Đã lưu phiên gia sư vào lịch sử học tập: session_id=%s", session_id)
        except Exception as exc:
            # Không làm gián đoạn phản hồi của sinh viên nếu lưu DB gặp sự cố
            logger.error("Lỗi khi lưu lịch sử gia sư: %s", str(exc), exc_info=True)

    # 5. Gán session_id (nếu authenticated) hoặc guest_context_token (nếu guest)
    if session_id:
        feedback_result = feedback_result.model_copy(update={"session_id": session_id})
    elif current_user is None:
        guest_token = GuestContextSigner.sign_guest_context({
            "current_hint_level": feedback_result.hint_level,
            "highest_hint_level_used": feedback_result.highest_hint_level_used,
            "solution_revealed": feedback_result.solution_revealed,
            "diagnosis": feedback_result.diagnosis.model_dump(),
            "student_code": request.student_code,
        })
        feedback_result = feedback_result.model_copy(update={"guest_context_token": guest_token})

    return feedback_result


@router.post("/hint", response_model=TutorHintResponse)
async def request_next_hint(
    http_request: Request,
    request: TutorHintRequest,
    current_user: Optional[CurrentUser] = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db),
    tutor_service: TutorService = Depends(get_tutor_service),
) -> TutorHintResponse:
    """
    POST /api/tutor/hint

    Cung cấp gợi ý cấp độ tiếp theo (Next-Hint) trong chu trình học tập thích ứng.
    Máy chủ toàn quyền kiểm soát chuyển đổi cấp độ tiếp theo (Server-Controlled Progression).
    Chặn đứng mọi nỗ lực thao túng client nhằm reset trạng thái hoặc nhảy cóc cấp độ.
    """
    # 1. Rate Limit Check
    rate_limit_key = _build_rate_limit_key(http_request, current_user.id if current_user else None)
    rate_decision = analyze_rate_limiter.check(
        rate_limit_key,
        limit=settings.analyze_rate_limit_requests,
        window_seconds=settings.analyze_rate_limit_window_seconds,
    )
    if not rate_decision.allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Bạn đang gửi yêu cầu quá nhanh. Vui lòng chờ một chút trước khi thử lại.",
            headers={"Retry-After": str(rate_decision.retry_after_seconds)},
        )

    # 2. Nhánh Authenticated User (Tải và đồng bộ trạng thái qua DB)
    if current_user:
        if not request.session_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Yêu cầu session_id cho phiên gia sư của người dùng đã đăng nhập.",
            )

        session_item = await HistoryRepository.get_tutor_session(db, current_user.id, request.session_id)
        if not session_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy phiên học tập tương ứng.",
            )

        dist = dict(session_item.emotion_distribution or {})
        db_current_level = int(dist.get("hint_level", 1))
        db_highest_level = int(dist.get("highest_hint_level_used", db_current_level))

        # Kiểm tra tính hợp lệ của chuyển đổi (Server controls progression, rejects invalid transitions)
        if request.current_hint_level != db_current_level:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Chuyển đổi cấp độ không hợp lệ: Cấp độ phía client ({request.current_hint_level}) không khớp với trạng thái phiên học trên máy chủ ({db_current_level}).",
            )

        next_level = min(4, db_current_level + 1)
        highest_level = max(db_highest_level, next_level)

        diag_raw = dist.get("diagnosis")
        if diag_raw:
            diagnosis_obj = TutorDiagnosis.model_validate(diag_raw)
        elif request.current_diagnosis:
            diagnosis_obj = request.current_diagnosis
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Không tìm thấy dữ liệu chẩn đoán của phiên học để sinh gợi ý tiếp theo.",
            )

        student_code = session_item.chat_text or request.student_code
        hint_payload = HintManager.generate_progressive_hint(
            diagnosis=diagnosis_obj,
            hint_level=next_level,
            student_code=student_code,
        )

        await HistoryRepository.update_tutor_hint_progression(
            db=db,
            user_id=current_user.id,
            session_id=request.session_id,
            next_level=next_level,
            hint_payload=hint_payload,
        )

        return TutorHintResponse(
            hint_level=next_level,
            highest_hint_level_used=highest_level,
            tutor_response=hint_payload.tutor_response,
            solution_revealed=hint_payload.solution_revealed,
            next_action=hint_payload.next_action,
            teaching_strategy=hint_payload.teaching_strategy,
            session_id=request.session_id,
        )

    # 3. Nhánh Stateless Guest Mode (Sử dụng signed guest_context_token, zero persistence)
    if request.guest_context_token:
        try:
            payload = GuestContextSigner.verify_guest_context(request.guest_context_token)
        except (GuestContextTamperedError, GuestContextError) as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Token ngữ cảnh guest không hợp lệ hoặc đã bị can thiệp: {str(exc)}",
            ) from exc

        token_current_level = int(payload.get("current_hint_level", 1))
        token_highest_level = int(payload.get("highest_hint_level_used", token_current_level))

        # Chống gian lận: client không được gửi current_hint_level lệch với signed token
        if request.current_hint_level != token_current_level:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Chuyển đổi cấp độ không hợp lệ: Cấp độ client ({request.current_hint_level}) không khớp với phiên làm việc ({token_current_level}).",
            )

        next_level = min(4, token_current_level + 1)
        highest_level = max(token_highest_level, next_level)

        diag_raw = payload.get("diagnosis") or (request.current_diagnosis.model_dump() if request.current_diagnosis else None)
        if not diag_raw:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Thiếu thông tin chẩn đoán kỹ thuật để sinh gợi ý tiếp theo.",
            )

        diagnosis_obj = TutorDiagnosis.model_validate(diag_raw)
        student_code = payload.get("student_code") or request.student_code
    else:
        # Nếu không có token, chỉ cho phép nếu bắt đầu từ Level 1 và có chẩn đoán
        if request.current_hint_level == 1 and request.current_diagnosis:
            next_level = 2
            highest_level = 2
            diagnosis_obj = request.current_diagnosis
            student_code = request.student_code
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Yêu cầu guest_context_token hợp lệ để tiếp tục gợi ý ở cấp độ tiếp theo.",
            )

    hint_payload = HintManager.generate_progressive_hint(
        diagnosis=diagnosis_obj,
        hint_level=next_level,
        student_code=student_code,
    )

    new_guest_token = GuestContextSigner.sign_guest_context({
        "current_hint_level": next_level,
        "highest_hint_level_used": highest_level,
        "solution_revealed": hint_payload.solution_revealed,
        "diagnosis": diagnosis_obj.model_dump(),
        "student_code": student_code,
    })

    return TutorHintResponse(
        hint_level=next_level,
        highest_hint_level_used=highest_level,
        tutor_response=hint_payload.tutor_response,
        solution_revealed=hint_payload.solution_revealed,
        next_action=hint_payload.next_action,
        teaching_strategy=hint_payload.teaching_strategy,
        guest_context_token=new_guest_token,
    )


@router.post("/verify", response_model=TutorVerifyResponse)
async def verify_retry(
    http_request: Request,
    request: TutorVerifyRequest,
    current_user: Optional[CurrentUser] = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db),
    verification_service: VerificationService = Depends(get_verification_service),
) -> TutorVerifyResponse:
    """
    POST /api/tutor/verify

    Xác minh lần thử lại (retry) của sinh viên sau khi nhận gợi ý sư phạm.
    Nguyên tắc bảo mật:
    - Tuyệt đối không thực thi mã C# tùy ý trực tiếp trên production backend.
    - Phân tích tĩnh, so khớp mẫu chuẩn và chẩn đoán cấu trúc.
    - Không mạo nhận kiểm tra tĩnh/LLM tương đương với việc biên dịch/chạy thử mã nguồn.
    """
    # 1. Rate Limit Check
    rate_limit_key = _build_rate_limit_key(http_request, current_user.id if current_user else None)
    rate_decision = analyze_rate_limiter.check(
        rate_limit_key,
        limit=settings.analyze_rate_limit_requests,
        window_seconds=settings.analyze_rate_limit_window_seconds,
    )
    if not rate_decision.allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Bạn đang gửi yêu cầu quá nhanh. Vui lòng chờ một chút trước khi thử lại.",
            headers={"Retry-After": str(rate_decision.retry_after_seconds)},
        )

    # 2. Bổ sung ngữ cảnh từ DB session nếu là authenticated user và chưa truyền đủ
    if current_user and request.session_id:
        try:
            session_item = await HistoryRepository.get_tutor_session(db, current_user.id, request.session_id)
            if session_item:
                if not request.previous_code and session_item.chat_text:
                    request = request.model_copy(update={"previous_code": session_item.chat_text})
                dist = dict(session_item.emotion_distribution or {})
                if not request.original_diagnosis and "diagnosis" in dist:
                    request = request.model_copy(
                        update={"original_diagnosis": TutorDiagnosis.model_validate(dist["diagnosis"])}
                    )
        except Exception as exc:
            logger.warning("Không thể lấy phiên học từ DB để bổ sung ngữ cảnh xác minh: %s", str(exc))

    # 3. Bổ sung ngữ cảnh từ guest_context_token nếu là stateless guest mode
    elif request.guest_context_token:
        try:
            payload = GuestContextSigner.verify_guest_context(request.guest_context_token)
            if not request.previous_code and payload.get("student_code"):
                request = request.model_copy(update={"previous_code": payload.get("student_code")})
            if not request.original_diagnosis and payload.get("diagnosis"):
                request = request.model_copy(
                    update={"original_diagnosis": TutorDiagnosis.model_validate(payload["diagnosis"])}
                )
        except Exception as exc:
            logger.warning("Không thể giải mã guest_context_token để bổ sung ngữ cảnh: %s", str(exc))

    # 4. Thực hiện xác minh qua VerificationService
    return await verification_service.verify_retry(request)

