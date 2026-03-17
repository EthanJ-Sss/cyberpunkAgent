from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from cybermarket.database import get_db
from cybermarket.dependencies import get_current_player
from cybermarket.models.player import Player
from cybermarket.schemas.skill import SkillResponse, BuySkillRequest
from cybermarket.services.skills import get_all_skills, buy_skill
from cybermarket.services.agent import get_agent

router = APIRouter(tags=["skills"])


@router.get("/api/v1/skills", response_model=list[SkillResponse])
async def list_skills(db: AsyncSession = Depends(get_db)):
    skills = await get_all_skills(db)
    return [
        SkillResponse(
            id=s.id,
            tier=s.tier,
            name=s.name,
            description=s.description,
            prerequisites=s.prerequisites,
            cost=s.cost,
            category=s.category,
        )
        for s in skills
    ]


@router.post("/api/v1/agents/{agent_id}/skills")
async def purchase_skill(
    agent_id: UUID,
    req: BuySkillRequest,
    player: Player = Depends(get_current_player),
    db: AsyncSession = Depends(get_db),
):
    agent = await get_agent(db, agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    if agent.player_id != player.id:
        raise HTTPException(status_code=403, detail="Not your agent")

    try:
        updated_agent = await buy_skill(db, agent, player, req.skill_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {
        "skills": updated_agent.skills,
        "skill_proficiency": updated_agent.skill_proficiency,
        "balance": player.balance,
    }
