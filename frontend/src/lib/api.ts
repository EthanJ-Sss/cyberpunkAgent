const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function fetchMarketOverview() {
  const res = await fetch(`${API_BASE}/api/v1/market/overview`);
  return res.json();
}

export async function fetchMarketListings(params?: {
  medium?: string;
  min_price?: number;
  max_price?: number;
  sort_by?: string;
}) {
  const searchParams = new URLSearchParams();
  if (params?.medium) searchParams.set("medium", params.medium);
  if (params?.min_price) searchParams.set("min_price", String(params.min_price));
  if (params?.max_price) searchParams.set("max_price", String(params.max_price));
  if (params?.sort_by) searchParams.set("sort_by", params.sort_by);

  const res = await fetch(`${API_BASE}/api/v1/market/listings?${searchParams}`);
  return res.json();
}

export async function fetchLeaderboard(sortBy = "reputation") {
  const res = await fetch(`${API_BASE}/api/v1/leaderboard?sort_by=${sortBy}`);
  return res.json();
}

export async function fetchSkills() {
  const res = await fetch(`${API_BASE}/api/v1/skills`);
  return res.json();
}

export async function fetchArtwork(id: string) {
  const res = await fetch(`${API_BASE}/api/v1/artworks/${id}`);
  return res.json();
}

// Authenticated requests
class AuthenticatedClient {
  private apiKey: string;

  constructor(apiKey: string) {
    this.apiKey = apiKey;
  }

  private async request(method: string, path: string, body?: unknown) {
    const res = await fetch(`${API_BASE}${path}`, {
      method,
      headers: {
        "Content-Type": "application/json",
        "X-API-Key": this.apiKey,
      },
      body: body ? JSON.stringify(body) : undefined,
    });
    if (!res.ok) {
      const error = await res.json().catch(() => ({ detail: "Request failed" }));
      throw new Error(
        (error as { detail?: string }).detail || "Request failed"
      );
    }
    return res.json();
  }

  async register(username: string) {
    const res = await fetch(`${API_BASE}/api/v1/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username }),
    });
    return res.json();
  }

  async getMe() {
    return this.request("GET", "/api/v1/auth/me");
  }
  async getAgents() {
    return this.request("GET", "/api/v1/agents");
  }
  async createAgent(name: string, modelTier = 1) {
    return this.request("POST", "/api/v1/agents", {
      name,
      model_tier: modelTier,
    });
  }
  async buySkill(agentId: string, skillId: string) {
    return this.request("POST", `/api/v1/agents/${agentId}/skills`, {
      skill_id: skillId,
    });
  }
  async createArtwork(data: {
    agent_id: string;
    title: string;
    description: string;
    creative_concept: string;
    medium: string;
    skills_used: string[];
  }) {
    return this.request("POST", "/api/v1/artworks", data);
  }
  async listForSale(artworkId: string, price: number) {
    return this.request("POST", `/api/v1/artworks/${artworkId}/list`, {
      price,
    });
  }
  async buyArtwork(artworkId: string) {
    return this.request("POST", `/api/v1/artworks/${artworkId}/buy`);
  }
}

export { AuthenticatedClient };
