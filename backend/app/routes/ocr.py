from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from app.schemas.ocr_schema import VisionOcrResponse
from app.services.vision_ocr_service import VisionOcrService, VisionOcrServiceError

router = APIRouter()

MAX_VISION_IMAGE_SIZE_BYTES = 5 * 1024 * 1024
ALLOWED_VISION_IMAGE_TYPES = {"image/png", "image/jpeg", "image/webp"}


@router.post("/ocr/vision", response_model=VisionOcrResponse)
async def extract_chat_text_with_vision(
    image: UploadFile = File(...),
    is_accepted: bool = Form(False),
):
    if not is_accepted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bạn cần đồng ý gửi ảnh đến AI provider trước khi dùng Vision OCR.",
        )

    if image.content_type not in ALLOWED_VISION_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vui lòng tải ảnh PNG, JPG, JPEG hoặc WEBP.",
        )

    image_bytes = await image.read()
    if not image_bytes:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ảnh tải lên đang rỗng.")

    if len(image_bytes) > MAX_VISION_IMAGE_SIZE_BYTES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ảnh tối đa 5MB.")

    try:
        return await VisionOcrService().extract_chat_text_from_image(image_bytes, image.content_type)
    except VisionOcrServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc) or "Vision AI chưa sẵn sàng. Vui lòng dùng OCR local hoặc nhập thủ công.",
        ) from exc
