import pytest


@pytest.mark.asyncio
async def test_create_agent(client):
    reg = await client.post("/api/v1/auth/register", json={"username": "p1"})
    api_key = reg.json()["api_key"]
    headers = {"X-API-Key": api_key}

    response = await client.post(
        "/api/v1/agents", json={"name": "梵高-7B"}, headers=headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "梵高-7B"
    assert data["model_tier"] == 1
    assert "sketch" in data["skills"]
    assert "color_fill" in data["skills"]
    assert "basic_composition" in data["skills"]


@pytest.mark.asyncio
async def test_create_agent_deducts_balance(client):
    reg = await client.post("/api/v1/auth/register", json={"username": "p2"})
    api_key = reg.json()["api_key"]
    headers = {"X-API-Key": api_key}

    await client.post("/api/v1/agents", json={"name": "test"}, headers=headers)
    me = await client.get("/api/v1/auth/me", headers=headers)
    assert me.json()["balance"] == 950.0


@pytest.mark.asyncio
async def test_create_agent_insufficient_balance(client):
    reg = await client.post("/api/v1/auth/register", json={"username": "p3"})
    api_key = reg.json()["api_key"]
    headers = {"X-API-Key": api_key}

    # Create 20 agents to drain balance (20 * 50 = 1000)
    for i in range(20):
        await client.post(
            "/api/v1/agents", json={"name": f"agent{i}"}, headers=headers
        )

    response = await client.post(
        "/api/v1/agents", json={"name": "one_too_many"}, headers=headers
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_list_my_agents(client):
    reg = await client.post("/api/v1/auth/register", json={"username": "p4"})
    api_key = reg.json()["api_key"]
    headers = {"X-API-Key": api_key}

    await client.post("/api/v1/agents", json={"name": "Agent1"}, headers=headers)
    await client.post("/api/v1/agents", json={"name": "Agent2"}, headers=headers)

    response = await client.get("/api/v1/agents", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 2


@pytest.mark.asyncio
async def test_get_agent_detail(client):
    reg = await client.post("/api/v1/auth/register", json={"username": "p5"})
    api_key = reg.json()["api_key"]
    headers = {"X-API-Key": api_key}

    create_resp = await client.post(
        "/api/v1/agents", json={"name": "DetailAgent"}, headers=headers
    )
    agent_id = create_resp.json()["id"]

    response = await client.get(f"/api/v1/agents/{agent_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["name"] == "DetailAgent"
