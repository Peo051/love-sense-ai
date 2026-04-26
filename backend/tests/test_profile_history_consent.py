import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.memory_store import MemoryStore

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_memory_store():
    MemoryStore.reset_all()
    yield
    MemoryStore.reset_all()


def test_consent_defaults_and_update():
    response = client.get("/api/consent")
    assert response.status_code == 200
    assert response.json()["history_enabled"] is True
    assert response.json()["is_accepted"] is False

    response = client.post(
        "/api/consent",
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


def test_profile_save_and_delete():
    response = client.post(
        "/api/profile",
        json={
            "user_profile": {
                "nickname": "An",
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
        },
    )

    assert response.status_code == 200
    assert response.json()["user_profile"]["nickname"] == "An"
    assert response.json()["partner_profile"]["dislikes_repeated_questions"] is True

    delete_response = client.delete("/api/profile")
    assert delete_response.status_code == 200

    get_response = client.get("/api/profile")
    assert get_response.status_code == 200
    assert get_response.json()["user_profile"]["nickname"] == ""


def test_analyze_does_not_save_history_by_default():
    response = client.post(
        "/api/analyze",
        json={
            "chat_text": "Em mệt thôi.",
            "profile_context": "",
            "save_input": False,
            "save_result": False,
        },
    )
    assert response.status_code == 200

    history_response = client.get("/api/history")
    assert history_response.status_code == 200
    assert history_response.json()["items"] == []


def test_analyze_saves_result_without_original_chat_when_allowed():
    response = client.post(
        "/api/analyze",
        json={
            "chat_text": "Em mệt thôi.",
            "profile_context": "",
            "save_input": False,
            "save_result": True,
        },
    )
    assert response.status_code == 200

    history_response = client.get("/api/history")
    items = history_response.json()["items"]
    assert len(items) == 1
    assert items[0]["save_result"] is True
    assert items[0]["save_input"] is False
    assert items[0]["chat_text"] is None


def test_analyze_saves_original_chat_only_with_explicit_consent():
    response = client.post(
        "/api/analyze",
        json={
            "chat_text": "Em mệt thôi.",
            "profile_context": "",
            "save_input": True,
            "save_result": True,
        },
    )
    assert response.status_code == 200

    history_response = client.get("/api/history")
    item = history_response.json()["items"][0]
    assert item["chat_text"] == "Em mệt thôi."
    assert item["save_input"] is True


def test_delete_history_item_and_all_user_data():
    client.post(
        "/api/analyze",
        json={
            "chat_text": "Em mệt thôi.",
            "profile_context": "",
            "save_input": False,
            "save_result": True,
        },
    )
    item_id = client.get("/api/history").json()["items"][0]["id"]

    delete_response = client.delete(f"/api/history/{item_id}")
    assert delete_response.status_code == 200
    assert client.get("/api/history").json()["items"] == []

    client.post(
        "/api/analyze",
        json={
            "chat_text": "Em mệt thôi.",
            "profile_context": "",
            "save_input": False,
            "save_result": True,
        },
    )
    assert len(client.get("/api/history").json()["items"]) == 1

    clear_response = client.delete("/api/user-data")
    assert clear_response.status_code == 200
    assert client.get("/api/history").json()["items"] == []
    assert client.get("/api/consent").json()["is_accepted"] is False
