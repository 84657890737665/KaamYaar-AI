import logging
import json
from typing import Any, Dict, List

from google import genai
from google.genai import types

from agents.base import BaseAgent
from agents.matching_ranker.schemas import RankedProvider, MatchingRankerOutput
from agents.provider_discovery.schemas import ProviderCandidate
from core.llm_client import get_gemini_client

logger = logging.getLogger(__name__)

class MatchingRankerAgent(BaseAgent):
    """
    Agent 3: Matching & Ranker Agent.
    Takes candidate providers and ranks them using a weighted multi-factor scoring algorithm.
    Supports a dynamic 'women_safety_mode' when requested by female users.
    Returns the top 3 matches with detailed reasoning.
    """
    name = "matching_ranker"

    def __init__(self):
        self._client: genai.Client = get_gemini_client()
        
        self.weights = {
            "distance_score": 0.15,
            "availability_score": 0.15,
            "rating_score": 0.20,
            "on_time_score": 0.15,
            "cancellation_score": 0.10,
            "skill_match_score": 0.10,
            "price_score": 0.08,
            "experience_score": 0.04,
            "review_volume_score": 0.02,
            "urgency_match_score": 0.01
        }

    def _calculate_scores(self, candidate: ProviderCandidate, max_distance: float, max_price: float, urgency: str, weights: Dict[str, float], women_safety_mode: bool = False) -> Dict[str, float]:
        # 1. distance_score
        dist_val = max_distance if max_distance > 0 else 50.0
        dist_score = 1.0 - (candidate.distance_km / dist_val)
        dist_score = max(0.0, min(1.0, dist_score))
        
        # 2. availability_score
        avail_score = 1.0 if candidate.is_available else 0.0
        
        # 3. rating_score
        rating_score = candidate.rating / 5.0
        
        # 4. on_time_score
        on_time_score = candidate.on_time_score
        
        # 5. cancellation_score
        cancellation_score = 1.0 - candidate.cancellation_rate
        
        # 6. skill_match_score
        if candidate.skill_level == "expert":
            skill_score = 1.0
        elif candidate.skill_level == "intermediate":
            skill_score = 0.7
        else:
            skill_score = 0.4
            
        # 7. price_score
        p_val = max_price if max_price > 0 else candidate.base_rate_pkr
        price_score = 1.0 - (candidate.base_rate_pkr / p_val) if p_val > 0 else 1.0
        price_score = max(0.0, min(1.0, price_score))
        
        # 8. experience_score
        exp_score = min(candidate.years_experience, 10) / 10.0
        
        # 9. review_volume_score
        review_score = min(candidate.review_count, 50) / 50.0
        
        # 10. urgency_match_score
        urgency = urgency or ""
        urgency_score = 1.0 if urgency.lower() in ['high', 'emergency'] and candidate.skill_level == "expert" else 0.0
        
        # 11. safety_verified_score
        safety_score = 1.0 if getattr(candidate, "is_cnic_verified", False) else 0.0

        scores = {
            "distance_score": dist_score * weights["distance_score"],
            "availability_score": avail_score * weights["availability_score"],
            "rating_score": rating_score * weights["rating_score"],
            "on_time_score": on_time_score * weights["on_time_score"],
            "cancellation_score": cancellation_score * weights["cancellation_score"],
            "skill_match_score": skill_score * weights["skill_match_score"],
            "price_score": price_score * weights["price_score"],
            "experience_score": exp_score * weights["experience_score"],
            "review_volume_score": review_score * weights["review_volume_score"],
            "urgency_match_score": urgency_score * weights["urgency_match_score"]
        }
        if women_safety_mode:
            scores["safety_verified_score"] = safety_score * weights["safety_verified_score"]
            
        logger.debug(
            "[%s] Scores for %s: dist=%.2f avail=%.2f rating=%.2f ontime=%.2f cancel=%.2f skill=%.2f price=%.2f",
            self.name, candidate.name, scores["distance_score"], scores["availability_score"],
            scores["rating_score"], scores["on_time_score"], scores["cancellation_score"],
            scores["skill_match_score"], scores["price_score"]
        )
        return scores

    def _generate_individual_reasoning(self, scores_breakdown: Dict[str, float], rank: int, provider: ProviderCandidate, weights: Dict[str, float], women_safety_mode: bool = False) -> str:
        """Programmatic simple English reasoning for individual provider."""
        # Calculate percentage of max for each score
        pct = {k: (v / weights[k] if weights[k] > 0 else 0) for k, v in scores_breakdown.items()}
        
        # Get top 2 reasons (excluding availability & safety as safety is appended separately)
        valid_reasons = {k: v for k, v in pct.items() if k not in ["availability_score", "safety_verified_score"]}
        top_reasons = sorted(valid_reasons.keys(), key=lambda k: valid_reasons[k], reverse=True)[:2]
        
        reason_map = {
            "distance_score": f"close proximity ({provider.distance_km}km)",
            "rating_score": f"high rating of {provider.rating}/5.0",
            "on_time_score": f"excellent on-time score ({int(provider.on_time_score*100)}%)",
            "cancellation_score": f"low cancellation rate ({int(provider.cancellation_rate*100)}%)",
            "skill_match_score": f"{provider.skill_level} skill level",
            "price_score": f"competitive pricing (Rs. {provider.base_rate_pkr})",
            "experience_score": f"solid {provider.years_experience} years of experience",
            "review_volume_score": f"significant number of reviews ({provider.review_count})"
        }
        
        r1 = reason_map.get(top_reasons[0], "overall strong performance")
        r2 = reason_map.get(top_reasons[1], "reliability")
        
        reason_text = f"{provider.name} is ranked #{rank} primarily due to their {r1} and {r2}."
        if women_safety_mode:
            reason_text += " Provider selected with CNIC verification for enhanced safety."
        return reason_text

    def _generate_reasoning_summary(self, primary_language: str, service_type: str, top_candidates: List[dict], women_safety_mode: bool = False) -> str:
        """Uses Gemini to generate a comparison summary in the user's detected language."""
        if not top_candidates:
            return "No providers available."
            
        prompt = f"""
        You are the matching and ranking engine for KaamYaar AI, a Pakistani service platform.
        You need to explain why the top recommended provider was chosen over the others in the top 3.
        
        Context:
        - Primary Language requested by user: {primary_language}
        - Service requested: {service_type}
        {"- Women Safety Mode: Active (all candidates are CNIC-verified for safety)" if women_safety_mode else ""}
        
        Top 3 Ranked Providers with their scores:
        {json.dumps(top_candidates, indent=2)}
        
        Write a concise, 1-2 sentence explanation in {primary_language} explaining why the #1 ranked provider is the best match. 
        Compare them briefly to the runner-up based on their score breakdown (e.g., better on-time rate, closer distance, or expert skill level).
        Return ONLY the raw explanation string, no markdown blocks.
        """
        
        FALLBACK_MODELS = [
            "gemini-2.0-flash",
            "gemini-2.0-flash-lite",
            "gemini-2.5-flash",
            "gemini-1.5-flash",
            "gemini-1.5-flash-8b",
        ]
        
        response = None
        last_exception = None
        
        for model_id in FALLBACK_MODELS:
            logger.info("[%s] Generating reasoning summary in %s with model %s...", self.name, primary_language, model_id)
            try:
                response = self._client.models.generate_content(
                    model=model_id,
                    contents=prompt,
                    config=types.GenerateContentConfig(temperature=0.3)
                )
                logger.info("[%s] Success generating reasoning summary with model: %s", self.name, model_id)
                break
            except Exception as e:
                logger.warning("[%s] Model %s failed for summary: %s. Trying next...", self.name, model_id, e)
                last_exception = e
                continue
                
        if response is not None:
            return response.text.strip()
        else:
            logger.error("[%s] All fallback models failed to generate summary: %s", self.name, last_exception)
            return "Could not generate reasoning summary due to an error."

    def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """
        Execute the ranking agent.
        
        Args:
            input_data: Must contain:
                - "candidates": List of ProviderCandidate dicts from Agent 2.
                - "parsed_request": ParsedServiceRequest dict from Agent 1.
                - "user_gender": str (optional, triggers 'women_safety_mode' if equal to 'female')
        """
        logger.info("[%s] Starting ranking process...", self.name)
        
        if not input_data.get("candidates"):
            return {
                "ranked_providers": [],
                "top_recommendation": None,
                "reasoning_summary": "No providers available in this area.",
                "ranking_method": "weighted_multi_factor",
                "fallback_message": "No candidates found — try expanding search radius."
            }
            
        raw_candidates = input_data.get("candidates", [])
        parsed_request = input_data.get("parsed_request", {})
            
        # Convert raw dicts to Pydantic models for validation
        candidates = [ProviderCandidate(**c) if isinstance(c, dict) else c for c in raw_candidates]
        
        urgency = parsed_request.get("urgency", "medium")
        primary_language = parsed_request.get("primary_language", "English")
        service_type = parsed_request.get("service_type", "service")
        
        # Check women safety mode based on user_gender
        user_gender = input_data.get("user_gender")
        if not user_gender and isinstance(parsed_request, dict):
            user_gender = parsed_request.get("user_gender")
            
        women_safety_mode = (user_gender == 'female')
        
        if women_safety_mode:
            # Filter candidates: only is_cnic_verified == True
            candidates = [c for c in candidates if getattr(c, "is_cnic_verified", False) is True]
            
        if not candidates:
            return {
                "ranked_providers": [],
                "top_recommendation": None,
                "reasoning_summary": "No verified providers available for safety mode in this area.",
                "ranking_method": "weighted_multi_factor",
                "fallback_message": "No candidates found — try expanding search radius."
            }

        # Calculate dynamic weights
        if women_safety_mode:
            weights = {k: v * 0.85 for k, v in self.weights.items()}
            weights["safety_verified_score"] = 0.15
        else:
            weights = self.weights.copy()
            
        max_dist = max([c.distance_km for c in candidates] + [1.0])
        max_price = max([c.base_rate_pkr for c in candidates] + [1.0])
        
        scored_candidates = []
        for c in candidates:
            breakdown = self._calculate_scores(c, max_distance=max_dist, max_price=max_price, urgency=urgency, weights=weights, women_safety_mode=women_safety_mode)
            total_score = sum(breakdown.values())
            scored_candidates.append((total_score, breakdown, c))
            
        # Sort by total_score descending
        scored_candidates.sort(key=lambda x: x[0], reverse=True)
        
        # Take top 3
        top_3 = scored_candidates[:3]
        
        ranked_providers = []
        for i, (total, breakdown, candidate) in enumerate(top_3):
            rank = i + 1
            reasoning = self._generate_individual_reasoning(breakdown, rank, candidate, weights, women_safety_mode)
            
            # Determine risk flag based on high cancellation rate (>30%) or high recent disputes (>=3)
            risk_flag = candidate.cancellation_rate > 0.30 or getattr(candidate, "recent_disputes", 0) >= 3
            
            rp = RankedProvider(
                rank=rank,
                provider=candidate,
                total_score=round(total, 3),
                score_breakdown={k: round(v, 3) for k, v in breakdown.items()},
                reasoning=reasoning,
                risk_flag=risk_flag
            )
            ranked_providers.append(rp)
            
        top_rec = ranked_providers[0].provider if ranked_providers else None
        
        # Format top 3 for Gemini summary
        summary_input = [
            {
                "rank": rp.rank,
                "name": rp.provider.name,
                "total_score": rp.total_score,
                "distance_km": rp.provider.distance_km,
                "rating": rp.provider.rating,
                "on_time_score": rp.provider.on_time_score,
                "skill_level": rp.provider.skill_level,
                "base_rate_pkr": rp.provider.base_rate_pkr,
                "is_cnic_verified": getattr(rp.provider, "is_cnic_verified", False)
            }
            for rp in ranked_providers
        ]
        
        reasoning_summary = self._generate_reasoning_summary(primary_language, service_type, summary_input, women_safety_mode)
        
        output = MatchingRankerOutput(
            ranked_providers=ranked_providers,
            top_recommendation=top_rec,
            reasoning_summary=reasoning_summary
        )
        
        logger.info("[%s] Ranking complete. Top recommendation: %s (Score: %.2f)", 
                    self.name, top_rec.name if top_rec else "None", ranked_providers[0].total_score if ranked_providers else 0.0)
                    
        return output.model_dump()
