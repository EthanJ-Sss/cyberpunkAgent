from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from cybermarket.models.agent import PainterAgent
from cybermarket.models.player import Player
from cybermarket.config import settings

INITIAL_SKILLS = ["sketch", "color_fill", "basic_composition"]
INITIAL_PROFICIENCY = {s: 50 for s in INITIAL_SKILLS}


async def create_agent(
    db: AsyncSession, player: Player, name: str, model_tier: int = 1
) -> PainterAgent:
    if player.balance < settings.agent_creation_cost:
        raise ValueError("Insufficient balance to create agent")

    player.balance -= settings.agent_creation_cost
    agent = PainterAgent(
        player_id=player.id,
        name=name,
        model_tier=model_tier,
        skills=list(INITIAL_SKILLS),
        skill_proficiency=dict(INITIAL_PROFICIENCY),
        status="active",
    )
    db.add(agent)
    await db.commit()
    await db.refresh(agent)
    return agent


async def get_player_agents(db: AsyncSession, player_id) -> list[PainterAgent]:
    result = await db.execute(
        select(PainterAgent).where(PainterAgent.player_id == player_id)
    )
    return list(result.scalars().all())


async def get_agent(db: AsyncSession, agent_id) -> PainterAgent | None:
    result = await db.execute(
        select(PainterAgent).where(PainterAgent.id == agent_id)
    )
    return result.scalar_one_or_none()
