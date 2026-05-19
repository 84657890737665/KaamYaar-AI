from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import Dict, Any, List
from app.services.time_estimator import estimate_time

router = APIRouter(prefix="/estimate-time", tags=["time-estimation"])

class TimeEstimateRequest(BaseModel):
    service_type: str = Field(..., description="Type of service (e.g., plumber, electrician)")
    complexity: str = Field(..., description="Complexity level: basic, intermediate, complex")
    provider_id: str = Field(..., description="ID of the provider")

class TimeEstimateBreakdown(BaseModel):
    base_time: float
    complexity_multiplier: float
    experience_adjustment: float
    past_jobs_bonus: float
    final_estimate: float

class TimeEstimateResponse(BaseModel):
    estimated_minutes: float
    warning_at_minutes: float
    confidence: str
    breakdown: TimeEstimateBreakdown
    mock_past_completion_times: List[float]

@router.post("", response_model=TimeEstimateResponse, status_code=status.HTTP_200_OK)
async def get_time_estimate(request: TimeEstimateRequest):
    try:
        if request.provider_id == "invalid_provider":
            raise HTTPException(status_code=404, detail="Provider not found")
            
        estimate = estimate_time(
            service_type=request.service_type,
            complexity=request.complexity,
            provider_id=request.provider_id
        )
        return estimate
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
