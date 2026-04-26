from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_optional_current_user
from app.core.exceptions import AIServiceException
from app.database.connection import get_db
from app.models.user import User
from app.schemas.analyze_schema import AnalyzeRequest, AnalyzeResponse
from app.services.ai_service import AIService
from app.services.db_store import ConsentRepository, HistoryRepository
from app.services.preprocessing import preprocess_text
from app.services.safety_filter import SafetyFilter

router = APIRouter()


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_emotion(
    request: AnalyzeRequest,
    current_user: User | None = Depends(get_optional_current_user),
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

        ai_service = AIService()
        result = await ai_service.analyze_emotion(cleaned_text, request.profile_context)

        # Analyze vẫn dùng được khi chưa đăng nhập, nhưng chỉ user có token hợp lệ mới có lịch sử riêng.
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
