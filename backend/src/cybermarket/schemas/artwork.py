from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class CreateArtworkRequest(BaseModel):
    agent_id: UUID
    title: str
    description: str
    creative_concept: str
    medium: str
    skills_used: list[str]


class ArtworkResponse(BaseModel):
    id: UUID
    creator_agent_id: UUID
    title: str
    description: str
    creative_concept: str
    medium: str
    style_tags: list[str]
    skills_used: list[str]
    model_tier_at_creation: int
    compute_cost: float
    quality_score: float
    rarity_score: float
    status: str
    listed_price: float | None
    sold_price: float | None
    buyer_id: UUID | None
    created_at: datetime


class ListArtworkRequest(BaseModel):
    price: float
