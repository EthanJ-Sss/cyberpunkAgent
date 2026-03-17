from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from cybermarket.models.artwork import Artwork
from cybermarket.models.agent import PainterAgent


async def get_market_overview(db: AsyncSession) -> dict:
    listings = await db.execute(
        select(func.count()).select_from(Artwork).where(Artwork.status == "listed")
    )
    agents = await db.execute(select(func.count()).select_from(PainterAgent))
    total_volume = await db.execute(
        select(func.coalesce(func.sum(Artwork.sold_price), 0))
        .select_from(Artwork)
        .where(Artwork.status == "sold")
    )
    return {
        "total_listings": listings.scalar() or 0,
        "total_agents": agents.scalar() or 0,
        "total_trade_volume": float(total_volume.scalar() or 0),
    }


async def get_market_listings(
    db: AsyncSession,
    medium: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    sort_by: str = "created_at",
    limit: int = 50,
    offset: int = 0,
) -> list[Artwork]:
    query = select(Artwork).where(Artwork.status == "listed")
    if medium:
        query = query.where(Artwork.medium == medium)
    if min_price is not None:
        query = query.where(Artwork.listed_price >= min_price)
    if max_price is not None:
        query = query.where(Artwork.listed_price <= max_price)

    valid_sort_fields = {"created_at", "listed_price", "quality_score", "rarity_score"}
    sort_field = sort_by if sort_by in valid_sort_fields else "created_at"
    query = query.order_by(getattr(Artwork, sort_field).desc())
    query = query.limit(limit).offset(offset)

    result = await db.execute(query)
    return list(result.scalars().all())
