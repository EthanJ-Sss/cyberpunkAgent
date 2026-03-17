from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from cybermarket.database import get_db
from cybermarket.schemas.artwork import ArtworkResponse
from cybermarket.schemas.market import MarketOverview
from cybermarket.services.market import get_market_overview, get_market_listings

router = APIRouter(prefix="/api/v1/market", tags=["market"])


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


@router.get("/overview", response_model=MarketOverview)
async def overview(db: AsyncSession = Depends(get_db)):
    data = await get_market_overview(db)
    return MarketOverview(**data)


@router.get("/listings", response_model=list[ArtworkResponse])
async def listings(
    medium: str | None = Query(None),
    min_price: float | None = Query(None),
    max_price: float | None = Query(None),
    sort_by: str = Query("created_at"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    artworks = await get_market_listings(
        db, medium=medium, min_price=min_price, max_price=max_price,
        sort_by=sort_by, limit=limit, offset=offset,
    )
    return [_artwork_to_response(a) for a in artworks]
