import pytest

from cybermarket.models.player import Player
from cybermarket.models.agent import PainterAgent


@pytest.mark.asyncio
async def test_create_player(db_session):
    player = Player(username="test_player", api_key="cm_test123", balance=1000.0)
    db_session.add(player)
    await db_session.commit()
    await db_session.refresh(player)
    assert player.id is not None
    assert player.balance == 1000.0


@pytest.mark.asyncio
async def test_create_agent(db_session):
    player = Player(username="test_player2", api_key="cm_test456", balance=1000.0)
    db_session.add(player)
    await db_session.commit()

    agent = PainterAgent(
        player_id=player.id,
        name="梵高-7B",
        model_tier=1,
        skills=["sketch", "color_fill", "basic_composition"],
        skill_proficiency={"sketch": 50, "color_fill": 50, "basic_composition": 50},
        status="active",
    )
    db_session.add(agent)
    await db_session.commit()
    await db_session.refresh(agent)
    assert agent.id is not None
    assert agent.player_id == player.id
