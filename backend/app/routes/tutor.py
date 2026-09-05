import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.database.connection import get_db
from app.deps.auth import CurrentUser, get_optional_user
from app.schemas.tutor_schema import TutorRequest, TutorResponse
from app.services.db_store import ConsentRepository, HistoryRepository
from app.services.rate_limiter import analyze_rate_limiter
from app.tutor.service import TutorService, TutorServiceError

logger = logging.getLogger(__name__)

router = APIRouter()


def get_tutor_service() -> TutorService:
    """Dependency cung cấp instance của TutorService (hỗ trợ override trong unit tests)."""
    return TutorService()


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
    try:
        feedback_result = await tutor_service.generate_feedback(request)
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

    # 5. Gán session_id và trả về kết quả
    if session_id:
        feedback_result = feedback_result.model_copy(update={"session_id": session_id})

    return feedback_result
