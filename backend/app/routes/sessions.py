import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.deps.auth import CurrentUser, get_current_user
from app.schemas.mastery_audit_schema import (
    AttemptOutcomeResolutionRequest,
    AttemptOutcomeResolutionResponse,
    MasteryAuditResponse,
)
from app.schemas.session_schema import (
    AttemptCreateRequest,
    MessageCreateRequest,
    SessionCreateRequest,
    SessionDeleteResponse,
    SessionDetailResponse,
    SessionSummaryResponse,
    StudentAttemptResponse,
    TutorMessageResponse,
)
from app.services.attempt_mastery_coordinator import AttemptMasteryCoordinator
from app.services.session_store import SessionRepository

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/sessions", response_model=SessionDetailResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    request: SessionCreateRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SessionDetailResponse:
    """
    POST /api/sessions
    Khởi tạo một phiên học tập đa lượt mới cho người dùng đã đăng nhập.
    """
    logger.info("Tạo phiên học tập mới cho user_id=%s, title=%s", current_user.id, request.title)
    return await SessionRepository.create_session(db, current_user.id, request)


@router.get("/sessions", response_model=list[SessionSummaryResponse])
async def list_sessions(
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[SessionSummaryResponse]:
    """
    GET /api/sessions
    Lấy danh sách các phiên học tập của người dùng hiện tại (Strict User Ownership).
    """
    return await SessionRepository.list_user_sessions(db, current_user.id, limit=limit, offset=offset)


@router.get("/sessions/{session_id}", response_model=SessionDetailResponse)
async def get_session(
    session_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SessionDetailResponse:
    """
    GET /api/sessions/{id}
    Lấy chi tiết phiên học tập bao gồm lịch sử các lần thử (attempts) và tin nhắn (messages).
    Nếu phiên không tồn tại hoặc thuộc về người dùng khác, trả về 404 Not Found để bảo mật ID.
    """
    session = await SessionRepository.get_user_session(db, current_user.id, session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy phiên học tập yêu cầu.",
        )
    return session


@router.delete("/sessions/{session_id}", response_model=SessionDeleteResponse)
async def delete_session(
    session_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SessionDeleteResponse:
    """
    DELETE /api/sessions/{id}
    Xóa phiên học tập và toàn bộ các lần thử, tin nhắn liên quan (cascade delete).
    Chỉ cho phép người sở hữu phiên thực hiện. Nếu sai trả về 404 Not Found.
    """
    deleted = await SessionRepository.delete_user_session(db, current_user.id, session_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy phiên học tập yêu cầu để xóa.",
        )
    return SessionDeleteResponse(deleted=True, id=session_id)


@router.post("/sessions/{session_id}/attempts", response_model=StudentAttemptResponse, status_code=status.HTTP_201_CREATED)
async def add_session_attempt(
    session_id: str,
    request: AttemptCreateRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> StudentAttemptResponse:
    """
    POST /api/sessions/{id}/attempts
    Ghi nhận một lần thử làm bài mới trong phiên học (tuân thủ cờ save_input).
    """
    attempt = await SessionRepository.add_attempt(db, current_user.id, session_id, request)
    if not attempt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy phiên học tập để thêm bài nộp.",
        )
    return attempt


@router.post("/sessions/{session_id}/messages", response_model=TutorMessageResponse, status_code=status.HTTP_201_CREATED)
async def add_session_message(
    session_id: str,
    request: MessageCreateRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> TutorMessageResponse:
    """
    POST /api/sessions/{id}/messages
    Gửi tin nhắn mới trong chuỗi trao đổi đa lượt của phiên học.
    """
    message = await SessionRepository.add_message(db, current_user.id, session_id, request)
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy phiên học tập để gửi tin nhắn.",
        )
    return message


@router.post(
    "/sessions/{session_id}/attempts/{attempt_id}/resolve",
    response_model=AttemptOutcomeResolutionResponse,
    summary="Xác nhận kết quả lần thử và kích hoạt cập nhật độ thuần thục kỹ năng giao dịch",
)
async def resolve_session_attempt(
    session_id: str,
    attempt_id: str,
    payload: AttemptOutcomeResolutionRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> AttemptOutcomeResolutionResponse:
    """
    POST /api/sessions/{session_id}/attempts/{attempt_id}/resolve
    Kết luận kết quả một lần thử bài (resolved, failed, solution_revealed, etc.)
    và cập nhật transactional điểm mastery cho các kỹ năng liên quan kèm audit log.
    Bảo đảm duplicate-event replay protection (idempotent).
    """
    attempt, audits = await AttemptMasteryCoordinator.resolve_attempt_and_update_mastery(
        db,
        user_id=current_user.id,
        attempt_id=attempt_id,
        outcome=payload.outcome,
        highest_hint_level=payload.highest_hint_level,
        solution_revealed=payload.solution_revealed,
        hints_used=payload.hints_used,
        custom_reason=payload.custom_reason,
    )
    if not attempt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy bài làm yêu cầu hoặc bạn không có quyền sở hữu.",
        )

    return AttemptOutcomeResolutionResponse(
        attempt_id=attempt.id,
        success_state=attempt.success_state,
        audit_records=[
            MasteryAuditResponse.model_validate(a) for a in audits
        ],
    )

