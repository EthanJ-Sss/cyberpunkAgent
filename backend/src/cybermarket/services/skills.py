from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from cybermarket.models.skill import SkillDefinition
from cybermarket.models.agent import PainterAgent
from cybermarket.models.player import Player
from cybermarket.data.seed_skills import SKILL_DEFINITIONS


async def ensure_skills_seeded(db: AsyncSession):
    result = await db.execute(select(SkillDefinition).limit(1))
    if not result.scalars().first():
        for skill_data in SKILL_DEFINITIONS:
            db.add(SkillDefinition(**skill_data))
        await db.commit()


async def get_all_skills(db: AsyncSession) -> list[SkillDefinition]:
    await ensure_skills_seeded(db)
    result = await db.execute(
        select(SkillDefinition).order_by(SkillDefinition.tier, SkillDefinition.id)
    )
    return list(result.scalars().all())


async def buy_skill(
    db: AsyncSession, agent: PainterAgent, player: Player, skill_id: str
) -> PainterAgent:
    await ensure_skills_seeded(db)

    result = await db.execute(
        select(SkillDefinition).where(SkillDefinition.id == skill_id)
    )
    skill = result.scalar_one_or_none()
    if not skill:
        raise ValueError(f"Skill '{skill_id}' not found")

    if skill_id in agent.skills:
        raise ValueError(f"Agent already has skill '{skill_id}'")

    for prereq in skill.prerequisites:
        if prereq not in agent.skills:
            raise ValueError(f"Missing prerequisite skill: {prereq}")

    if player.balance < skill.cost:
        raise ValueError(
            f"Insufficient balance. Need {skill.cost} CU, have {player.balance} CU"
        )

    player.balance -= skill.cost
    new_skills = list(agent.skills) + [skill_id]
    new_proficiency = dict(agent.skill_proficiency)
    new_proficiency[skill_id] = 30
    agent.skills = new_skills
    agent.skill_proficiency = new_proficiency
    await db.commit()
    await db.refresh(agent)
    return agent
