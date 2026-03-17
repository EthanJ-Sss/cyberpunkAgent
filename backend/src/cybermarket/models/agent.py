import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Float, Integer, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cybermarket.database import Base


class PainterAgent(Base):
    __tablename__ = "painter_agents"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    player_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("players.id"))
    name: Mapped[str] = mapped_column(String(100))
    model_tier: Mapped[int] = mapped_column(Integer, default=1)
    skills: Mapped[list] = mapped_column(JSON, default=list)
    skill_proficiency: Mapped[dict] = mapped_column(JSON, default=dict)
    reputation_score: Mapped[float] = mapped_column(Float, default=0.0)
    reputation_level: Mapped[int] = mapped_column(Integer, default=1)
    style_tags: Mapped[list] = mapped_column(JSON, default=list)
    total_artworks: Mapped[int] = mapped_column(Integer, default=0)
    total_sales: Mapped[float] = mapped_column(Float, default=0.0)
    compute_consumed: Mapped[float] = mapped_column(Float, default=0.0)
    status: Mapped[str] = mapped_column(String(20), default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    player = relationship("Player", back_populates="agents")
    artworks = relationship("Artwork", back_populates="creator_agent")
