from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_analyze_post_returns_deprecated_410():
    response = client.post(
        "/api/analyze",
        json={
            "chat_text": "Em mệt thôi.",
        },
    )

    assert response.status_code == 410
    assert "deprecated" in response.json()["detail"].lower()


def test_analyze_get_returns_deprecated_410():
    response = client.get("/api/analyze")

    assert response.status_code == 410
    assert "deprecated" in response.json()["detail"].lower()


def test_health_root():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_api_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "CodeSense AI API"

