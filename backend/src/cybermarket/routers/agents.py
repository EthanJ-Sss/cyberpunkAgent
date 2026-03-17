from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from cybermarket.database import get_db
from cybermarket.dependencies import get_current_player
from cybermarket.models.player import Player
from cybermarket.schemas.agent import CreateAgentRequest, AgentResponse
from cybermarket.services.agent import create_agent, get_player_agents, get_agent

router = APIRouter(prefix="/api/v1/agents", tags=["agents"])


def _agent_to_response(agent) -> AgentResponse:
    return AgentResponse(
        id=agent.id,
        name=agent.name,
        model_tier=agent.model_tier,
        skills=agent.skills,
        skill_proficiency=agent.skill_proficiency,
        reputation_score=agent.reputation_score,
        reputation_level=agent.reputation_level,
        style_tags=agent.style_tags,
        total_artworks=agent.total_artworks,
        total_sales=agent.total_sales,
        compute_consumed=agent.compute_consumed,
        status=agent.status,
    )


@router.post("", response_model=AgentResponse, status_code=201)
async def create(
    req: CreateAgentRequest,
    player: Player = Depends(get_current_player),
    db: AsyncSession = Depends(get_db),
):
    try:
        agent = await create_agent(db, player, req.name, req.model_tier)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return _agent_to_response(agent)


@router.get("", response_model=list[AgentResponse])
async def list_agents(
    player: Player = Depends(get_current_player),
    db: AsyncSession = Depends(get_db),
):
    agents = await get_player_agents(db, player.id)
    return [_agent_to_response(a) for a in agents]


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent_detail(
    agent_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    agent = await get_agent(db, agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return _agent_to_response(agent)
