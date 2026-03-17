from sqlalchemy import String, Float, Integer, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column

from cybermarket.database import Base


class SkillDefinition(Base):
    __tablename__ = "skill_definitions"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    tier: Mapped[int] = mapped_column(Integer)
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(Text)
    prerequisites: Mapped[list] = mapped_column(JSON, default=list)
    cost: Mapped[float] = mapped_column(Float, default=0.0)
    category: Mapped[str] = mapped_column(String(50))
