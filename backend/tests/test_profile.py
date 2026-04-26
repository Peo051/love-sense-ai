import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_profile():
    response = client.post(
        "/api/profile",
        json={
            "name": "Test User",
            "age": 25,
            "communication_style": "direct"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test User"

def test_get_profile():
    response = client.get("/api/profile/1")
    assert response.status_code == 200
