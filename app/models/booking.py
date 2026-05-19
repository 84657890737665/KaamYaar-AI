from enum import Enum
from datetime import datetime, timezone
from typing import Optional, ClassVar, Dict, Any
from pydantic import BaseModel, Field
from .base import BaseFirestoreModel

class BookingStatus(str, Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    SAFETY_CONCERN_RAISED = "safety_concern_raised"

class PriceBreakdown(BaseModel):
    base_fare: float = Field(..., ge=0.0, description="Base service charge")
    taxes: float = Field(default=0.0, ge=0.0, description="Applicable taxes")
    total: float = Field(..., ge=0.0, description="Total amount to be paid")

class Booking(BaseFirestoreModel):
    COLLECTION_NAME: ClassVar[str] = "bookings"
    
    user_id: str = Field(..., description="ID of the user who made the booking")
    provider_id: str = Field(..., description="ID of the assigned provider")
    service_type: str = Field(..., description="Type of service booked")
    status: BookingStatus = Field(default=BookingStatus.PENDING, description="Current status of the booking")
    price_breakdown: PriceBreakdown = Field(..., description="Detailed price calculation")
    service_details: Optional[Dict[str, Any]] = Field(default=None, description="Details of the service request")
    before_state: Optional[Dict[str, Any]] = Field(default=None, description="Snapshot of state before booking")
    after_state: Optional[Dict[str, Any]] = Field(default=None, description="Snapshot of state after completion")
    last_location: Optional[Dict[str, float]] = Field(default=None, description="Last recorded location of provider")
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Timestamp of the last update")
    
    # M4: Safety Timer + Warning System
    safety_timer_active: bool = Field(default=False, description="Whether safety timer is active")
    safety_alert_sent: bool = Field(default=False, description="Whether safety alert has been sent")
    safety_alert_sent_at: Optional[datetime] = Field(default=None, description="Timestamp when safety alert was sent")
    
    # M5: Emergency Alert
    emergency_alert_id: Optional[str] = Field(default=None, description="ID of the emergency alert if raised")
