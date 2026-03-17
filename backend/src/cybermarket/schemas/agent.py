from pydantic import BaseModel
from uuid import UUID


class CreateAgentRequest(BaseModel):
    name: str
    model_tier: int = 1


class AgentResponse(BaseModel):
    id: UUID
    name: str
    model_tier: int
    skills: list[str]
    skill_proficiency: dict[str, int]
    reputation_score: float
    reputation_level: int
    style_tags: list[str]
    total_artworks: int
    total_sales: float
    compute_consumed: float
    status: str


class AgentFinancials(BaseModel):
    agent_id: UUID
    total_revenue: float
    total_cost: float
    net_profit: float
    total_artworks: int
    total_sold: int
