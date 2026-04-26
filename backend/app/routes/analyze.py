from fastapi import APIRouter, HTTPException

from app.schemas.analyze_schema import AnalyzeRequest, AnalyzeResponse
from app.services.ai_service import AIService
from app.services.memory_store import ConsentService, HistoryService
from app.services.preprocessing import preprocess_text
from app.services.safety_filter import SafetyFilter

router = APIRouter()


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_emotion(request: AnalyzeRequest):
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

        # Không lưu mặc định. Chỉ lưu khi người dùng bật checkbox đồng ý trong request.
        ConsentService.accept_analysis_consent(
            save_input=request.save_input,
            save_result=request.save_result or request.save_input,
        )
        HistoryService.save_analysis(
            chat_text=cleaned_text,
            result=result,
            save_input=request.save_input,
            save_result=request.save_result or request.save_input,
        )

        return result
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Không thể phân tích đoạn chat lúc này.") from exc
