from pydantic import BaseModel

class ProviderCandidate(BaseModel):
    provider_id: str
    name: str
    service_types: list[str]
    location_name: str
    distance_km: float
    rating: float
    on_time_score: float
    cancellation_rate: float
    base_rate_pkr: int
    is_available: bool
    skill_level: str
    years_experience: int
    review_count: int
    recent_disputes: int = 0

class ProviderDiscoveryOutput(BaseModel):
    candidates: list[ProviderCandidate]
    total_found: int
    search_radius_km: float
    fallback_triggered: bool
