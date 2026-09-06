from datetime import datetime, timezone
import logging
from typing import Optional

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.student_profile import StudentProfile
from app.schemas.student_profile_schema import (
    StudentProfileRequest,
    StudentProfileResponse,
)

logger = logging.getLogger(__name__)


class StudentProfileRepository:
    """
    Data access layer quản lý hồ sơ học tập của sinh viên (Student Profile).
    Tách biệt 100% khỏi relationship schema cũ.
    """

    @staticmethod
    async def get_profile(
        db: AsyncSession,
        user_id: str,
    ) -> Optional[StudentProfileResponse]:
        """Lấy hồ sơ sinh viên theo user_id. Trả về None nếu chưa được khởi tạo."""
        result = await db.execute(
            select(StudentProfile).where(StudentProfile.user_id == user_id)
        )
        profile = result.scalar_one_or_none()
        if not profile:
            return None

        return StudentProfileResponse.model_validate(profile)

    @staticmethod
    async def save_profile(
        db: AsyncSession,
        user_id: str,
        request: StudentProfileRequest,
    ) -> StudentProfileResponse:
        """Tạo mới hoặc cập nhật (Upsert) hồ sơ học tập của sinh viên."""
        result = await db.execute(
            select(StudentProfile).where(StudentProfile.user_id == user_id)
        )
        profile = result.scalar_one_or_none()

        preferred_exp_val = (
            request.preferred_explanation.value
            if hasattr(request.preferred_explanation, "value")
            else str(request.preferred_explanation)
        )
        solution_pref_val = (
            request.solution_preference.value
            if hasattr(request.solution_preference, "value")
            else str(request.solution_preference)
        )

        if profile is None:
            profile = StudentProfile(
                user_id=user_id,
                display_name=request.display_name,
                programming_language=request.programming_language,
                skill_level=request.skill_level,
                current_course=request.current_course,
                preferred_explanation=preferred_exp_val,
                solution_preference=solution_pref_val,
            )
            db.add(profile)
        else:
            profile.display_name = request.display_name
            profile.programming_language = request.programming_language
            profile.skill_level = request.skill_level
            profile.current_course = request.current_course
            profile.preferred_explanation = preferred_exp_val
            profile.solution_preference = solution_pref_val
            profile.updated_at = datetime.now(timezone.utc)

        await db.commit()
        await db.refresh(profile)
        logger.info("Đã lưu hồ sơ sinh viên cho user_id=%s", user_id)
        return StudentProfileResponse.model_validate(profile)

    @staticmethod
    async def delete_profile(
        db: AsyncSession,
        user_id: str,
    ) -> bool:
        """Xóa hồ sơ sinh viên của người dùng hiện tại."""
        result = await db.execute(
            delete(StudentProfile).where(StudentProfile.user_id == user_id)
        )
        await db.commit()
        logger.info("Đã xóa hồ sơ sinh viên của user_id=%s", user_id)
        return bool(result.rowcount)
