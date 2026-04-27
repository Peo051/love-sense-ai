from uuid import uuid4

from app.core.config import settings


def register_and_login(client, email: str | None = None):
    email = email or f"rate-{uuid4()}@example.com"
    password = "secret123"
    assert client.post("/api/register", json={"email": email, "password": password}).status_code == 201
    token_response = client.post(
        "/api/token",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert token_response.status_code == 200
    return {"Authorization": f"Bearer {token_response.json()['access_token']}"}


def analyze_payload(text: str = "Em mệt thôi."):
    return {
        "chat_text": text,
        "profile_context": "",
        "save_input": False,
        "save_result": False,
    }


def test_analyze_rate_limit_for_anonymous_client(client, monkeypatch):
    monkeypatch.setattr(settings, "analyze_rate_limit_requests", 1)
    monkeypatch.setattr(settings, "analyze_rate_limit_window_seconds", 60)

    assert client.post("/api/analyze", json=analyze_payload()).status_code == 200
    response = client.post("/api/analyze", json=analyze_payload("Em hơi mệt."))

    assert response.status_code == 429
    assert response.json()["detail"] == "Bạn đang phân tích quá nhanh. Vui lòng chờ một chút rồi thử lại."
    assert int(response.headers["Retry-After"]) > 0


def test_analyze_rate_limit_is_scoped_by_authenticated_user(client, monkeypatch):
    monkeypatch.setattr(settings, "analyze_rate_limit_requests", 1)
    monkeypatch.setattr(settings, "analyze_rate_limit_window_seconds", 60)
    user_a_headers = register_and_login(client)
    user_b_headers = register_and_login(client)

    assert client.post("/api/analyze", headers=user_a_headers, json=analyze_payload()).status_code == 200
    assert client.post("/api/analyze", headers=user_a_headers, json=analyze_payload("Tin nhắn thứ hai.")).status_code == 429
    assert client.post("/api/analyze", headers=user_b_headers, json=analyze_payload()).status_code == 200
