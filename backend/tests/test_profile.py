from fastapi.testclient import TestClient

from app.main import app
from app.services.memory_store import MemoryStore

client = TestClient(app)


def setup_function():
    MemoryStore.reset_all()


def teardown_function():
    MemoryStore.reset_all()


def test_save_profile():
    response = client.post(
        "/api/profile",
        json={
            "user_profile": {
                "nickname": "Test User",
                "primary_language": "Tiếng Việt",
                "communication_style": "direct",
                "relationship_status": "dating",
            },
            "partner_profile": {
                "nickname": "Partner",
                "likes": "coffee",
                "dislikes": "spam messages",
                "texting_style": "short replies",
                "when_happy": "uses more emojis",
                "when_sad": "gets quiet",
                "when_angry": "needs space",
                "likes_checkins": True,
                "dislikes_repeated_questions": True,
            },
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["user_profile"]["nickname"] == "Test User"
    assert data["partner_profile"]["nickname"] == "Partner"


def test_get_profile():
    response = client.get("/api/profile")
    assert response.status_code == 200
    data = response.json()
    assert data["user_profile"]["nickname"] == ""
    assert data["partner_profile"]["nickname"] == ""
