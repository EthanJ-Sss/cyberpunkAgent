from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from cybermarket.models.artwork import Artwork
from cybermarket.models.agent import PainterAgent
from cybermarket.models.player import Player
from cybermarket.services.scoring import (
    calculate_quality_score,
    calculate_creation_cost,
    calculate_rarity_score,
)


async def create_artwork(
    db: AsyncSession,
    agent: PainterAgent,
    player: Player,
    title: str,
    description: str,
    creative_concept: str,
    medium: str,
    skills_used: list[str],
) -> Artwork:
    for skill in skills_used:
        if skill not in agent.skills:
            raise ValueError(f"Agent does not have skill: {skill}")

    cost = calculate_creation_cost(agent.model_tier, len(skills_used))
    if player.balance < cost:
        raise ValueError(
            f"Insufficient balance. Need {cost} CU, have {player.balance} CU"
        )

    prof_values = [agent.skill_proficiency.get(s, 30) for s in skills_used]
    avg_prof = sum(prof_values) / len(prof_values) if prof_values else 0

    count_result = await db.execute(select(func.count()).select_from(Artwork))
    total_artworks = count_result.scalar() or 0

    medium_count_result = await db.execute(
        select(func.count()).select_from(Artwork).where(Artwork.medium == medium)
    )
    same_medium_count = medium_count_result.scalar() or 0

    quality = calculate_quality_score(
        agent.model_tier, avg_prof, description, total_artworks
    )
    rarity = calculate_rarity_score(
        same_medium_count, len(skills_used), agent.reputation_score, cost
    )

    player.balance -= cost
    agent.compute_consumed = (agent.compute_consumed or 0) + cost
    agent.total_artworks = (agent.total_artworks or 0) + 1

    artwork = Artwork(
        creator_agent_id=agent.id,
        title=title,
        description=description,
        creative_concept=creative_concept,
        medium=medium,
        style_tags=[],
        skills_used=skills_used,
        model_tier_at_creation=agent.model_tier,
        compute_cost=cost,
        quality_score=quality,
        rarity_score=rarity,
        status="draft",
    )
    db.add(artwork)
    await db.commit()
    await db.refresh(artwork)
    return artwork
