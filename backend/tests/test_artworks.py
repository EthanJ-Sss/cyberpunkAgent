import pytest
from uuid import uuid4

LONG_DESC = "在霓虹灯光的映照下，一座废弃的摩天大楼矗立在夕阳中。赛博朋克风格的水彩画，用柔和的色彩描绘出硬朗的城市轮廓。" * 3


async def _create_agent(client):
    reg = await client.post("/api/v1/auth/register", json={"username": f"artist_{uuid4().hex[:8]}"})
    api_key = reg.json()["api_key"]
    headers = {"X-API-Key": api_key}
    agent = await client.post("/api/v1/agents", json={"name": "painter"}, headers=headers)
    return agent.json()["id"], headers, api_key


@pytest.mark.asyncio
async def test_create_artwork(client):
    agent_id, headers, _ = await _create_agent(client)
    response = await client.post("/api/v1/artworks", json={
        "agent_id": agent_id,
        "title": "赛博黄昏",
        "description": LONG_DESC,
        "creative_concept": "探索科技与自然的对立统一",
        "medium": "sketch",
        "skills_used": ["sketch", "color_fill"],
    }, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "赛博黄昏"
    assert data["quality_score"] > 0
    assert data["compute_cost"] > 0
    assert data["status"] == "draft"


@pytest.mark.asyncio
async def test_create_artwork_missing_skill(client):
    agent_id, headers, _ = await _create_agent(client)
    response = await client.post("/api/v1/artworks", json={
        "agent_id": agent_id,
        "title": "test",
        "description": LONG_DESC,
        "creative_concept": "test",
        "medium": "oil_painting",
        "skills_used": ["oil_painting"],
    }, headers=headers)
    assert response.status_code == 400
    assert "skill" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_list_artwork_for_sale(client):
    agent_id, headers, _ = await _create_agent(client)
    art = await client.post("/api/v1/artworks", json={
        "agent_id": agent_id,
        "title": "For Sale",
        "description": LONG_DESC,
        "creative_concept": "test",
        "medium": "sketch",
        "skills_used": ["sketch"],
    }, headers=headers)
    artwork_id = art.json()["id"]

    response = await client.post(
        f"/api/v1/artworks/{artwork_id}/list",
        json={"price": 100.0},
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json()["status"] == "listed"
    assert response.json()["listed_price"] == 100.0
