from typing import List, Dict, Optional
from fastapi import APIRouter, Body, HTTPException, status
from pydantic import BaseModel, Field, conint
from app.services.quality_monitor import quality_monitor

router = APIRouter(
    prefix="/quality",
    tags=["quality"]
)

class TrackEnrouteRequest(BaseModel):
    booking_id: str = Field(..., description="ID of the booking")
    provider_location: Dict[str, float] = Field(..., description="Current location of the provider {'lat': float, 'lng': float}")

class SubmitFeedbackRequest(BaseModel):
    booking_id: str = Field(..., description="ID of the booking")
    rating: int = Field(..., ge=1, le=5, description="Rating between 1 and 5")
    review_text: str = Field(..., description="Text review of the service")
    photo_urls: Optional[List[str]] = Field(default=[], description="List of Firebase Storage photo URLs")

@router.post("/track-enroute", status_code=status.HTTP_200_OK)
async def track_enroute(request: TrackEnrouteRequest = Body(...)):
    """
    Simulates real-time location tracking for an en-route provider.
    """
    result = await quality_monitor.track_enroute(
        booking_id=request.booking_id,
        provider_location=request.provider_location
    )
    return result

@router.post("/submit-feedback", status_code=status.HTTP_200_OK)
async def submit_feedback(request: SubmitFeedbackRequest = Body(...)):
    """
    Submits feedback for a completed booking, stores it, and triggers a recalculation
    of the provider's overall rating and performance metrics.
    """
    result = await quality_monitor.collect_feedback(
        booking_id=request.booking_id,
        rating=request.rating,
        review_text=request.review_text,
        photo_urls=request.photo_urls
    )
    return result
