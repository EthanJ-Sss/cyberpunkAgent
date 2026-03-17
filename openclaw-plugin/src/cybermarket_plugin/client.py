import httpx


class CyberMarketClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.headers = {"X-API-Key": api_key}

    async def _request(self, method: str, path: str, **kwargs):
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method,
                f"{self.base_url}{path}",
                headers=self.headers,
                **kwargs,
            )
            response.raise_for_status()
            return response.json()

    async def observe_market(self, category: str | None = None) -> dict:
        params = {}
        if category:
            params["medium"] = category
        overview = await self._request("GET", "/api/v1/market/overview")
        listings = await self._request(
            "GET", "/api/v1/market/listings", params=params
        )
        return {"overview": overview, "recent_listings": listings[:10]}

    async def create_artwork(
        self,
        agent_id: str,
        title: str,
        description: str,
        creative_concept: str,
        medium: str,
        skills_used: list[str],
    ) -> dict:
        return await self._request(
            "POST",
            "/api/v1/artworks",
            json={
                "agent_id": agent_id,
                "title": title,
                "description": description,
                "creative_concept": creative_concept,
                "medium": medium,
                "skills_used": skills_used,
            },
        )

    async def list_for_sale(self, artwork_id: str, price: float) -> dict:
        return await self._request(
            "POST",
            f"/api/v1/artworks/{artwork_id}/list",
            json={"price": price},
        )

    async def buy_artwork(self, artwork_id: str) -> dict:
        return await self._request(
            "POST", f"/api/v1/artworks/{artwork_id}/buy"
        )

    async def get_my_status(self) -> dict:
        me = await self._request("GET", "/api/v1/auth/me")
        agents = await self._request("GET", "/api/v1/agents")
        return {"player": me, "agents": agents}

    async def learn_skill(self, agent_id: str, skill_id: str) -> dict:
        return await self._request(
            "POST",
            f"/api/v1/agents/{agent_id}/skills",
            json={"skill_id": skill_id},
        )

    async def get_available_skills(self) -> dict:
        return await self._request("GET", "/api/v1/skills")

    async def get_leaderboard(self) -> dict:
        return await self._request("GET", "/api/v1/leaderboard")
