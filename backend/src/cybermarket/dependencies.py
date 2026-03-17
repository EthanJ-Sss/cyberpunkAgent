from fastapi import Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession

from cybermarket.database import get_db
from cybermarket.models.player import Player
from cybermarket.services.auth import get_player_by_api_key


async def get_current_player(
    x_api_key: str = Header(...),
    db: AsyncSession = Depends(get_db),
) -> Player:
    player = await get_player_by_api_key(db, x_api_key)
    if not player:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return player
