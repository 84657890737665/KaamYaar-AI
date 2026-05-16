from enum import Enum
from datetime import datetime, timezone
from typing import Optional, ClassVar
from pydantic import BaseModel, Field
from .base import BaseFirestoreModel

class BookingStatus(str, Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

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
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Timestamp of the last update")
