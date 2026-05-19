from enum import Enum
from datetime import datetime, timezone
from typing import Optional, ClassVar, Dict, Any
from pydantic import BaseModel, Field
from .base import BaseFirestoreModel

class AlertType(str, Enum):
    SAFETY_CONCERN = "safety_concern"
    MEDICAL = "medical"
    HARASSMENT = "harassment"

class AlertStatus(str, Enum):
    DISPATCHED = "dispatched"
    RESOLVED = "resolved"
    ESCALATED = "escalated"

class Location(BaseModel):
    lat: float = Field(..., description="Latitude")
    lng: float = Field(..., description="Longitude")

class ProviderInfo(BaseModel):
    provider_id: str = Field(..., description="ID of the provider")
    provider_name: str = Field(..., description="Name of the provider")
    provider_location: Optional[Location] = Field(default=None, description="Location of the provider at the time of alert")

class BookingInfo(BaseModel):
    service_type: str = Field(..., description="Type of service")
    address: str = Field(..., description="Address of the booking")

class EmergencyAlert(BaseFirestoreModel):
    COLLECTION_NAME: ClassVar[str] = "emergency_alerts"
    
    booking_id: str = Field(..., description="ID of the associated booking")
    user_id: str = Field(..., description="ID of the user who raised the alert")
    alert_type: AlertType = Field(..., description="Type of emergency alert")
    message: Optional[str] = Field(default=None, description="Custom message provided by the user")
    location: Location = Field(..., description="Location where the alert was triggered")
    status: AlertStatus = Field(default=AlertStatus.DISPATCHED, description="Current status of the alert")
    trusted_contacts_notified: int = Field(default=0, description="Number of trusted contacts notified")
    provider_info: ProviderInfo = Field(..., description="Information about the provider")
    booking_info: BookingInfo = Field(..., description="Information about the booking")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Timestamp when the alert was created")
    resolved_at: Optional[datetime] = Field(default=None, description="Timestamp when the alert was resolved")
    resolution_notes: Optional[str] = Field(default=None, description="Notes added when resolving the alert")
