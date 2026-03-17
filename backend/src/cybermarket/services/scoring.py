import random
import re


MODEL_WEIGHTS = {1: 20, 2: 45, 3: 75, 4: 95}
MODEL_COST_COEFF = {1: 1.0, 2: 2.5, 3: 6.0, 4: 15.0}


def calculate_quality_score(
    model_tier: int,
    skill_proficiency_avg: float,
    description: str,
    existing_artworks_count: int,
) -> float:
    model_score = MODEL_WEIGHTS.get(model_tier, 20)
    desc_richness = _evaluate_description(description)
    uniqueness = max(10, 100 - existing_artworks_count * 2)
    spark = random.uniform(0, 100)

    score = (
        model_score * 0.35
        + skill_proficiency_avg * 0.25
        + desc_richness * 0.20
        + uniqueness * 0.10
        + spark * 0.10
    )
    return round(min(100, max(0, score)), 2)


def _evaluate_description(description: str) -> float:
    length_score = min(100, len(description) / 5)
    words = set(re.findall(r"\w+", description))
    vocab_score = min(100, len(words) * 2)
    return (length_score + vocab_score) / 2


def calculate_creation_cost(
    model_tier: int, num_skills: int, base_cost: float = 10.0
) -> float:
    skill_coeff = 1.2**num_skills
    return round(base_cost * MODEL_COST_COEFF.get(model_tier, 1.0) * skill_coeff, 2)


def calculate_rarity_score(
    same_medium_count: int,
    skills_used_count: int,
    reputation_score: float,
    compute_cost: float,
) -> float:
    supply_factor = max(5, 100 - same_medium_count * 3)
    skill_rarity = min(100, skills_used_count * 25)
    rep_factor = reputation_score
    cost_factor = min(100, compute_cost * 2)

    score = (
        supply_factor * 0.35
        + skill_rarity * 0.25
        + rep_factor * 0.20
        + cost_factor * 0.20
    )
    return round(min(100, max(0, score)), 2)
