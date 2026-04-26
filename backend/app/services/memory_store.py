from copy import deepcopy
from datetime import datetime, timezone
from uuid import uuid4

from app.schemas.analyze_schema import AnalyzeResponse
from app.schemas.consent_schema import ConsentSettings, ConsentUpdate
from app.schemas.history_schema import HistoryItem, HistoryListResponse
from app.schemas.profile_schema import PartnerProfile, ProfileResponse, ProfileUpsert, UserProfile


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class MemoryStore:
    """Kho dữ liệu tạm cho bản sau MVP, thay bằng database khi triển khai production."""

    profile: ProfileResponse = ProfileResponse(
        user_profile=UserProfile(),
        partner_profile=PartnerProfile(),
        updated_at=utc_now(),
    )
    consent: ConsentSettings = ConsentSettings()
    history_items: list[HistoryItem] = []

    @classmethod
    def reset_all(cls) -> None:
        cls.profile = ProfileResponse(
            user_profile=UserProfile(),
            partner_profile=PartnerProfile(),
            updated_at=utc_now(),
        )
        cls.consent = ConsentSettings()
        cls.history_items = []


class ProfileService:
    @staticmethod
    def get_profile() -> ProfileResponse:
        return deepcopy(MemoryStore.profile)

    @staticmethod
    def save_profile(profile: ProfileUpsert) -> ProfileResponse:
        MemoryStore.profile = ProfileResponse(
            user_profile=profile.user_profile,
            partner_profile=profile.partner_profile,
            updated_at=utc_now(),
        )
        return deepcopy(MemoryStore.profile)

    @staticmethod
    def delete_profile() -> None:
        MemoryStore.profile = ProfileResponse(
            user_profile=UserProfile(),
            partner_profile=PartnerProfile(),
            updated_at=utc_now(),
        )


class ConsentService:
    @staticmethod
    def get_consent() -> ConsentSettings:
        return deepcopy(MemoryStore.consent)

    @staticmethod
    def save_consent(consent: ConsentUpdate) -> ConsentSettings:
        accepted_at = utc_now() if consent.is_accepted else None
        MemoryStore.consent = ConsentSettings(
            history_enabled=consent.history_enabled,
            save_input=consent.save_input,
            save_result=consent.save_result,
            consent_type=consent.consent_type,
            is_accepted=consent.is_accepted,
            accepted_at=accepted_at,
        )
        return deepcopy(MemoryStore.consent)

    @staticmethod
    def accept_analysis_consent(save_input: bool, save_result: bool) -> ConsentSettings:
        if not save_input and not save_result:
            return deepcopy(MemoryStore.consent)

        MemoryStore.consent = ConsentSettings(
            history_enabled=MemoryStore.consent.history_enabled,
            save_input=save_input,
            save_result=save_result,
            consent_type="analysis_submission",
            is_accepted=True,
            accepted_at=utc_now(),
        )
        return deepcopy(MemoryStore.consent)

    @staticmethod
    def reset_consent() -> None:
        MemoryStore.consent = ConsentSettings()


class HistoryService:
    @staticmethod
    def list_history() -> HistoryListResponse:
        return HistoryListResponse(items=[deepcopy(item) for item in MemoryStore.history_items])

    @staticmethod
    def get_history_item(analysis_id: str) -> HistoryItem | None:
        for item in MemoryStore.history_items:
            if item.id == analysis_id:
                return deepcopy(item)
        return None

    @staticmethod
    def save_analysis(
        *,
        chat_text: str,
        result: AnalyzeResponse,
        save_input: bool,
        save_result: bool,
    ) -> HistoryItem | None:
        consent = MemoryStore.consent
        should_save_result = consent.history_enabled and (save_result or save_input)

        if not should_save_result:
            return None

        # Chỉ lưu chat gốc khi người dùng đồng ý rõ ràng với save_input.
        item = HistoryItem(
            id=str(uuid4()),
            analyzed_at=utc_now(),
            overall_emotion=result.overall_emotion,
            confidence=result.confidence,
            emotion_distribution=result.emotion_distribution,
            summary=result.summary,
            context_note=result.context_note,
            suggested_reply=result.suggested_reply,
            warning=result.warning,
            save_input=save_input,
            save_result=True,
            chat_text=chat_text if save_input else None,
        )
        MemoryStore.history_items.insert(0, item)
        return deepcopy(item)

    @staticmethod
    def delete_history_item(analysis_id: str) -> bool:
        before_count = len(MemoryStore.history_items)
        MemoryStore.history_items = [item for item in MemoryStore.history_items if item.id != analysis_id]
        return len(MemoryStore.history_items) != before_count

    @staticmethod
    def clear_history() -> None:
        MemoryStore.history_items = []


class UserDataService:
    @staticmethod
    def delete_all_user_data() -> None:
        MemoryStore.reset_all()
