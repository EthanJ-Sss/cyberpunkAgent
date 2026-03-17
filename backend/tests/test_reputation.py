from cybermarket.services.reputation import get_reputation_level, calculate_reputation_score


def test_reputation_level_new():
    assert get_reputation_level(0, 0, 0) == 1


def test_reputation_level_beginner():
    assert get_reputation_level(total_sold=5, avg_score=50, total_revenue=250) == 2


def test_reputation_level_intermediate():
    assert get_reputation_level(total_sold=20, avg_score=65, total_revenue=2500) == 3


def test_reputation_level_advanced():
    assert get_reputation_level(total_sold=50, avg_score=80, total_revenue=12000) == 4


def test_reputation_level_master():
    assert get_reputation_level(total_sold=100, avg_score=90, total_revenue=50000) == 5


def test_reputation_score_basic():
    score = calculate_reputation_score(
        total_revenue=1000, avg_quality=60, total_artworks=10, days_active=5
    )
    assert 0 <= score <= 100


def test_reputation_score_zero():
    score = calculate_reputation_score(
        total_revenue=0, avg_quality=0, total_artworks=0, days_active=0
    )
    assert score == 10.0  # only uniqueness_index default (50 * 0.20 = 10)
