"""
agents/quality_monitor/schemas.py

Pydantic schemas to validate data inputs and outputs for the Service Quality Monitor Agent (Agent 6 of 7).
"""

from typing import Any
from pydantic import BaseModel, Field


class FeedbackChecklist(BaseModel):
    """Binary service checklist items to grade provider performance."""

    work_quality: bool = Field(..., description="Was work quality satisfactory?")
    on_time: bool = Field(..., description="Did the provider arrive on time?")
    professional_behavior: bool = Field(..., description="Was the provider polite and professional?")
    correct_pricing: bool = Field(..., description="Was pricing consistent with the quote?")
    would_recommend: bool = Field(..., description="Would the user recommend this provider?")


class CustomerFeedback(BaseModel):
    """Customer rating, review text, and structured checklist response."""

    customer_rating: float = Field(..., ge=1.0, le=5.0, description="Customer rating out of 5.0")
    review_text: str = Field(..., description="Written customer feedback review")
    checklist: FeedbackChecklist = Field(..., description="Binary service checklist")
    evidence_placeholder: str = Field("photo/video upload supported", description="Upload reference placeholder")


class QualityMonitorOutput(BaseModel):
    """Standardized output payload for the Quality Monitor Agent."""

    booking_id: str = Field(..., description="Active booking ID being monitored")
    final_status: str = Field("completed", description="Final lifecycle status of booking")
    stage_log: list[dict[str, Any]] = Field(..., description="Logs detailing stage transitions and timestamps")
    customer_feedback: dict[str, Any] = Field(..., description="Collected feedback record")
    old_provider_rating: float = Field(..., description="Provider rating before this feedback")
    new_provider_rating: float = Field(..., description="Provider rating recalculated after this feedback")
    rating_updated_in_firestore: bool = Field(..., description="True if new rating saved in Firestore")
    future_matching_note: str = Field(..., description="Analysis explaining the feedback's impact on future matching score")
