from fastapi import APIRouter, HTTPException

from app.schemas.analyze_schema import AnalyzeRequest, AnalyzeResponse
from app.services.ai_service import AIService
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

        # MVP chưa lưu nội dung chat mặc định.
        # Khi làm lịch sử thật, chỉ lưu nếu người dùng bật save_input và có cơ chế đồng ý rõ ràng.
        ai_service = AIService()
        return await ai_service.analyze_emotion(cleaned_text, request.profile_context)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Không thể phân tích đoạn chat lúc này.") from exc
