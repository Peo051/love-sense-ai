from fastapi import APIRouter, HTTPException, status

router = APIRouter()


@router.post("/analyze", deprecated=True)
async def analyze_deprecated():
    """API phân tích cảm xúc cũ đã ngừng hoạt động (retired / deprecated)."""
    raise HTTPException(
        status_code=status.HTTP_410_GONE,
        detail="API phân tích cảm xúc (/api/analyze) đã ngừng hoạt động (deprecated). Vui lòng sử dụng CodeSense Tutor (/tutor).",
    )


@router.get("/analyze", deprecated=True)
async def analyze_get_deprecated():
    """API phân tích cảm xúc cũ đã ngừng hoạt động (retired / deprecated)."""
    raise HTTPException(
        status_code=status.HTTP_410_GONE,
        detail="API phân tích cảm xúc (/api/analyze) đã ngừng hoạt động (deprecated). Vui lòng sử dụng CodeSense Tutor (/tutor).",
    )

