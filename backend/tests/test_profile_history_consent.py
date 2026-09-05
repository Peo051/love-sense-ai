import asyncio
from uuid import uuid4

from app.models.analysis_session import AnalysisSession
from tests.conftest import TestingSessionLocal


def seed_history_session(
    user_id: str,
    *,
    chat_text: str | None = None,
    save_input: bool = False,
    save_result: bool = True,
    summary: str = "Tóm tắt bài tập",
    overall_emotion: str = "Đạt yêu cầu",
) -> str:
    async def _insert():
        async with TestingSessionLocal() as session:
            item = AnalysisSession(
                user_id=user_id,
                overall_emotion=overall_emotion,
                confidence=0.85,
                emotion_distribution={"pass": 1.0},
                summary=summary,
                context_note="",
                suggested_reply="Tiếp tục phát huy",
                warning="Cảnh báo tham khảo",
                save_input=save_input,
                save_result=save_result,
                consent_type="analysis_submission",
                is_accepted=True,
                chat_text=chat_text if save_input else None,
            )
            session.add(item)
            await session.commit()
            await session.refresh(item)
            return item.id

    return asyncio.run(_insert())


def register_and_login(client, email: str | None = None):
    email = email or f"user-{uuid4()}@example.com"
    password = "secret123"
    client.post("/api/register", json={"email": email, "password": password})
    token_response = client.post(
        "/api/token",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    token = token_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def sample_profile_payload(nickname: str = "An"):
    return {
        "user_profile": {
            "nickname": nickname,
            "primary_language": "Tiếng Việt",
            "communication_style": "Nhẹ nhàng",
            "relationship_status": "Đang tìm hiểu",
        },
        "partner_profile": {
            "nickname": "Bình",
            "likes": "Nhạc acoustic",
            "dislikes": "Bị hỏi dồn",
            "texting_style": "Trả lời chậm khi bận",
            "when_happy": "Nhắn nhiều hơn",
            "when_sad": "Ít nói",
            "when_angry": "Cần không gian riêng",
            "likes_checkins": True,
            "dislikes_repeated_questions": True,
            "height_cm": 165,
            "weight_kg": 55,
            "appearance": "",
            "private_notes": "Không dùng chiều cao/cân nặng để suy luận cảm xúc.",
        },
    }


def test_consent_defaults_and_update(client, auth_headers):
    response = client.get("/api/consent", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["history_enabled"] is True
    assert response.json()["is_accepted"] is False

    response = client.post(
        "/api/consent",
        headers=auth_headers,
        json={
            "history_enabled": False,
            "save_input": False,
            "save_result": False,
            "consent_type": "privacy_settings",
            "is_accepted": False,
        },
    )

    assert response.status_code == 200
    assert response.json()["history_enabled"] is False
    assert response.json()["accepted_at"] is None


def test_profile_save_and_delete(client, auth_headers):
    response = client.post(
        "/api/profile",
        headers=auth_headers,
        json=sample_profile_payload(),
    )

    assert response.status_code == 200
    assert response.json()["user_profile"]["nickname"] == "An"
    assert response.json()["partner_profile"]["dislikes_repeated_questions"] is True

    delete_response = client.delete("/api/profile", headers=auth_headers)
    assert delete_response.status_code == 200

    get_response = client.get("/api/profile", headers=auth_headers)
    assert get_response.status_code == 200
    assert get_response.json()["user_profile"]["nickname"] == ""


def test_each_user_only_sees_own_profile_and_consent(client):
    user_a_headers = register_and_login(client)
    user_b_headers = register_and_login(client)

    client.post(
        "/api/profile",
        headers=user_a_headers,
        json={
            "user_profile": {
                "nickname": "User A",
                "primary_language": "vi",
                "communication_style": "calm",
                "relationship_status": "dating",
            },
            "partner_profile": {
                "nickname": "Partner A",
                "likes": "",
                "dislikes": "",
                "texting_style": "",
                "when_happy": "",
                "when_sad": "",
                "when_angry": "",
                "likes_checkins": True,
                "dislikes_repeated_questions": True,
                "height_cm": None,
                "weight_kg": None,
                "appearance": "",
                "private_notes": "",
            },
        },
    )
    client.post(
        "/api/consent",
        headers=user_a_headers,
        json={
            "history_enabled": False,
            "save_input": False,
            "save_result": False,
            "consent_type": "privacy_settings",
            "is_accepted": False,
        },
    )

    user_a_profile = client.get("/api/profile", headers=user_a_headers).json()
    user_b_profile = client.get("/api/profile", headers=user_b_headers).json()
    user_a_consent = client.get("/api/consent", headers=user_a_headers).json()
    user_b_consent = client.get("/api/consent", headers=user_b_headers).json()

    assert user_a_profile["user_profile"]["nickname"] == "User A"
    assert user_b_profile["user_profile"]["nickname"] == ""
    assert user_a_consent["history_enabled"] is False
    assert user_b_consent["history_enabled"] is True


def test_profile_delete_is_scoped_to_current_user(client):
    user_a_headers = register_and_login(client)
    user_b_headers = register_and_login(client)

    client.post("/api/profile", headers=user_a_headers, json=sample_profile_payload("User A"))
    client.post("/api/profile", headers=user_b_headers, json=sample_profile_payload("User B"))

    delete_response = client.delete("/api/profile", headers=user_a_headers)
    assert delete_response.status_code == 200

    user_a_profile = client.get("/api/profile", headers=user_a_headers).json()
    user_b_profile = client.get("/api/profile", headers=user_b_headers).json()

    assert user_a_profile["user_profile"]["nickname"] == ""
    assert user_b_profile["user_profile"]["nickname"] == "User B"


def test_clear_history_removes_history_but_keeps_profile(client, auth_headers):
    client.post("/api/profile", headers=auth_headers, json=sample_profile_payload())
    user_id = client.get("/api/me", headers=auth_headers).json()["id"]

    seed_history_session(user_id, summary="Bài 1")
    seed_history_session(user_id, summary="Bài 2")

    history_response = client.get("/api/history", headers=auth_headers)
    assert len(history_response.json()["items"]) == 2

    clear_response = client.delete("/api/history", headers=auth_headers)
    assert clear_response.status_code == 200
    assert client.get("/api/history", headers=auth_headers).json()["items"] == []
    assert client.get("/api/profile", headers=auth_headers).json()["user_profile"]["nickname"] == "An"


def test_each_user_only_sees_own_history(client):
    user_a_headers = register_and_login(client)
    user_b_headers = register_and_login(client)
    user_a_id = client.get("/api/me", headers=user_a_headers).json()["id"]

    seed_history_session(user_a_id, chat_text="User A code", save_input=True)

    user_a_history = client.get("/api/history", headers=user_a_headers).json()["items"]
    user_b_history = client.get("/api/history", headers=user_b_headers).json()["items"]

    assert len(user_a_history) == 1
    assert user_a_history[0]["chat_text"] == "User A code"
    assert user_b_history == []


def test_history_detail_delete_and_clear_are_scoped_to_current_user(client):
    user_a_headers = register_and_login(client)
    user_b_headers = register_and_login(client)
    user_a_id = client.get("/api/me", headers=user_a_headers).json()["id"]
    user_b_id = client.get("/api/me", headers=user_b_headers).json()["id"]

    item_a_id = seed_history_session(user_a_id, chat_text="User A code", save_input=True)
    seed_history_session(user_b_id, chat_text="User B code", save_input=True)

    assert client.get(f"/api/history/{item_a_id}", headers=user_b_headers).status_code == 404
    assert client.delete(f"/api/history/{item_a_id}", headers=user_b_headers).status_code == 404
    assert client.get(f"/api/history/{item_a_id}", headers=user_a_headers).status_code == 200

    clear_b_response = client.delete("/api/history", headers=user_b_headers)
    assert clear_b_response.status_code == 200
    assert client.get("/api/history", headers=user_b_headers).json()["items"] == []

    user_a_history = client.get("/api/history", headers=user_a_headers).json()["items"]
    assert len(user_a_history) == 1
    assert user_a_history[0]["chat_text"] == "User A code"


def test_delete_user_data_is_scoped_to_current_user(client):
    user_a_headers = register_and_login(client)
    user_b_headers = register_and_login(client)
    user_a_id = client.get("/api/me", headers=user_a_headers).json()["id"]
    user_b_id = client.get("/api/me", headers=user_b_headers).json()["id"]

    client.post("/api/profile", headers=user_a_headers, json=sample_profile_payload("User A"))
    client.post("/api/profile", headers=user_b_headers, json=sample_profile_payload("User B"))
    client.post(
        "/api/consent",
        headers=user_b_headers,
        json={
            "history_enabled": True,
            "save_input": False,
            "save_result": True,
            "consent_type": "privacy_settings",
            "is_accepted": True,
        },
    )

    seed_history_session(user_a_id, summary="User A session")
    seed_history_session(user_b_id, summary="User B session")

    delete_response = client.delete("/api/user-data", headers=user_a_headers)
    assert delete_response.status_code == 200

    assert client.get("/api/profile", headers=user_a_headers).json()["user_profile"]["nickname"] == ""
    assert client.get("/api/history", headers=user_a_headers).json()["items"] == []
    assert client.get("/api/consent", headers=user_a_headers).json()["is_accepted"] is False

    assert client.get("/api/profile", headers=user_b_headers).json()["user_profile"]["nickname"] == "User B"
    user_b_history = client.get("/api/history", headers=user_b_headers).json()["items"]
    assert len(user_b_history) == 1
    assert client.get("/api/consent", headers=user_b_headers).json()["is_accepted"] is True


def test_delete_history_item_and_all_user_data(client, auth_headers):
    client.post("/api/profile", headers=auth_headers, json=sample_profile_payload())
    user_id = client.get("/api/me", headers=auth_headers).json()["id"]

    item_id = seed_history_session(user_id, summary="Session 1")

    delete_response = client.delete(f"/api/history/{item_id}", headers=auth_headers)
    assert delete_response.status_code == 200
    assert client.get("/api/history", headers=auth_headers).json()["items"] == []

    seed_history_session(user_id, summary="Session 2")
    assert len(client.get("/api/history", headers=auth_headers).json()["items"]) == 1

    clear_response = client.delete("/api/user-data", headers=auth_headers)
    assert clear_response.status_code == 200
    assert client.get("/api/history", headers=auth_headers).json()["items"] == []
    assert client.get("/api/consent", headers=auth_headers).json()["is_accepted"] is False
    assert client.get("/api/profile", headers=auth_headers).json()["user_profile"]["nickname"] == ""

