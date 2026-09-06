import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.deps.auth import CurrentUser, get_current_user
from app.schemas.student_profile_schema import (
    StudentProfileDeleteResponse,
    StudentProfileRequest,
    StudentProfileResponse,
)
from app.services.student_profile_store import StudentProfileRepository

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/student-profile", response_model=StudentProfileResponse)
async def get_student_profile(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> StudentProfileResponse:
    """
    GET /api/student-profile
    Lấy thông tin hồ sơ học tập của sinh viên hiện tại.
    Trả về 404 Not Found nếu sinh viên chưa tạo hồ sơ học tập.
    """
    profile = await StudentProfileRepository.get_profile(db, current_user.id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hồ sơ sinh viên chưa được khởi tạo. Vui lòng tạo hồ sơ mới.",
        )
    return profile


@router.post("/student-profile", response_model=StudentProfileResponse)
async def save_student_profile(
    request: StudentProfileRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> StudentProfileResponse:
    """
    POST /api/student-profile
    Khởi tạo hoặc cập nhật hồ sơ học tập của sinh viên.
    Chỉ chấp nhận các trường sư phạm C# OOP; tuyệt đối cấm các trường cá nhân/tình cảm.
    """
    logger.info("Lưu hồ sơ sinh viên cho user_id=%s", current_user.id)
    return await StudentProfileRepository.save_profile(db, current_user.id, request)


@router.delete("/student-profile", response_model=StudentProfileDeleteResponse)
async def delete_student_profile(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> StudentProfileDeleteResponse:
    """
    DELETE /api/student-profile
    Xóa hồ sơ học tập của sinh viên.
    """
    deleted = await StudentProfileRepository.delete_profile(db, current_user.id)
    return StudentProfileDeleteResponse(deleted=deleted)
