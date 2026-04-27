from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_analyze_emotion():
    response = client.post(
        "/api/analyze",
        json={
            "chat_text": "Em sao vậy?\nKhông sao.\nAnh thấy em hơi lạ.\nEm mệt thôi.",
            "profile_context": "Người yêu thường im lặng khi mệt, không thích bị hỏi dồn.",
            "save_input": False,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["overall_emotion"] == "mệt mỏi / né tránh nhẹ"
    assert data["confidence"] == 0.72
    assert data["authenticated"] is False
    assert data["saved_to_history"] is False
    assert "emotion_distribution" in data
    assert data["warning"] == "Kết quả chỉ mang tính tham khảo, không thể thay thế giao tiếp trực tiếp."


def test_analyze_empty_message():
    response = client.post("/api/analyze", json={"chat_text": ""})
    assert response.status_code in [400, 422]


def test_analyze_ignores_invalid_optional_auth_token():
    response = client.post(
        "/api/analyze",
        headers={"Authorization": "Bearer invalid-token"},
        json={
            "chat_text": "Em mệt thôi.",
            "profile_context": "",
            "save_input": False,
            "save_result": False,
        },
    )

    assert response.status_code == 200
    assert response.json()["overall_emotion"] == "mệt mỏi / né tránh nhẹ"


def test_health_root():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
