from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import List, Dict, Any
from app.models.provider import ProviderWithDistance
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/rank-providers",
    tags=["rank-providers"],
)

class RankingWeights(BaseModel):
    distance: float = Field(0.3, description="Weight for distance proximity")
    rating: float = Field(0.2, description="Weight for user ratings")
    on_time: float = Field(0.2, description="Weight for on-time arrival history")
    price: float = Field(0.15, description="Weight for base service rate")
    cancellation: float = Field(0.1, description="Weight for non-cancellation rate")
    skills_match: float = Field(0.05, description="Weight for exact skills match")

class RankProvidersInput(BaseModel):
    providers: List[ProviderWithDistance] = Field(..., description="List of providers from find-providers")
    user_request: Dict[str, Any] = Field(..., description="Parsed user request details")
    weights: RankingWeights = Field(default_factory=RankingWeights)

class RankedProvider(ProviderWithDistance):
    distance_score: float = Field(..., description="Normalized distance score (0-100)")
    rating_score: float = Field(..., description="Normalized rating score (0-100)")
    on_time_score_normalized: float = Field(..., description="Normalized on-time score (0-100)")
    price_score: float = Field(..., description="Normalized price score (0-100)")
    cancellation_score: float = Field(..., description="Normalized cancellation score (0-100)")
    skills_match_score: float = Field(..., description="Normalized skills match score (0-100)")
    total_score: float = Field(..., description="Final weighted total score (0-100)")
    reasoning_text: str = Field(..., description="Textual reasoning explaining the rank")

@router.post("", response_model=List[RankedProvider])
async def rank_providers(request: RankProvidersInput):
    providers = request.providers
    if not providers:
        return []

    weights = request.weights
    total_weight = (weights.distance + weights.rating + weights.on_time + 
                    weights.price + weights.cancellation + weights.skills_match)
    if total_weight == 0:
        total_weight = 1.0

    # Calculate ranges for min-max normalization
    min_dist = min(p.distance_value for p in providers)
    max_dist = max(p.distance_value for p in providers)
    dist_range = max_dist - min_dist

    min_price = min(p.base_rate for p in providers)
    max_price = max(p.base_rate for p in providers)
    price_range = max_price - min_price

    requested_service = str(request.user_request.get("service", "")).lower()

    ranked_results = []

    for provider in providers:
        # 1. Distance (lower is better)
        if dist_range == 0:
            score_dist = 100.0
        else:
            score_dist = 100.0 * (max_dist - provider.distance_value) / dist_range

        # 2. Rating (higher is better, 0-5 scale)
        score_rating = (provider.rating / 5.0) * 100.0

        # 3. On-time score (higher is better, 0-100 scale)
        score_on_time = float(provider.on_time_score)

        # 4. Price (lower is better)
        if price_range == 0:
            score_price = 100.0
        else:
            score_price = 100.0 * (max_price - provider.base_rate) / price_range

        # 5. Cancellation (lower cancellation is better)
        score_cancellation = 100.0 - float(provider.cancellation_rate)

        # 6. Skills match (higher is better)
        score_skills = 50.0 # Baseline for matching the generic service category
        if any(requested_service in skill.lower() or skill.lower() in requested_service for skill in provider.skills):
            score_skills = 100.0

        # Calculate final weighted score
        total_score = (
            score_dist * weights.distance +
            score_rating * weights.rating +
            score_on_time * weights.on_time +
            score_price * weights.price +
            score_cancellation * weights.cancellation +
            score_skills * weights.skills_match
        ) / total_weight

        # Generate reasoning text
        score_contributors = {
            "proximity": score_dist * weights.distance,
            "high ratings": score_rating * weights.rating,
            "punctuality": score_on_time * weights.on_time,
            "competitive pricing": score_price * weights.price,
            "reliability (low cancellation)": score_cancellation * weights.cancellation,
            "exact skills match": score_skills * weights.skills_match
        }
        
        top_2 = sorted(score_contributors.items(), key=lambda x: x[1], reverse=True)[:2]
        strong_points = f"{top_2[0][0]} and {top_2[1][0]}"

        if total_score >= 80:
            reasoning = f"Excellent match! Highly ranked due to {strong_points}."
        elif total_score >= 60:
            reasoning = f"Good match. Strong points include {strong_points}."
        else:
            reasoning = f"Fair match. Selected mainly for {top_2[0][0]}."

        ranked_provider = RankedProvider(
            **provider.model_dump(),
            distance_score=round(score_dist, 2),
            rating_score=round(score_rating, 2),
            on_time_score_normalized=round(score_on_time, 2),
            price_score=round(score_price, 2),
            cancellation_score=round(score_cancellation, 2),
            skills_match_score=round(score_skills, 2),
            total_score=round(total_score, 2),
            reasoning_text=reasoning
        )
        ranked_results.append(ranked_provider)

    # Sort by total score descending
    ranked_results.sort(key=lambda x: x.total_score, reverse=True)

    return ranked_results
