import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Float, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cybermarket.database import Base


class Player(Base):
    __tablename__ = "players"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    api_key: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    openclaw_endpoint: Mapped[str | None] = mapped_column(String(500), nullable=True)
    balance: Mapped[float] = mapped_column(Float, default=1000.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    agents = relationship("PainterAgent", back_populates="player")
