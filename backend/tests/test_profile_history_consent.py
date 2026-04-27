from uuid import uuid4


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


def test_analyze_does_not_save_history_by_default(client, auth_headers):
    response = client.post(
        "/api/analyze",
        headers=auth_headers,
        json={
            "chat_text": "Em mệt thôi.",
            "profile_context": "",
            "save_input": False,
            "save_result": False,
        },
    )
    assert response.status_code == 200

    history_response = client.get("/api/history", headers=auth_headers)
    assert history_response.status_code == 200
    assert history_response.json()["items"] == []


def test_analyze_saves_result_without_original_chat_when_allowed(client, auth_headers):
    response = client.post(
        "/api/analyze",
        headers=auth_headers,
        json={
            "chat_text": "Em mệt thôi.",
            "profile_context": "",
            "save_input": False,
            "save_result": True,
        },
    )
    assert response.status_code == 200

    history_response = client.get("/api/history", headers=auth_headers)
    items = history_response.json()["items"]
    assert len(items) == 1
    assert items[0]["save_result"] is True
    assert items[0]["save_input"] is False
    assert items[0]["chat_text"] is None


def test_clear_history_removes_history_but_keeps_profile(client, auth_headers):
    client.post("/api/profile", headers=auth_headers, json=sample_profile_payload())

    for chat_text in ["Em mệt thôi.", "Hôm nay em cần yên tĩnh."]:
        response = client.post(
            "/api/analyze",
            headers=auth_headers,
            json={
                "chat_text": chat_text,
                "profile_context": "",
                "save_input": False,
                "save_result": True,
            },
        )
        assert response.status_code == 200

    history_response = client.get("/api/history", headers=auth_headers)
    assert len(history_response.json()["items"]) == 2

    clear_response = client.delete("/api/history", headers=auth_headers)
    assert clear_response.status_code == 200
    assert client.get("/api/history", headers=auth_headers).json()["items"] == []
    assert client.get("/api/profile", headers=auth_headers).json()["user_profile"]["nickname"] == "An"


def test_analyze_saves_original_chat_only_with_explicit_consent(client, auth_headers):
    response = client.post(
        "/api/analyze",
        headers=auth_headers,
        json={
            "chat_text": "Em mệt thôi.",
            "profile_context": "",
            "save_input": True,
            "save_result": True,
        },
    )
    assert response.status_code == 200

    history_response = client.get("/api/history", headers=auth_headers)
    item = history_response.json()["items"][0]
    assert item["chat_text"] == "Em mệt thôi."
    assert item["save_input"] is True


def test_analyze_public_request_does_not_save_even_when_save_requested(client):
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


def test_each_user_only_sees_own_history(client):
    user_a_headers = register_and_login(client)
    user_b_headers = register_and_login(client)

    client.post(
        "/api/analyze",
        headers=user_a_headers,
        json={
            "chat_text": "User A chat",
            "profile_context": "",
            "save_input": True,
            "save_result": True,
        },
    )

    user_a_history = client.get("/api/history", headers=user_a_headers).json()["items"]
    user_b_history = client.get("/api/history", headers=user_b_headers).json()["items"]

    assert len(user_a_history) == 1
    assert user_a_history[0]["chat_text"] == "User A chat"
    assert user_b_history == []


def test_delete_history_item_and_all_user_data(client, auth_headers):
    client.post("/api/profile", headers=auth_headers, json=sample_profile_payload())

    client.post(
        "/api/analyze",
        headers=auth_headers,
        json={
            "chat_text": "Em mệt thôi.",
            "profile_context": "",
            "save_input": False,
            "save_result": True,
        },
    )
    item_id = client.get("/api/history", headers=auth_headers).json()["items"][0]["id"]

    delete_response = client.delete(f"/api/history/{item_id}", headers=auth_headers)
    assert delete_response.status_code == 200
    assert client.get("/api/history", headers=auth_headers).json()["items"] == []

    client.post(
        "/api/analyze",
        headers=auth_headers,
        json={
            "chat_text": "Em mệt thôi.",
            "profile_context": "",
            "save_input": False,
            "save_result": True,
        },
    )
    assert len(client.get("/api/history", headers=auth_headers).json()["items"]) == 1

    clear_response = client.delete("/api/user-data", headers=auth_headers)
    assert clear_response.status_code == 200
    assert client.get("/api/history", headers=auth_headers).json()["items"] == []
    assert client.get("/api/consent", headers=auth_headers).json()["is_accepted"] is False
    assert client.get("/api/profile", headers=auth_headers).json()["user_profile"]["nickname"] == ""
