import pytest


@pytest.mark.asyncio
async def test_list_skills(client):
    response = await client.get("/api/v1/skills")
    assert response.status_code == 200
    skills = response.json()
    assert len(skills) >= 12
    sketch = next(s for s in skills if s["id"] == "sketch")
    assert sketch["tier"] == 1
    assert sketch["cost"] == 0


@pytest.mark.asyncio
async def test_buy_skill_success(client):
    reg = await client.post("/api/v1/auth/register", json={"username": "skill_p1"})
    api_key = reg.json()["api_key"]
    headers = {"X-API-Key": api_key}
    agent_resp = await client.post(
        "/api/v1/agents", json={"name": "test"}, headers=headers
    )
    agent_id = agent_resp.json()["id"]

    response = await client.post(
        f"/api/v1/agents/{agent_id}/skills",
        json={"skill_id": "oil_painting"},
        headers=headers,
    )
    assert response.status_code == 200
    assert "oil_painting" in response.json()["skills"]


@pytest.mark.asyncio
async def test_buy_skill_deducts_balance(client):
    reg = await client.post("/api/v1/auth/register", json={"username": "skill_p2"})
    api_key = reg.json()["api_key"]
    headers = {"X-API-Key": api_key}
    agent_resp = await client.post(
        "/api/v1/agents", json={"name": "test"}, headers=headers
    )
    agent_id = agent_resp.json()["id"]

    await client.post(
        f"/api/v1/agents/{agent_id}/skills",
        json={"skill_id": "oil_painting"},
        headers=headers,
    )
    me = await client.get("/api/v1/auth/me", headers=headers)
    # 1000 - 50 (agent) - 100 (oil_painting) = 850
    assert me.json()["balance"] == 850.0


@pytest.mark.asyncio
async def test_buy_skill_missing_prereq(client):
    reg = await client.post("/api/v1/auth/register", json={"username": "skill_p3"})
    api_key = reg.json()["api_key"]
    headers = {"X-API-Key": api_key}
    agent_resp = await client.post(
        "/api/v1/agents", json={"name": "test"}, headers=headers
    )
    agent_id = agent_resp.json()["id"]

    response = await client.post(
        f"/api/v1/agents/{agent_id}/skills",
        json={"skill_id": "style_fusion"},
        headers=headers,
    )
    assert response.status_code == 400
    assert "prerequisite" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_buy_skill_already_owned(client):
    reg = await client.post("/api/v1/auth/register", json={"username": "skill_p4"})
    api_key = reg.json()["api_key"]
    headers = {"X-API-Key": api_key}
    agent_resp = await client.post(
        "/api/v1/agents", json={"name": "test"}, headers=headers
    )
    agent_id = agent_resp.json()["id"]

    response = await client.post(
        f"/api/v1/agents/{agent_id}/skills",
        json={"skill_id": "sketch"},
        headers=headers,
    )
    assert response.status_code == 400
    assert "already" in response.json()["detail"].lower()
