import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

# Constants
SAFETY_SCORE_WEIGHT = 0.15

def filter_providers_by_safety(providers: list, user_gender: str) -> list:
    """
    Filter providers based on female safety constraints.
    Female users only see verified providers (is_cnic_verified == True).
    """
    gender_lower = str(user_gender).lower()
    logger.info(f"Applying safety filter for user_gender='{user_gender}' (normalized: '{gender_lower}') on {len(providers)} providers")
    
    if gender_lower == "female":
        filtered = []
        for p in providers:
            is_verified = getattr(p, "is_cnic_verified", False) if not isinstance(p, dict) else p.get("is_cnic_verified", False)
            if is_verified is True:
                filtered.append(p)
        logger.info(f"Female safety filter: retained {len(filtered)} out of {len(providers)} providers")
        return filtered
    else:
        logger.info(f"Male/other safety filter: retained all {len(providers)} providers")
        return providers

def calculate_safety_score(provider) -> float:
    """
    Calculate safety score (0-100) based on verification attributes.
    """
    score = 0
    is_cnic_verified = getattr(provider, "is_cnic_verified", False) if not isinstance(provider, dict) else provider.get("is_cnic_verified", False)
    is_face_verified = getattr(provider, "is_face_verified", False) if not isinstance(provider, dict) else provider.get("is_face_verified", False)
    verification_status = getattr(provider, "verification_status", "pending") if not isinstance(provider, dict) else provider.get("verification_status", "pending")
    gender = getattr(provider, "gender", "male") if not isinstance(provider, dict) else provider.get("gender", "male")

    if is_cnic_verified:
        score += 40
    if is_face_verified:
        score += 30
    if verification_status == "verified":
        score += 20
    if gender == "female":
        score += 10 # bonus for female providers
        
    return min(score, 100)

def determine_confidence_level(provider) -> str:
    """
    Determine confidence level based on verification status.
    """
    is_cnic_verified = getattr(provider, "is_cnic_verified", False) if not isinstance(provider, dict) else provider.get("is_cnic_verified", False)
    is_face_verified = getattr(provider, "is_face_verified", False) if not isinstance(provider, dict) else provider.get("is_face_verified", False)
    verification_status = getattr(provider, "verification_status", "pending") if not isinstance(provider, dict) else provider.get("verification_status", "pending")
    
    if is_cnic_verified and is_face_verified and verification_status == "verified":
        return "high"
    elif is_cnic_verified or is_face_verified:
        return "medium"
    else:
        return "low"

def rank_providers_core(providers: list, user_request: dict, weights) -> list:
    """
    Core ranking logic for providers. Returns list of scored dicts ready for RankedProvider construction.
    """
    user_gender = str(user_request.get("user_gender", "male")).lower()
    is_female_user = (user_gender == "female")
    
    if is_female_user:
        total_weight = (weights.distance + weights.rating + weights.on_time + 
                        weights.safety + weights.price + weights.cancellation + weights.skills_match)
    else:
        total_weight = (weights.distance + weights.rating + weights.on_time + 
                        weights.price + weights.cancellation + weights.skills_match)
                        
    if total_weight == 0:
        total_weight = 1.0

    if not providers:
        return []

    # Calculate ranges for min-max normalization
    min_dist = min(getattr(p, "distance_value", 0) if not isinstance(p, dict) else p.get("distance_value", 0) for p in providers)
    max_dist = max(getattr(p, "distance_value", 0) if not isinstance(p, dict) else p.get("distance_value", 0) for p in providers)
    dist_range = max_dist - min_dist

    min_price = min(getattr(p, "base_rate", 0) if not isinstance(p, dict) else p.get("base_rate", 0) for p in providers)
    max_price = max(getattr(p, "base_rate", 0) if not isinstance(p, dict) else p.get("base_rate", 0) for p in providers)
    price_range = max_price - min_price

    requested_service = str(user_request.get("service", "")).lower()
    ranked_results = []

    for provider in providers:
        # Extract attributes
        distance_value = getattr(provider, "distance_value", 0) if not isinstance(provider, dict) else provider.get("distance_value", 0)
        rating = getattr(provider, "rating", 0.0) if not isinstance(provider, dict) else provider.get("rating", 0.0)
        on_time_score = getattr(provider, "on_time_score", 100.0) if not isinstance(provider, dict) else provider.get("on_time_score", 100.0)
        base_rate = getattr(provider, "base_rate", 0.0) if not isinstance(provider, dict) else provider.get("base_rate", 0.0)
        cancellation_rate = getattr(provider, "cancellation_rate", 0.0) if not isinstance(provider, dict) else provider.get("cancellation_rate", 0.0)
        skills = getattr(provider, "skills", []) if not isinstance(provider, dict) else provider.get("skills", [])

        # 1. Distance (lower is better)
        if dist_range == 0:
            score_dist = 100.0
        else:
            score_dist = 100.0 * (max_dist - distance_value) / dist_range

        # 2. Rating (higher is better, 0-5 scale)
        score_rating = (rating / 5.0) * 100.0

        # 3. On-time score (higher is better, 0-100 scale)
        score_on_time = float(on_time_score)

        # 4. Price (lower is better)
        if price_range == 0:
            score_price = 100.0
        else:
            score_price = 100.0 * (max_price - base_rate) / price_range

        # 5. Cancellation (lower cancellation is better)
        score_cancellation = 100.0 - float(cancellation_rate)

        # 6. Skills match (higher is better)
        score_skills = 50.0
        if any(requested_service in skill.lower() or skill.lower() in requested_service for skill in skills):
            score_skills = 100.0
            
        # 7. Safety score
        score_safety = calculate_safety_score(provider)
        
        # Calculate final weighted score
        if is_female_user:
            total_score = (
                score_dist * weights.distance +
                score_rating * weights.rating +
                score_on_time * weights.on_time +
                score_safety * weights.safety +
                score_price * weights.price +
                score_cancellation * weights.cancellation +
                score_skills * weights.skills_match
            ) / total_weight
        else:
            total_score = (
                score_dist * weights.distance +
                score_rating * weights.rating +
                score_on_time * weights.on_time +
                score_price * weights.price +
                score_cancellation * weights.cancellation +
                score_skills * weights.skills_match
            ) / total_weight

        # Normalize total_score to 0-1 range
        normalized_total = total_score / 100.0

        # Generate reasoning text
        score_contributors = {
            "proximity": score_dist * weights.distance,
            "high ratings": score_rating * weights.rating,
            "punctuality": score_on_time * weights.on_time,
            "competitive pricing": score_price * weights.price,
            "reliability (low cancellation)": score_cancellation * weights.cancellation,
            "exact skills match": score_skills * weights.skills_match
        }
        if is_female_user:
            score_contributors["safety profile"] = score_safety * weights.safety
            
        top_2 = sorted(score_contributors.items(), key=lambda x: x[1], reverse=True)[:2]
        strong_points = f"{top_2[0][0]} and {top_2[1][0]}"

        if normalized_total >= 0.80:
            reasoning = f"Excellent match! Highly ranked due to {strong_points}."
        elif normalized_total >= 0.60:
            reasoning = f"Good match. Strong points include {strong_points}."
        else:
            reasoning = f"Fair match. Selected mainly for {top_2[0][0]}."

        ranked_results.append({
            "provider": provider,
            "ranking_score": round(normalized_total, 2),
            "factors": {
                "distance_score": round(score_dist, 2),
                "rating_score": round(score_rating, 2),
                "on_time_score": round(score_on_time, 2),
                "safety_score": round(score_safety, 2),
                "price_score": round(score_price, 2),
                "cancellation_score": round(score_cancellation, 2),
                "skills_match_score": round(score_skills, 2)
            },
            "confidence_level": determine_confidence_level(provider),
            "reasoning_text": reasoning
        })

    # Sort by ranking score descending
    ranked_results.sort(key=lambda x: x["ranking_score"], reverse=True)
    return ranked_results
