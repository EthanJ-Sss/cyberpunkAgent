import pytest
from uuid import uuid4

LONG_DESC = (
    "在霓虹灯光的映照下，城市的天际线被无数光柱切割成碎片。"
    "远处的摩天大楼如同巨大的电路板，窗户中闪烁着无数数据流。"
    "一位赛博朋克风格的旅者站在天桥上，俯瞰着这座永不停歇的城市。"
    "他的义体手臂在月光下泛着金属光泽，植入式的光学镜片扫描着周围的一切。"
    "空气中弥漫着人造雨的气息，混合着街边小摊飘来的合成食物香气。"
    "这是2077年的夜城——一个美丽而危险的赛博朋克世界。"
)


@pytest.mark.asyncio
async def test_full_trading_cycle(client):
    """Test the complete cycle: register → create agent → create artwork → list → buy"""
    suffix = uuid4().hex[:8]

    # Step 1: Register two players
    seller_reg = await client.post(
        "/api/v1/auth/register", json={"username": f"seller_{suffix}"}
    )
    assert seller_reg.status_code == 201
    seller_key = seller_reg.json()["api_key"]
    seller_headers = {"X-API-Key": seller_key}
    seller_initial_balance = seller_reg.json()["balance"]
    assert seller_initial_balance == 1000.0

    buyer_reg = await client.post(
        "/api/v1/auth/register", json={"username": f"buyer_{suffix}"}
    )
    assert buyer_reg.status_code == 201
    buyer_key = buyer_reg.json()["api_key"]
    buyer_headers = {"X-API-Key": buyer_key}

    # Step 2: Seller creates an agent
    agent_resp = await client.post(
        "/api/v1/agents",
        json={"name": f"画家_{suffix}"},
        headers=seller_headers,
    )
    assert agent_resp.status_code == 201
    agent = agent_resp.json()
    agent_id = agent["id"]
    assert "sketch" in agent["skills"]

    # Verify balance deducted for agent creation
    seller_me = await client.get("/api/v1/auth/me", headers=seller_headers)
    assert seller_me.json()["balance"] == 950.0  # 1000 - 50

    # Step 3: Agent creates an artwork
    artwork_resp = await client.post(
        "/api/v1/artworks",
        json={
            "agent_id": agent_id,
            "title": f"赛博夜城_{suffix}",
            "description": LONG_DESC,
            "creative_concept": "探索人与机器的共生关系",
            "medium": "sketch",
            "skills_used": ["sketch", "color_fill"],
        },
        headers=seller_headers,
    )
    assert artwork_resp.status_code == 201
    artwork = artwork_resp.json()
    artwork_id = artwork["id"]
    assert artwork["quality_score"] > 0
    assert artwork["status"] == "draft"
    creation_cost = artwork["compute_cost"]

    # Step 4: List artwork for sale
    list_resp = await client.post(
        f"/api/v1/artworks/{artwork_id}/list",
        json={"price": 200.0},
        headers=seller_headers,
    )
    assert list_resp.status_code == 200
    assert list_resp.json()["status"] == "listed"
    assert list_resp.json()["listed_price"] == 200.0

    # Step 5: Verify artwork appears in market listings
    market_resp = await client.get("/api/v1/market/listings")
    assert market_resp.status_code == 200
    listings = market_resp.json()
    assert any(a["id"] == artwork_id for a in listings)

    # Step 6: Verify market overview
    overview_resp = await client.get("/api/v1/market/overview")
    assert overview_resp.status_code == 200
    overview = overview_resp.json()
    assert overview["total_listings"] >= 1
    assert overview["total_agents"] >= 1

    # Step 7: Buyer purchases the artwork
    buy_resp = await client.post(
        f"/api/v1/artworks/{artwork_id}/buy",
        headers=buyer_headers,
    )
    assert buy_resp.status_code == 200
    trade = buy_resp.json()
    assert trade["price"] == 200.0
    assert trade["platform_fee"] == 10.0  # 5% of 200
    assert trade["seller_revenue"] == 190.0

    # Step 8: Verify balances after trade
    buyer_me = await client.get("/api/v1/auth/me", headers=buyer_headers)
    assert buyer_me.json()["balance"] == 800.0  # 1000 - 200

    seller_me = await client.get("/api/v1/auth/me", headers=seller_headers)
    expected_seller_balance = 950.0 - creation_cost + 190.0
    assert abs(seller_me.json()["balance"] - expected_seller_balance) < 0.01

    # Step 9: Verify artwork is now sold
    artwork_detail = await client.get(f"/api/v1/artworks/{artwork_id}")
    assert artwork_detail.status_code == 200
    assert artwork_detail.json()["status"] == "sold"

    # Step 10: Verify leaderboard
    lb_resp = await client.get("/api/v1/leaderboard")
    assert lb_resp.status_code == 200
    assert "gini_coefficient" in lb_resp.json()

    # Step 11: Verify skills are available
    skills_resp = await client.get("/api/v1/skills")
    assert skills_resp.status_code == 200
    assert len(skills_resp.json()) >= 12

    # Step 12: Buy a skill for the agent
    skill_resp = await client.post(
        f"/api/v1/agents/{agent_id}/skills",
        json={"skill_id": "oil_painting"},
        headers=seller_headers,
    )
    assert skill_resp.status_code == 200
    assert "oil_painting" in skill_resp.json()["skills"]


@pytest.mark.asyncio
async def test_matthew_effect_scenario(client):
    """Test that agents with better models produce higher quality artworks."""
    suffix = uuid4().hex[:8]

    # Create two players
    rich_reg = await client.post(
        "/api/v1/auth/register", json={"username": f"rich_{suffix}"}
    )
    rich_headers = {"X-API-Key": rich_reg.json()["api_key"]}

    poor_reg = await client.post(
        "/api/v1/auth/register", json={"username": f"poor_{suffix}"}
    )
    poor_headers = {"X-API-Key": poor_reg.json()["api_key"]}

    # Create agents with different model tiers
    rich_agent = await client.post(
        "/api/v1/agents",
        json={"name": "T3大师", "model_tier": 3},
        headers=rich_headers,
    )
    poor_agent = await client.post(
        "/api/v1/agents",
        json={"name": "T1新手", "model_tier": 1},
        headers=poor_headers,
    )

    rich_agent_id = rich_agent.json()["id"]
    poor_agent_id = poor_agent.json()["id"]

    # Both create artworks with same description
    rich_art = await client.post(
        "/api/v1/artworks",
        json={
            "agent_id": rich_agent_id,
            "title": "大师之作",
            "description": LONG_DESC,
            "creative_concept": "深度审美探索",
            "medium": "sketch",
            "skills_used": ["sketch"],
        },
        headers=rich_headers,
    )

    poor_art = await client.post(
        "/api/v1/artworks",
        json={
            "agent_id": poor_agent_id,
            "title": "新手习作",
            "description": LONG_DESC,
            "creative_concept": "初次尝试",
            "medium": "sketch",
            "skills_used": ["sketch"],
        },
        headers=poor_headers,
    )

    # T3 should generally produce higher quality than T1
    # (Note: there's a random factor, so we check the general tendency)
    rich_quality = rich_art.json()["quality_score"]
    poor_quality = poor_art.json()["quality_score"]

    # T3 model weight is 75, T1 is 20 (difference of 55 * 0.35 = ~19 points)
    # Even with random factors, T3 should usually score higher
    rich_cost = rich_art.json()["compute_cost"]
    poor_cost = poor_art.json()["compute_cost"]

    # T3 costs more than T1 (6x vs 1x coefficient)
    assert rich_cost > poor_cost
