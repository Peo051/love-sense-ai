from datetime import datetime, timezone
from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.analysis_session import AnalysisSession
from app.models.consent import Consent
from app.models.learning_session import LearningSession, StudentAttempt, TutorMessage
from app.models.mastery_audit import StudentMasteryAudit
from app.models.partner_profile import PartnerProfile as PartnerProfileModel
from app.models.preference import Preference
from app.models.profile import Profile as ProfileModel
from app.models.student_profile import StudentProfile
from app.models.student_skill_mastery import StudentSkillMastery
from app.models.user import User
from app.schemas.consent_schema import ConsentSettings, ConsentUpdate
from app.schemas.history_schema import HistoryItem, HistoryListResponse
from app.schemas.profile_schema import PartnerProfile, ProfileResponse, ProfileUpsert, UserProfile


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class ProfileRepository:
    @staticmethod
    async def get_profile(db: AsyncSession, user_id: str) -> ProfileResponse:
        profile = await ProfileRepository._get_user_profile_model(db, user_id)
        partner = await ProfileRepository._get_partner_profile_model(db, user_id)
        updated_at = max(
            [value for value in [getattr(profile, "updated_at", None), getattr(partner, "updated_at", None)] if value],
            default=utc_now(),
        )

        return ProfileResponse(
            user_profile=ProfileRepository._to_user_profile(profile),
            partner_profile=ProfileRepository._to_partner_profile(partner),
            updated_at=updated_at,
        )

    @staticmethod
    async def save_profile(db: AsyncSession, user_id: str, profile: ProfileUpsert) -> ProfileResponse:
        user_profile = await ProfileRepository._get_user_profile_model(db, user_id)
        if user_profile is None:
            user_profile = ProfileModel(user_id=user_id)
            db.add(user_profile)

        partner_profile = await ProfileRepository._get_partner_profile_model(db, user_id)
        if partner_profile is None:
            partner_profile = PartnerProfileModel(user_id=user_id)
            db.add(partner_profile)

        for field, value in profile.user_profile.model_dump().items():
            setattr(user_profile, field, value)
        for field, value in profile.partner_profile.model_dump().items():
            setattr(partner_profile, field, value)

        await db.commit()
        await db.refresh(user_profile)
        await db.refresh(partner_profile)
        return await ProfileRepository.get_profile(db, user_id)

    @staticmethod
    async def delete_profile(db: AsyncSession, user_id: str) -> None:
        await db.execute(delete(ProfileModel).where(ProfileModel.user_id == user_id))
        await db.execute(delete(PartnerProfileModel).where(PartnerProfileModel.user_id == user_id))
        await db.commit()

    @staticmethod
    async def _get_user_profile_model(db: AsyncSession, user_id: str) -> ProfileModel | None:
        result = await db.execute(select(ProfileModel).where(ProfileModel.user_id == user_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def _get_partner_profile_model(db: AsyncSession, user_id: str) -> PartnerProfileModel | None:
        result = await db.execute(select(PartnerProfileModel).where(PartnerProfileModel.user_id == user_id))
        return result.scalar_one_or_none()

    @staticmethod
    def _to_user_profile(profile: ProfileModel | None) -> UserProfile:
        if profile is None:
            return UserProfile()
        return UserProfile(
            nickname=profile.nickname,
            primary_language=profile.primary_language,
            communication_style=profile.communication_style,
            relationship_status=profile.relationship_status,
        )

    @staticmethod
    def _to_partner_profile(profile: PartnerProfileModel | None) -> PartnerProfile:
        if profile is None:
            return PartnerProfile()
        return PartnerProfile(
            nickname=profile.nickname,
            likes=profile.likes,
            dislikes=profile.dislikes,
            texting_style=profile.texting_style,
            when_happy=profile.when_happy,
            when_sad=profile.when_sad,
            when_angry=profile.when_angry,
            likes_checkins=profile.likes_checkins,
            dislikes_repeated_questions=profile.dislikes_repeated_questions,
            height_cm=profile.height_cm,
            weight_kg=profile.weight_kg,
            appearance=profile.appearance,
            private_notes=profile.private_notes,
        )


class ConsentRepository:
    @staticmethod
    async def get_consent(db: AsyncSession, user_id: str, consent_type: str = "privacy_settings") -> ConsentSettings:
        consent = await ConsentRepository._get_consent_model(db, user_id, consent_type)
        if consent is None:
            return ConsentSettings(consent_type=consent_type)
        return ConsentRepository._to_schema(consent)

    @staticmethod
    async def save_consent(db: AsyncSession, user_id: str, consent: ConsentUpdate) -> ConsentSettings:
        consent_model = await ConsentRepository._get_consent_model(db, user_id, consent.consent_type)
        if consent_model is None:
            consent_model = Consent(user_id=user_id, consent_type=consent.consent_type)
            db.add(consent_model)

        consent_model.history_enabled = consent.history_enabled
        consent_model.save_input = consent.save_input
        consent_model.save_result = consent.save_result
        consent_model.is_accepted = consent.is_accepted
        consent_model.accepted_at = utc_now() if consent.is_accepted else None

        await db.commit()
        await db.refresh(consent_model)
        return ConsentRepository._to_schema(consent_model)

    @staticmethod
    async def accept_analysis_consent(
        db: AsyncSession,
        user_id: str,
        *,
        save_input: bool,
        save_result: bool,
    ) -> ConsentSettings:
        if not save_input and not save_result:
            return await ConsentRepository.get_consent(db, user_id, "analysis_submission")

        return await ConsentRepository.save_consent(
            db,
            user_id,
            ConsentUpdate(
                history_enabled=True,
                save_input=save_input,
                save_result=save_result,
                consent_type="analysis_submission",
                is_accepted=True,
            ),
        )

    @staticmethod
    async def delete_user_consents(db: AsyncSession, user_id: str) -> None:
        await db.execute(delete(Consent).where(Consent.user_id == user_id))
        await db.commit()

    @staticmethod
    async def _get_consent_model(db: AsyncSession, user_id: str, consent_type: str) -> Consent | None:
        result = await db.execute(
            select(Consent).where(Consent.user_id == user_id, Consent.consent_type == consent_type)
        )
        return result.scalar_one_or_none()

    @staticmethod
    def _to_schema(consent: Consent) -> ConsentSettings:
        return ConsentSettings(
            history_enabled=consent.history_enabled,
            save_input=consent.save_input,
            save_result=consent.save_result,
            consent_type=consent.consent_type,
            is_accepted=consent.is_accepted,
            accepted_at=consent.accepted_at,
        )


class HistoryRepository:
    @staticmethod
    async def list_history(db: AsyncSession, user_id: str) -> HistoryListResponse:
        result = await db.execute(
            select(AnalysisSession)
            .where(AnalysisSession.user_id == user_id)
            .order_by(AnalysisSession.analyzed_at.desc())
        )
        return HistoryListResponse(items=[HistoryRepository._to_schema(item) for item in result.scalars().all()])

    @staticmethod
    async def get_history_item(db: AsyncSession, user_id: str, analysis_id: str) -> HistoryItem | None:
        result = await db.execute(
            select(AnalysisSession).where(
                AnalysisSession.id == analysis_id,
                AnalysisSession.user_id == user_id,
            )
        )
        item = result.scalar_one_or_none()
        return HistoryRepository._to_schema(item) if item else None

    @staticmethod
    async def save_analysis(
        db: AsyncSession,
        user_id: str,
        *,
        chat_text: str,
        result: Any,
        save_input: bool,
        save_result: bool,
    ) -> AnalysisSession | None:
        privacy_consent = await ConsentRepository.get_consent(db, user_id, "privacy_settings")
        if not privacy_consent.history_enabled or not (save_result or save_input):
            return None

        accepted_at = utc_now()
        item = AnalysisSession(
            user_id=user_id,
            overall_emotion=result.overall_emotion,
            confidence=result.confidence,
            emotion_distribution=result.emotion_distribution,
            summary=result.summary,
            context_note=result.context_note,
            suggested_reply=result.suggested_reply,
            warning=result.warning,
            save_input=save_input,
            save_result=True,
            consent_type="analysis_submission",
            is_accepted=True,
            accepted_at=accepted_at,
            chat_text=chat_text if save_input else None,
        )
        db.add(item)
        await db.commit()
        await db.refresh(item)
        return item

    @staticmethod
    async def save_tutor_session(
        db: AsyncSession,
        user_id: str,
        *,
        problem_statement: str,
        student_code: str,
        compiler_error: str | None = None,
        topic: str | None = None,
        result: Any,
        save_input: bool = False,
        save_result: bool = True,
    ) -> AnalysisSession | None:
        if not (save_result or save_input):
            return None

        privacy_consent = await ConsentRepository.get_consent(db, user_id, "privacy_settings")
        if not privacy_consent.history_enabled:
            return None

        accepted_at = utc_now()
        issue_type = getattr(result.diagnosis, "issue_type", "diagnostic_feedback")
        confidence = getattr(result.diagnosis, "confidence", 1.0)
        summary = f"Chẩn đoán OOP: {issue_type} (Mức {result.hint_level})"

        # Privacy Invariant:
        # Khi save_input=False: context_note chỉ lưu chủ đề chung, tuyệt đối không rò rỉ problem_statement.
        # Khi save_input=True: context_note được phép lưu trích đoạn đề bài.
        if save_input:
            context_note = f"Chủ đề: {topic or 'C# OOP'}. Đề bài: {problem_statement[:150]}"
        else:
            context_note = f"Chủ đề: {topic or 'C# OOP'}"

        diagnosis_dict = (
            result.diagnosis.model_dump()
            if hasattr(result.diagnosis, "model_dump")
            else dict(result.diagnosis)
        )
        highest_hint_level_used = getattr(result, "highest_hint_level_used", result.hint_level)
        solution_revealed = getattr(result, "solution_revealed", False)
        success_state = getattr(result, "success_state", "in_progress")

        # save_result may store: diagnosis, skills, hint usage, success state, summary
        distribution_data: dict[str, Any] = {
            "knowledge_components": result.knowledge_components,
            "hint_level": result.hint_level,
            "highest_hint_level_used": highest_hint_level_used,
            "solution_revealed": solution_revealed,
            "teaching_strategy": result.teaching_strategy,
            "prompt_version": getattr(result, "prompt_version", "v1"),
            "diagnosis": diagnosis_dict,
            "success_state": success_state,
        }

        # save_input explicitly permits storage of: problem statement, student code, compiler error
        if save_input:
            distribution_data["student_code"] = student_code
            distribution_data["problem_statement"] = problem_statement
            if compiler_error:
                distribution_data["compiler_error"] = compiler_error

        item = AnalysisSession(
            user_id=user_id,
            overall_emotion=issue_type,
            confidence=confidence,
            emotion_distribution=distribution_data,
            summary=summary,
            context_note=context_note,
            suggested_reply=result.tutor_response,
            warning=result.next_action,
            save_input=save_input,
            save_result=save_result,
            consent_type="tutor_submission",
            is_accepted=True,
            accepted_at=accepted_at,
            chat_text=student_code if save_input else None,
        )
        db.add(item)
        await db.commit()
        await db.refresh(item)
        return item

    @staticmethod
    async def get_tutor_session(
        db: AsyncSession,
        user_id: str,
        session_id: str,
    ) -> AnalysisSession | None:
        """Lấy phiên gia sư của người dùng từ cơ sở dữ liệu."""
        result = await db.execute(
            select(AnalysisSession).where(
                AnalysisSession.id == session_id,
                AnalysisSession.user_id == user_id,
                AnalysisSession.consent_type == "tutor_submission",
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def update_tutor_hint_progression(
        db: AsyncSession,
        user_id: str,
        session_id: str,
        next_level: int,
        hint_payload: Any,
    ) -> AnalysisSession | None:
        """Cập nhật tiến trình gợi ý mới vào phiên học trong DB."""
        item = await HistoryRepository.get_tutor_session(db, user_id, session_id)
        if not item:
            return None

        current_dist = dict(item.emotion_distribution or {})
        prev_highest = current_dist.get("highest_hint_level_used", current_dist.get("hint_level", 1))
        new_highest = max(prev_highest, next_level)

        current_dist["hint_level"] = next_level
        current_dist["highest_hint_level_used"] = new_highest
        current_dist["solution_revealed"] = hint_payload.solution_revealed
        current_dist["teaching_strategy"] = hint_payload.teaching_strategy

        item.emotion_distribution = current_dist
        item.suggested_reply = hint_payload.tutor_response
        item.warning = hint_payload.next_action
        item.summary = f"Chẩn đoán OOP: {item.overall_emotion} (Mức {next_level})"

        await db.commit()
        await db.refresh(item)
        return item

    @staticmethod
    async def delete_history_item(db: AsyncSession, user_id: str, analysis_id: str) -> bool:
        result = await db.execute(
            delete(AnalysisSession).where(
                AnalysisSession.id == analysis_id,
                AnalysisSession.user_id == user_id,
            )
        )
        await db.commit()
        return bool(result.rowcount)

    @staticmethod
    async def clear_history(db: AsyncSession, user_id: str) -> None:
        await db.execute(delete(AnalysisSession).where(AnalysisSession.user_id == user_id))
        await db.commit()

    @staticmethod
    def _to_schema(item: AnalysisSession) -> HistoryItem:
        return HistoryItem(
            id=item.id,
            analyzed_at=item.analyzed_at,
            overall_emotion=item.overall_emotion,
            confidence=item.confidence,
            emotion_distribution=item.emotion_distribution or {},
            summary=item.summary,
            context_note=item.context_note,
            suggested_reply=item.suggested_reply,
            warning=item.warning,
            save_input=item.save_input,
            save_result=item.save_result,
            chat_text=item.chat_text,
        )


class UserDataRepository:
    @staticmethod
    async def delete_all_user_data(db: AsyncSession, user_id: str) -> None:
        """
        Xóa toàn bộ dữ liệu thuộc sở hữu của người dùng hiện tại:
        - student profile
        - sessions (learning_sessions, analysis_sessions)
        - attempts (student_attempts)
        - messages (tutor_messages)
        - mastery (student_skill_mastery)
        - audit records (student_mastery_audits)
        - general consent settings
        - stored inputs (mã nguồn và dữ liệu đầu vào đã lưu)
        
        Quy tắc bất biến: Bảo lưu Vision-specific consent (Preserve Vision-specific consent).
        """
        user_session_subquery = select(LearningSession.id).where(LearningSession.user_id == user_id)

        # 1. Xóa các tin nhắn gia sư thuộc các phiên học của user
        await db.execute(delete(TutorMessage).where(TutorMessage.session_id.in_(user_session_subquery)))

        # 2. Xóa các bản ghi audit mastery của user
        await db.execute(delete(StudentMasteryAudit).where(StudentMasteryAudit.user_id == user_id))

        # 3. Xóa các lần thử làm bài (student attempts) thuộc các phiên học của user
        await db.execute(delete(StudentAttempt).where(StudentAttempt.session_id.in_(user_session_subquery)))

        # 4. Xóa các phiên học đa lượt của user
        await db.execute(delete(LearningSession).where(LearningSession.user_id == user_id))

        # 5. Xóa các phiên phân tích đơn lẻ (analysis sessions) của user
        await db.execute(delete(AnalysisSession).where(AnalysisSession.user_id == user_id))

        # 6. Xóa độ thành thạo kỹ năng (student mastery) của user
        await db.execute(delete(StudentSkillMastery).where(StudentSkillMastery.user_id == user_id))

        # 7. Xóa hồ sơ học viên (student profile) của user
        await db.execute(delete(StudentProfile).where(StudentProfile.user_id == user_id))

        # 8. Xóa consent cấu hình chung, NHƯNG BẢO LƯU Vision-specific consent
        await db.execute(
            delete(Consent).where(
                Consent.user_id == user_id,
                ~Consent.consent_type.in_(["vision", "vision_ocr", "vision_consent"]),
            )
        )

        # 9. Xóa các model hồ sơ phụ trợ/legacy nếu còn tồn tại
        await db.execute(delete(ProfileModel).where(ProfileModel.user_id == user_id))
        await db.execute(delete(PartnerProfileModel).where(PartnerProfileModel.user_id == user_id))
        await db.execute(delete(Preference).where(Preference.user_id == user_id))

        await db.commit()


class UserRepository:
    @staticmethod
    async def get_by_email(db: AsyncSession, email: str) -> User | None:
        result = await db.execute(select(User).where(User.email == email.lower()))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_firebase_uid(db: AsyncSession, firebase_uid: str) -> User | None:
        result = await db.execute(select(User).where(User.firebase_uid == firebase_uid))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_id(db: AsyncSession, user_id: str) -> User | None:
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def create_user(db: AsyncSession, *, email: str, hashed_password: str) -> User:
        user = User(email=email.lower(), hashed_password=hashed_password)
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    async def get_or_create_firebase_user(db: AsyncSession, *, firebase_uid: str, email: str) -> User:
        existing_by_uid = await UserRepository.get_by_firebase_uid(db, firebase_uid)
        if existing_by_uid:
            return existing_by_uid

        normalized_email = email.lower()
        existing_by_email = await UserRepository.get_by_email(db, normalized_email)
        if existing_by_email:
            existing_by_email.firebase_uid = firebase_uid
            await db.commit()
            await db.refresh(existing_by_email)
            return existing_by_email

        user = User(
            email=normalized_email,
            firebase_uid=firebase_uid,
            hashed_password="firebase-auth-managed-user",
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user
