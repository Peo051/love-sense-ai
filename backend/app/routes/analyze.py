from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.auth import get_optional_user_from_token, optional_oauth2_scheme
from app.core.exceptions import AIServiceException
from app.database.connection import get_db
from app.schemas.analyze_schema import AnalyzeRequest, AnalyzeResponse
from app.services.ai_service import AIService
from app.services.db_store import ConsentRepository, HistoryRepository
from app.services.preprocessing import preprocess_text
from app.services.rate_limiter import analyze_rate_limiter
from app.services.safety_filter import SafetyFilter

router = APIRouter()


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_emotion(
    http_request: Request,
    request: AnalyzeRequest,
    token: str | None = Depends(optional_oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):
    try:
        cleaned_text = preprocess_text(request.chat_text)

        if not cleaned_text:
            raise HTTPException(status_code=400, detail="Vui lòng nhập đoạn chat cần phân tích.")

        if not SafetyFilter.is_safe(cleaned_text):
            raise HTTPException(
                status_code=400,
                detail="Nội dung này không phù hợp với mục tiêu phân tích an toàn của ứng dụng.",
            )

        current_user = await get_optional_user_from_token(token, db)
        rate_limit_key = _build_rate_limit_key(http_request, current_user.id if current_user else None)
        rate_limit = analyze_rate_limiter.check(
            rate_limit_key,
            limit=settings.analyze_rate_limit_requests,
            window_seconds=settings.analyze_rate_limit_window_seconds,
        )
        if not rate_limit.allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Bạn đang phân tích quá nhanh. Vui lòng chờ một chút rồi thử lại.",
                headers={"Retry-After": str(rate_limit.retry_after_seconds)},
            )

        ai_service = AIService()
        result = await ai_service.analyze_emotion(cleaned_text, request.profile_context)

        # Analyze luôn dùng được không cần đăng nhập; chỉ lưu lịch sử khi có user và request có consent lưu.
        if current_user and (request.save_input or request.save_result):
            await ConsentRepository.accept_analysis_consent(
                db,
                current_user.id,
                save_input=request.save_input,
                save_result=request.save_result or request.save_input,
            )
            await HistoryRepository.save_analysis(
                db,
                current_user.id,
                chat_text=cleaned_text,
                result=result,
                save_input=request.save_input,
                save_result=request.save_result or request.save_input,
            )

        return result
    except HTTPException:
        raise
    except AIServiceException as exc:
        raise HTTPException(status_code=502, detail=str(exc) or "LLM provider chưa sẵn sàng.") from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Không thể phân tích đoạn chat lúc này.") from exc


def _build_rate_limit_key(request: Request, user_id: str | None) -> str:
    if user_id:
        return f"user:{user_id}"

    client_host = request.client.host if request.client else "unknown"
    return f"ip:{client_host}"
