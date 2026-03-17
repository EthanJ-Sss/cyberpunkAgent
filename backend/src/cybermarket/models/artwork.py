import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Float, Integer, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cybermarket.database import Base


class Artwork(Base):
    __tablename__ = "artworks"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    creator_agent_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("painter_agents.id"))
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text)
    creative_concept: Mapped[str] = mapped_column(Text, default="")
    medium: Mapped[str] = mapped_column(String(50))
    style_tags: Mapped[list] = mapped_column(JSON, default=list)
    skills_used: Mapped[list] = mapped_column(JSON, default=list)
    model_tier_at_creation: Mapped[int] = mapped_column(Integer)
    compute_cost: Mapped[float] = mapped_column(Float)
    quality_score: Mapped[float] = mapped_column(Float, default=0.0)
    rarity_score: Mapped[float] = mapped_column(Float, default=0.0)
    status: Mapped[str] = mapped_column(String(20), default="draft")
    listed_price: Mapped[float | None] = mapped_column(Float, nullable=True)
    sold_price: Mapped[float | None] = mapped_column(Float, nullable=True)
    buyer_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("players.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    sold_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    creator_agent = relationship("PainterAgent", back_populates="artworks")
