from pydantic import BaseModel
from uuid import UUID


class RegisterRequest(BaseModel):
    username: str


class RegisterResponse(BaseModel):
    id: UUID
    username: str
    api_key: str
    balance: float


class PlayerResponse(BaseModel):
    id: UUID
    username: str
    openclaw_endpoint: str | None
    balance: float


class BindOpenClawRequest(BaseModel):
    openclaw_endpoint: str
