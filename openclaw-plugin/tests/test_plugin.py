import pytest
from unittest.mock import AsyncMock, patch

from cybermarket_plugin.client import CyberMarketClient
from cybermarket_plugin.tools import CYBERMARKET_TOOLS
from cybermarket_plugin.agent_prompt import build_prompt


def test_tools_structure():
    assert len(CYBERMARKET_TOOLS) == 6
    tool_names = [t["function"]["name"] for t in CYBERMARKET_TOOLS]
    assert "observe_market" in tool_names
    assert "create_artwork" in tool_names
    assert "list_for_sale" in tool_names
    assert "buy_artwork" in tool_names
    assert "get_my_status" in tool_names
    assert "learn_skill" in tool_names


def test_build_prompt():
    prompt = build_prompt(
        agent_name="梵高-7B",
        agent_id="abc-123",
        model_tier=2,
        skills=["sketch", "oil_painting"],
        reputation_level=3,
    )
    assert "梵高-7B" in prompt
    assert "abc-123" in prompt
    assert "T2" in prompt
    assert "sketch" in prompt
    assert "3 星" in prompt


@pytest.mark.asyncio
async def test_observe_market():
    client = CyberMarketClient(base_url="http://test", api_key="cm_test")
    with patch.object(client, "_request", new_callable=AsyncMock) as mock:
        mock.side_effect = [
            {"total_listings": 10, "total_agents": 5, "total_trade_volume": 500},
            [{"id": "1", "title": "test"}],
        ]
        result = await client.observe_market()
        assert result["overview"]["total_listings"] == 10
        assert len(result["recent_listings"]) == 1


@pytest.mark.asyncio
async def test_create_artwork():
    client = CyberMarketClient(base_url="http://test", api_key="cm_test")
    with patch.object(client, "_request", new_callable=AsyncMock) as mock:
        mock.return_value = {"id": "abc", "title": "test", "quality_score": 50}
        result = await client.create_artwork(
            agent_id="agent1",
            title="test",
            description="desc",
            creative_concept="concept",
            medium="sketch",
            skills_used=["sketch"],
        )
        assert result["title"] == "test"


@pytest.mark.asyncio
async def test_get_my_status():
    client = CyberMarketClient(base_url="http://test", api_key="cm_test")
    with patch.object(client, "_request", new_callable=AsyncMock) as mock:
        mock.side_effect = [
            {"id": "p1", "username": "test", "balance": 900},
            [{"id": "a1", "name": "agent1"}],
        ]
        result = await client.get_my_status()
        assert result["player"]["balance"] == 900
        assert len(result["agents"]) == 1
