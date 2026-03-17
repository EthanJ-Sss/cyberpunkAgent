import secrets

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from cybermarket.models.player import Player
from cybermarket.config import settings


async def register_player(db: AsyncSession, username: str) -> Player:
    existing = await db.execute(select(Player).where(Player.username == username))
    if existing.scalar_one_or_none():
        raise ValueError("Username already exists")

    api_key = f"{settings.api_key_prefix}{secrets.token_urlsafe(32)}"
    player = Player(username=username, api_key=api_key, balance=settings.initial_balance)
    db.add(player)
    await db.commit()
    await db.refresh(player)
    return player


async def get_player_by_api_key(db: AsyncSession, api_key: str) -> Player | None:
    result = await db.execute(select(Player).where(Player.api_key == api_key))
    return result.scalar_one_or_none()
