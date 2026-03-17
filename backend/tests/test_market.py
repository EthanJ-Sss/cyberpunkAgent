import pytest
from uuid import uuid4

LONG_DESC = "在霓虹灯光的映照下，一座废弃的摩天大楼矗立在夕阳中。赛博朋克风格的水彩画，用柔和的色彩描绘出硬朗的城市轮廓。" * 3


async def _setup_listed_artwork(client):
    """Create a player with an agent that has a listed artwork."""
    reg = await client.post("/api/v1/auth/register", json={"username": f"seller_{uuid4().hex[:8]}"})
    api_key = reg.json()["api_key"]
    headers = {"X-API-Key": api_key}
    agent = await client.post("/api/v1/agents", json={"name": "seller_agent"}, headers=headers)
    agent_id = agent.json()["id"]

    art = await client.post("/api/v1/artworks", json={
        "agent_id": agent_id,
        "title": "Artwork for sale",
        "description": LONG_DESC,
        "creative_concept": "test",
        "medium": "sketch",
        "skills_used": ["sketch"],
    }, headers=headers)
    artwork_id = art.json()["id"]

    await client.post(
        f"/api/v1/artworks/{artwork_id}/list",
        json={"price": 100.0},
        headers=headers,
    )
    return artwork_id, headers


@pytest.mark.asyncio
async def test_buy_artwork(client):
    artwork_id, seller_headers = await _setup_listed_artwork(client)

    buyer_reg = await client.post("/api/v1/auth/register", json={"username": f"buyer_{uuid4().hex[:8]}"})
    buyer_key = buyer_reg.json()["api_key"]
    buyer_headers = {"X-API-Key": buyer_key}

    response = await client.post(
        f"/api/v1/artworks/{artwork_id}/buy",
        headers=buyer_headers,
    )
    assert response.status_code == 200
    trade = response.json()
    assert trade["price"] == 100.0
    assert trade["platform_fee"] == 5.0
    assert trade["seller_revenue"] == 95.0


@pytest.mark.asyncio
async def test_buy_artwork_insufficient_balance(client):
    artwork_id, _ = await _setup_listed_artwork(client)

    # Create buyer and drain their balance
    buyer_reg = await client.post("/api/v1/auth/register", json={"username": f"broke_buyer_{uuid4().hex[:8]}"})
    buyer_key = buyer_reg.json()["api_key"]
    buyer_headers = {"X-API-Key": buyer_key}

    # Create many agents to drain balance
    for i in range(20):
        await client.post("/api/v1/agents", json={"name": f"drain{i}"}, headers=buyer_headers)

    response = await client.post(
        f"/api/v1/artworks/{artwork_id}/buy",
        headers=buyer_headers,
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_market_overview(client):
    response = await client.get("/api/v1/market/overview")
    assert response.status_code == 200
    data = response.json()
    assert "total_listings" in data
    assert "total_agents" in data
    assert "total_trade_volume" in data


@pytest.mark.asyncio
async def test_market_listings(client):
    response = await client.get("/api/v1/market/listings")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_market_listings_with_filter(client):
    await _setup_listed_artwork(client)
    response = await client.get("/api/v1/market/listings?medium=sketch")
    assert response.status_code == 200
    listings = response.json()
    assert len(listings) >= 1
    for listing in listings:
        assert listing["medium"] == "sketch"
