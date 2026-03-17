from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from cybermarket.models.agent import PainterAgent


async def get_leaderboard(
    db: AsyncSession, sort_by: str = "reputation", limit: int = 20
) -> list[PainterAgent]:
    if sort_by == "sales":
        query = select(PainterAgent).order_by(PainterAgent.total_sales.desc())
    elif sort_by == "artworks":
        query = select(PainterAgent).order_by(PainterAgent.total_artworks.desc())
    else:
        query = select(PainterAgent).order_by(PainterAgent.reputation_score.desc())

    query = query.limit(limit)
    result = await db.execute(query)
    return list(result.scalars().all())


def calculate_gini_coefficient(values: list[float]) -> float:
    if not values or all(v == 0 for v in values):
        return 0.0

    sorted_vals = sorted(values)
    n = len(sorted_vals)
    total = sum(sorted_vals)
    if total == 0:
        return 0.0

    cumulative = 0.0
    weighted_sum = 0.0
    for i, val in enumerate(sorted_vals):
        cumulative += val
        weighted_sum += (2 * (i + 1) - n - 1) * val

    gini = weighted_sum / (n * total)
    return round(max(0, min(1, gini)), 4)
