from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from cybermarket.models.artwork import Artwork
from cybermarket.models.trade import Trade
from cybermarket.models.agent import PainterAgent
from cybermarket.models.player import Player
from cybermarket.config import settings


async def execute_purchase(
    db: AsyncSession,
    artwork: Artwork,
    buyer: Player,
) -> Trade:
    if artwork.status != "listed":
        raise ValueError("Artwork is not listed for sale")
    if artwork.listed_price is None:
        raise ValueError("Artwork has no listed price")
    if buyer.balance < artwork.listed_price:
        raise ValueError("Insufficient balance")

    price = artwork.listed_price
    platform_fee = round(price * settings.platform_fee_rate, 2)
    seller_revenue = round(price - platform_fee, 2)

    buyer.balance -= price

    seller_agent = await db.get(PainterAgent, artwork.creator_agent_id)
    seller = await db.get(Player, seller_agent.player_id)
    seller.balance += seller_revenue
    seller_agent.total_sales = (seller_agent.total_sales or 0) + price

    artwork.status = "sold"
    artwork.sold_price = price
    artwork.buyer_id = buyer.id
    artwork.sold_at = datetime.now(timezone.utc)

    trade = Trade(
        artwork_id=artwork.id,
        seller_agent_id=artwork.creator_agent_id,
        buyer_id=buyer.id,
        price=price,
        platform_fee=platform_fee,
        royalty_fee=0,
        seller_revenue=seller_revenue,
        trade_type="direct",
    )
    db.add(trade)
    await db.commit()
    await db.refresh(trade)
    return trade
