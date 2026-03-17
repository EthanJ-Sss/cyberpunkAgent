from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from cybermarket.database import get_db
from cybermarket.dependencies import get_current_player
from cybermarket.models.player import Player
from cybermarket.schemas.artwork import (
    CreateArtworkRequest,
    ArtworkResponse,
    ListArtworkRequest,
)
from cybermarket.services.agent import get_agent
from cybermarket.services.artwork import create_artwork

router = APIRouter(prefix="/api/v1/artworks", tags=["artworks"])


def _artwork_to_response(artwork) -> ArtworkResponse:
    return ArtworkResponse(
        id=artwork.id,
        creator_agent_id=artwork.creator_agent_id,
        title=artwork.title,
        description=artwork.description,
        creative_concept=artwork.creative_concept,
        medium=artwork.medium,
        style_tags=artwork.style_tags,
        skills_used=artwork.skills_used,
        model_tier_at_creation=artwork.model_tier_at_creation,
        compute_cost=artwork.compute_cost,
        quality_score=artwork.quality_score,
        rarity_score=artwork.rarity_score,
        status=artwork.status,
        listed_price=artwork.listed_price,
        sold_price=artwork.sold_price,
        buyer_id=artwork.buyer_id,
        created_at=artwork.created_at,
    )


@router.post("", response_model=ArtworkResponse, status_code=201)
async def create(
    req: CreateArtworkRequest,
    player: Player = Depends(get_current_player),
    db: AsyncSession = Depends(get_db),
):
    agent = await get_agent(db, req.agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    if agent.player_id != player.id:
        raise HTTPException(status_code=403, detail="Not your agent")

    try:
        artwork = await create_artwork(
            db, agent, player,
            req.title, req.description, req.creative_concept,
            req.medium, req.skills_used,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return _artwork_to_response(artwork)


@router.get("/{artwork_id}", response_model=ArtworkResponse)
async def get_artwork(artwork_id: UUID, db: AsyncSession = Depends(get_db)):
    from sqlalchemy import select
    from cybermarket.models.artwork import Artwork

    result = await db.execute(select(Artwork).where(Artwork.id == artwork_id))
    artwork = result.scalar_one_or_none()
    if not artwork:
        raise HTTPException(status_code=404, detail="Artwork not found")
    return _artwork_to_response(artwork)


@router.post("/{artwork_id}/list", response_model=ArtworkResponse)
async def list_for_sale(
    artwork_id: UUID,
    req: ListArtworkRequest,
    player: Player = Depends(get_current_player),
    db: AsyncSession = Depends(get_db),
):
    from sqlalchemy import select
    from cybermarket.models.artwork import Artwork

    result = await db.execute(select(Artwork).where(Artwork.id == artwork_id))
    artwork = result.scalar_one_or_none()
    if not artwork:
        raise HTTPException(status_code=404, detail="Artwork not found")

    agent = await get_agent(db, artwork.creator_agent_id)
    if agent.player_id != player.id:
        raise HTTPException(status_code=403, detail="Not your artwork")

    if artwork.status != "draft":
        raise HTTPException(status_code=400, detail="Artwork is not in draft status")

    artwork.status = "listed"
    artwork.listed_price = req.price
    await db.commit()
    await db.refresh(artwork)
    return _artwork_to_response(artwork)


@router.post("/{artwork_id}/buy")
async def buy_artwork(
    artwork_id: UUID,
    player: Player = Depends(get_current_player),
    db: AsyncSession = Depends(get_db),
):
    from sqlalchemy import select
    from cybermarket.models.artwork import Artwork
    from cybermarket.services.economy import execute_purchase

    result = await db.execute(select(Artwork).where(Artwork.id == artwork_id))
    artwork = result.scalar_one_or_none()
    if not artwork:
        raise HTTPException(status_code=404, detail="Artwork not found")

    try:
        trade = await execute_purchase(db, artwork, player)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {
        "id": str(trade.id),
        "artwork_id": str(trade.artwork_id),
        "price": trade.price,
        "platform_fee": trade.platform_fee,
        "seller_revenue": trade.seller_revenue,
        "trade_type": trade.trade_type,
    }
