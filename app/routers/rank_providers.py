from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from app.models.provider import ProviderWithDistance
import logging

from app.services.ranker_engine import (
    filter_providers_by_safety,
    calculate_safety_score,
    determine_confidence_level,
    rank_providers_core
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/rank-providers",
    tags=["rank-providers"],
)

class RankingWeights(BaseModel):
    distance: float = Field(0.25, description="Weight for distance proximity")
    rating: float = Field(0.20, description="Weight for user ratings")
    on_time: float = Field(0.15, description="Weight for on-time arrival history")
    safety: float = Field(0.15, description="Weight for safety score (female users only)")
    price: float = Field(0.10, description="Weight for base service rate")
    cancellation: float = Field(0.05, description="Weight for non-cancellation rate")
    skills_match: float = Field(0.05, description="Weight for exact skills match")

class RankProvidersInput(BaseModel):
    providers: List[ProviderWithDistance] = Field(..., description="List of providers from find-providers")
    user_request: Dict[str, Any] = Field(..., description="Parsed user request details")
    weights: RankingWeights = Field(default_factory=RankingWeights)

class RankedProviderFactors(BaseModel):
    distance_score: float = Field(..., description="Normalized distance score (0-100)")
    rating_score: float = Field(..., description="Normalized rating score (0-100)")
    on_time_score: float = Field(..., description="Normalized on-time score (0-100)")
    safety_score: Optional[float] = Field(None, description="Normalized safety score (0-100)")
    price_score: float = Field(..., description="Normalized price score (0-100)")
    cancellation_score: float = Field(..., description="Normalized cancellation score (0-100)")
    skills_match_score: float = Field(..., description="Normalized skills match score (0-100)")

class RankedProvider(ProviderWithDistance):
    ranking_score: float = Field(..., description="Final weighted total score normalized (0-1)")
    factors: RankedProviderFactors = Field(..., description="Individual factor scores")
    is_cnic_verified: bool = Field(default=False, description="Whether CNIC is verified")
    is_face_verified: bool = Field(default=False, description="Whether Face is verified")
    safety_badge: str = Field(default="unverified", description="Verified or Unverified")
    confidence_level: str = Field(default="low", description="Confidence level based on verification status")
    reasoning_text: str = Field(..., description="Textual reasoning explaining the rank")

class FiltersApplied(BaseModel):
    verified_only: bool = False
    safety_score_min: Optional[int] = None
    user_gender: str = "male"

class RankProvidersResponse(BaseModel):
    ranked_providers: List[RankedProvider]
    filters_applied: FiltersApplied
    safety_message: Optional[str] = None
    warning: Optional[str] = None
    safety_override_available: Optional[bool] = None

@router.post("", response_model=RankProvidersResponse)
async def rank_providers(request: RankProvidersInput):
    original_providers = request.providers
    user_gender = str(request.user_request.get("user_gender", "male")).lower()
    
    # Apply Safety Filter
    providers = filter_providers_by_safety(original_providers, user_gender)
    
    filters_applied = FiltersApplied(
        verified_only=(user_gender == "female"),
        safety_score_min=None,
        user_gender=user_gender
    )

    if not providers and user_gender == "female" and len(original_providers) > 0:
        # Handled edge case: no verified providers
        return RankProvidersResponse(
            ranked_providers=[],
            warning="No verified providers available in your area. Please try again later or contact support.",
            safety_override_available=False,
            filters_applied=filters_applied
        )
    elif not providers:
        return RankProvidersResponse(
            ranked_providers=[],
            filters_applied=filters_applied
        )

    # Core scoring logic
    ranked_dicts = rank_providers_core(providers, request.user_request, request.weights)
    
    ranked_results = []
    for rd in ranked_dicts:
        provider = rd["provider"]
        is_verified = getattr(provider, "is_cnic_verified", False)
        is_face_verified = getattr(provider, "is_face_verified", False)
        
        ranked_provider = RankedProvider(
            **provider.model_dump(),
            ranking_score=rd["ranking_score"],
            factors=RankedProviderFactors(
                distance_score=rd["factors"]["distance_score"],
                rating_score=rd["factors"]["rating_score"],
                on_time_score=rd["factors"]["on_time_score"],
                safety_score=rd["factors"]["safety_score"],
                price_score=rd["factors"]["price_score"],
                cancellation_score=rd["factors"]["cancellation_score"],
                skills_match_score=rd["factors"]["skills_match_score"]
            ),
            safety_badge="verified" if is_verified else "unverified",
            confidence_level=rd["confidence_level"],
            reasoning_text=rd["reasoning_text"]
        )
        ranked_results.append(ranked_provider)

    response = RankProvidersResponse(
        ranked_providers=ranked_results,
        filters_applied=filters_applied
    )
    
    if user_gender == "female":
        response.safety_message = "Showing only verified providers for your safety"
        if len(ranked_results) > 0:
             # Find min safety score of returned providers
             min_safety = min(p.factors.safety_score for p in ranked_results if p.factors.safety_score is not None)
             response.filters_applied.safety_score_min = int(min_safety)

    return response
