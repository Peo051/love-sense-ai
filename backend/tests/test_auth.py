def test_register_login_and_get_me(client):
    register_response = client.post(
        "/api/register",
        json={"email": "person@example.com", "password": "secret123"},
    )
    assert register_response.status_code == 201
    assert register_response.json()["email"] == "person@example.com"

    token_response = client.post(
        "/api/token",
        data={"username": "person@example.com", "password": "secret123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert token_response.status_code == 200

    token = token_response.json()["access_token"]
    me_response = client.get("/api/me", headers={"Authorization": f"Bearer {token}"})
    assert me_response.status_code == 200
    assert me_response.json()["email"] == "person@example.com"
    assert me_response.json()["uid"]


def test_get_me_requires_token(client):
    response = client.get("/api/me")
    assert response.status_code == 401


def test_firebase_admin_requires_service_account_in_production(monkeypatch):
    from app.core.config import settings
    from app.core.firebase import initialize_firebase_admin

    monkeypatch.setattr("app.core.firebase.is_firebase_admin_initialized", lambda: False)
    monkeypatch.setattr(settings, "app_env", "production")
    monkeypatch.setattr(settings, "firebase_service_account_json", "")

    try:
        initialize_firebase_admin()
    except RuntimeError as exc:
        assert "Missing FIREBASE_SERVICE_ACCOUNT_JSON" in str(exc)
    else:
        raise AssertionError("Expected Firebase Admin configuration error")


def test_get_me_accepts_firebase_token_and_maps_internal_user(client, monkeypatch):
    monkeypatch.setattr("app.deps.auth.is_firebase_admin_initialized", lambda: True)
    monkeypatch.setattr("app.deps.auth.initialize_firebase_admin", lambda: True)
    monkeypatch.setattr(
        "app.deps.auth.firebase_auth.verify_id_token",
        lambda token: {
            "uid": "firebase-user-1",
            "email": "google-user@example.com",
            "name": "Google User",
            "picture": "https://example.com/avatar.png",
        },
    )

    response = client.get("/api/me", headers={"Authorization": "Bearer firebase-token"})

    assert response.status_code == 200
    data = response.json()
    assert data["uid"] == "firebase-user-1"
    assert data["email"] == "google-user@example.com"
    assert data["name"] == "Google User"
    assert data["picture"] == "https://example.com/avatar.png"


def test_firebase_user_data_is_scoped_by_uid(client, monkeypatch):
    monkeypatch.setattr("app.deps.auth.is_firebase_admin_initialized", lambda: True)
    monkeypatch.setattr("app.deps.auth.initialize_firebase_admin", lambda: True)

    def verify_id_token(token):
        uid = "firebase-a" if token == "firebase-token-a" else "firebase-b"
        return {"uid": uid, "email": f"{uid}@example.com"}

    monkeypatch.setattr("app.deps.auth.firebase_auth.verify_id_token", verify_id_token)

    headers_a = {"Authorization": "Bearer firebase-token-a"}
    headers_b = {"Authorization": "Bearer firebase-token-b"}

    save_response = client.post(
        "/api/profile",
        headers=headers_a,
        json={
            "user_profile": {
                "nickname": "Firebase A",
                "primary_language": "Tiếng Việt",
                "communication_style": "",
                "relationship_status": "",
            },
            "partner_profile": {
                "nickname": "",
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
    assert save_response.status_code == 200

    assert client.get("/api/profile", headers=headers_a).json()["user_profile"]["nickname"] == "Firebase A"
    assert client.get("/api/profile", headers=headers_b).json()["user_profile"]["nickname"] == ""


def test_register_rejects_duplicate_email(client):
    payload = {"email": "duplicate@example.com", "password": "secret123"}
    assert client.post("/api/register", json=payload).status_code == 201

    response = client.post("/api/register", json=payload)
    assert response.status_code == 400


def test_login_rejects_wrong_password(client):
    client.post("/api/register", json={"email": "person@example.com", "password": "secret123"})
    response = client.post(
        "/api/token",
        data={"username": "person@example.com", "password": "wrongpass"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 401
