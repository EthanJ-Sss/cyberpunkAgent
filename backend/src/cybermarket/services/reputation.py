def get_reputation_level(
    total_sold: int, avg_score: float, total_revenue: float
) -> int:
    if total_sold >= 100 and avg_score >= 85 and total_revenue >= 20000:
        return 5
    if total_sold >= 50 and avg_score >= 75 and total_revenue >= 10000:
        return 4
    if total_sold >= 20 and avg_score >= 60 and total_revenue >= 2000:
        return 3
    if total_sold >= 5 and total_revenue >= 200:
        return 2
    return 1


def calculate_reputation_score(
    total_revenue: float,
    avg_quality: float,
    total_artworks: int,
    days_active: int,
    uniqueness_index: float = 50.0,
) -> float:
    revenue_score = min(100, total_revenue / 200)
    quality_score = avg_quality
    productivity = min(100, total_artworks * 5)
    activity = min(100, days_active * 10)

    score = (
        revenue_score * 0.30
        + quality_score * 0.25
        + productivity * 0.15
        + activity * 0.10
        + uniqueness_index * 0.20
    )
    return round(min(100, max(0, score)), 2)
