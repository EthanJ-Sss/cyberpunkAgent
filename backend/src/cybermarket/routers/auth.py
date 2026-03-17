from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from cybermarket.database import get_db
from cybermarket.dependencies import get_current_player
from cybermarket.models.player import Player
from cybermarket.schemas.auth import (
    RegisterRequest,
    RegisterResponse,
    PlayerResponse,
    BindOpenClawRequest,
)
from cybermarket.services.auth import register_player

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/register", response_model=RegisterResponse, status_code=201)
async def register(req: RegisterRequest, db: AsyncSession = Depends(get_db)):
    try:
        player = await register_player(db, req.username)
    except ValueError:
        raise HTTPException(status_code=409, detail="Username already exists")
    return RegisterResponse(
        id=player.id,
        username=player.username,
        api_key=player.api_key,
        balance=player.balance,
    )


@router.get("/me", response_model=PlayerResponse)
async def me(player: Player = Depends(get_current_player)):
    return PlayerResponse(
        id=player.id,
        username=player.username,
        openclaw_endpoint=player.openclaw_endpoint,
        balance=player.balance,
    )


@router.post("/bind-openclaw")
async def bind_openclaw(
    req: BindOpenClawRequest,
    player: Player = Depends(get_current_player),
    db: AsyncSession = Depends(get_db),
):
    player.openclaw_endpoint = req.openclaw_endpoint
    await db.commit()
    return {"status": "bound", "openclaw_endpoint": req.openclaw_endpoint}
