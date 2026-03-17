import pytest


@pytest.mark.asyncio
async def test_register_player(client):
    response = await client.post("/api/v1/auth/register", json={"username": "player1"})
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "player1"
    assert data["api_key"].startswith("cm_")
    assert data["balance"] == 1000.0


@pytest.mark.asyncio
async def test_register_duplicate_username(client):
    await client.post("/api/v1/auth/register", json={"username": "player1"})
    response = await client.post("/api/v1/auth/register", json={"username": "player1"})
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_api_key_auth(client):
    reg = await client.post("/api/v1/auth/register", json={"username": "player1"})
    api_key = reg.json()["api_key"]
    response = await client.get("/api/v1/auth/me", headers={"X-API-Key": api_key})
    assert response.status_code == 200
    assert response.json()["username"] == "player1"


@pytest.mark.asyncio
async def test_invalid_api_key(client):
    response = await client.get("/api/v1/auth/me", headers={"X-API-Key": "invalid"})
    assert response.status_code == 401
