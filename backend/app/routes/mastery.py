from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.deps.auth import CurrentUser, get_current_user
from app.schemas.mastery_schema import (
    FormulaDocumentationResponse,
    RecordPracticeAttemptRequest,
    SkillMasteryResponse,
    StudentMasterySummaryResponse,
)
from app.services.mastery_store import MasteryRepository
from app.tutor.mastery import DeterministicMasteryModel
from app.tutor.skill_taxonomy import SkillTaxonomy

router = APIRouter()


@router.get(
    "/mastery/formula",
    response_model=FormulaDocumentationResponse,
    summary="Xem tài liệu công thức tính điểm thuần thục kỹ năng tất định (Inspectable Formula V1)",
)
async def get_mastery_formula() -> Any:
    """
    Trả về công thức toán học, trọng số delta, quy tắc kẹp biên và lý giải sư phạm
    cho mô hình độ thuần thục tất định V1.
    """
    return DeterministicMasteryModel.get_formula_documentation()


@router.get(
    "/mastery",
    response_model=StudentMasterySummaryResponse,
    summary="Xem tổng quan và chi tiết độ thuần thục các kỹ năng C# OOP của sinh viên",
)
async def get_my_masteries(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Lấy danh sách mức độ thuần thục cho toàn bộ taxonomy C# OOP V1.
    Kỹ năng chưa làm bài có điểm khởi tạo trung tính 0.5.
    """
    return await MasteryRepository.get_user_mastery_summary(db, current_user.id)


@router.get(
    "/mastery/{skill_id}",
    response_model=SkillMasteryResponse,
    summary="Xem chi tiết mức độ thuần thục một kỹ năng cụ thể",
)
async def get_single_skill_mastery(
    skill_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Xem điểm thuần thục và các bộ đếm thành công/thất bại/gợi ý của một kỹ năng.
    """
    canonical_skill = SkillTaxonomy.get_skill(skill_id)
    if not canonical_skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Kỹ năng '{skill_id}' không tồn tại trong taxonomy C# OOP.",
        )

    record = await MasteryRepository.get_user_mastery(db, current_user.id, canonical_skill.code)
    if not record:
        # Kỹ năng chưa có tương tác thực tế: trả về trạng thái trung tính 0.5
        return SkillMasteryResponse(
            skill_id=canonical_skill.code,
            skill_name=canonical_skill.name,
            mastery_score=DeterministicMasteryModel.INITIAL_MASTERY,
            success_count=0,
            failure_count=0,
            hint_count=0,
            last_practiced_at=None,
        )

    return SkillMasteryResponse(
        skill_id=record.skill_id,
        skill_name=canonical_skill.name,
        mastery_score=record.mastery_score,
        success_count=record.success_count,
        failure_count=record.failure_count,
        hint_count=record.hint_count,
        last_practiced_at=record.last_practiced_at,
        created_at=record.created_at,
        updated_at=record.updated_at,
    )


@router.post(
    "/mastery/practice",
    response_model=list[SkillMasteryResponse],
    summary="Cập nhật độ thuần thục sau một lần làm bài tập (Deterministic Update)",
)
async def record_practice_attempt(
    payload: RecordPracticeAttemptRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Ghi nhận một sự kiện giải bài (thành công độc lập, qua gợi ý L1, L2/3, mở giải L4 hoặc thất bại)
    và áp dụng công thức tất định cập nhật điểm các kỹ năng liên quan.
    """
    updated_records = await MasteryRepository.record_practice_attempt(
        db,
        user_id=current_user.id,
        skill_ids=payload.skill_ids,
        event=payload.event,
        hints_used=payload.hints_used,
    )

    results: list[SkillMasteryResponse] = []
    for r in updated_records:
        skill_info = SkillTaxonomy.get_skill(r.skill_id)
        results.append(
            SkillMasteryResponse(
                skill_id=r.skill_id,
                skill_name=skill_info.name if skill_info else None,
                mastery_score=r.mastery_score,
                success_count=r.success_count,
                failure_count=r.failure_count,
                hint_count=r.hint_count,
                last_practiced_at=r.last_practiced_at,
                created_at=r.created_at,
                updated_at=r.updated_at,
            )
        )
    return results
