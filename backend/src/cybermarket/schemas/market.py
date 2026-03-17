from pydantic import BaseModel


class MarketOverview(BaseModel):
    total_listings: int
    total_agents: int
    total_trade_volume: float


class TradeResponse(BaseModel):
    id: str
    artwork_id: str
    seller_agent_id: str
    buyer_id: str
    price: float
    platform_fee: float
    royalty_fee: float
    seller_revenue: float
    trade_type: str
