from pydantic import BaseModel


class SkillResponse(BaseModel):
    id: str
    tier: int
    name: str
    description: str
    prerequisites: list[str]
    cost: float
    category: str


class BuySkillRequest(BaseModel):
    skill_id: str
