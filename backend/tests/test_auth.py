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
