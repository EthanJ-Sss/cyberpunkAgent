import pytest


@pytest.mark.asyncio
async def test_leaderboard(client):
    response = await client.get("/api/v1/leaderboard")
    assert response.status_code == 200
    data = response.json()
    assert "by_reputation" in data
    assert "gini_coefficient" in data
    assert isinstance(data["gini_coefficient"], float)


@pytest.mark.asyncio
async def test_leaderboard_by_sales(client):
    response = await client.get("/api/v1/leaderboard?sort_by=sales")
    assert response.status_code == 200
    data = response.json()
    assert "by_sales" in data


def test_gini_coefficient():
    from cybermarket.services.leaderboard import calculate_gini_coefficient

    assert calculate_gini_coefficient([]) == 0.0
    assert calculate_gini_coefficient([100, 100, 100]) == 0.0
    gini = calculate_gini_coefficient([0, 0, 0, 100])
    assert gini > 0.5  # very unequal
