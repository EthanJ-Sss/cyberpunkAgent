import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Float, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from cybermarket.database import Base


class Trade(Base):
    __tablename__ = "trades"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    artwork_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("artworks.id"))
    seller_agent_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("painter_agents.id"))
    buyer_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("players.id"))
    price: Mapped[float] = mapped_column(Float)
    platform_fee: Mapped[float] = mapped_column(Float)
    royalty_fee: Mapped[float] = mapped_column(Float, default=0.0)
    seller_revenue: Mapped[float] = mapped_column(Float)
    trade_type: Mapped[str] = mapped_column(String(20), default="direct")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
