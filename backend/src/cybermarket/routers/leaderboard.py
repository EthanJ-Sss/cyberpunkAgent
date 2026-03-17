from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from cybermarket.database import get_db
from cybermarket.models.agent import PainterAgent
from cybermarket.services.leaderboard import get_leaderboard, calculate_gini_coefficient

router = APIRouter(prefix="/api/v1/leaderboard", tags=["leaderboard"])


@router.get("")
async def leaderboard(
    sort_by: str = Query("reputation", pattern="^(reputation|sales|artworks)$"),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    agents = await get_leaderboard(db, sort_by=sort_by, limit=limit)

    result = await db.execute(select(PainterAgent.total_sales))
    all_sales = [row[0] or 0.0 for row in result.all()]
    gini = calculate_gini_coefficient(all_sales)

    return {
        "by_" + sort_by: [
            {
                "id": str(a.id),
                "name": a.name,
                "reputation_score": a.reputation_score,
                "reputation_level": a.reputation_level,
                "total_sales": a.total_sales,
                "total_artworks": a.total_artworks,
            }
            for a in agents
        ],
        "gini_coefficient": gini,
    }
