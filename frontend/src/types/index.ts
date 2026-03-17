export interface Artwork {
  id: string;
  creator_agent_id: string;
  title: string;
  description: string;
  creative_concept: string;
  medium: string;
  style_tags: string[];
  skills_used: string[];
  model_tier_at_creation: number;
  compute_cost: number;
  quality_score: number;
  rarity_score: number;
  status: string;
  listed_price: number | null;
  sold_price: number | null;
  buyer_id: string | null;
  created_at: string;
}

export interface MarketOverview {
  total_listings: number;
  total_agents: number;
  total_trade_volume: number;
}

export interface Agent {
  id: string;
  name: string;
  model_tier: number;
  skills: string[];
  skill_proficiency: Record<string, number>;
  reputation_score: number;
  reputation_level: number;
  style_tags: string[];
  total_artworks: number;
  total_sales: number;
  compute_consumed: number;
  status: string;
}

export interface Skill {
  id: string;
  tier: number;
  name: string;
  description: string;
  prerequisites: string[];
  cost: number;
  category: string;
}

export interface Player {
  id: string;
  username: string;
  openclaw_endpoint: string | null;
  balance: number;
}
