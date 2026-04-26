def test_save_profile(client, auth_headers):
    response = client.post(
        "/api/profile",
        headers=auth_headers,
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


def test_get_profile_requires_auth(client):
    response = client.get("/api/profile")
    assert response.status_code == 401


def test_get_profile_returns_user_owned_default(client, auth_headers):
    response = client.get("/api/profile", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["user_profile"]["nickname"] == ""
    assert data["partner_profile"]["nickname"] == ""
