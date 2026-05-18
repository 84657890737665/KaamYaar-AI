from typing import Dict, List, Optional
from pydantic import BaseModel

from agents.provider_discovery.schemas import ProviderCandidate

class RankedProvider(BaseModel):
    rank: int
    provider: ProviderCandidate
    total_score: float
    score_breakdown: Dict[str, float]
    reasoning: str
    risk_flag: bool = False

class MatchingRankerOutput(BaseModel):
    ranked_providers: List[RankedProvider]
    ranking_method: str = "weighted_multi_factor"
    top_recommendation: Optional[ProviderCandidate] = None
    reasoning_summary: str
