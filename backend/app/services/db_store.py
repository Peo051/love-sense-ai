from datetime import datetime, timezone

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.analysis_session import AnalysisSession
from app.models.consent import Consent
from app.models.partner_profile import PartnerProfile as PartnerProfileModel
from app.models.preference import Preference
from app.models.profile import Profile as ProfileModel
from app.models.user import User
from app.schemas.analyze_schema import AnalyzeResponse
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
        result: AnalyzeResponse,
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
        await db.execute(delete(AnalysisSession).where(AnalysisSession.user_id == user_id))
        await db.execute(delete(Consent).where(Consent.user_id == user_id))
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
