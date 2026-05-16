from enum import Enum
from typing import Optional, ClassVar
from pydantic import Field
from .base import BaseFirestoreModel

class DisputeStatus(str, Enum):
    OPEN = "OPEN"
    IN_REVIEW = "IN_REVIEW"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"

class Dispute(BaseFirestoreModel):
    COLLECTION_NAME: ClassVar[str] = "disputes"
    
    booking_id: str = Field(..., description="ID of the booking this dispute is about")
    reason: str = Field(..., description="Reason for opening the dispute")
    status: DisputeStatus = Field(default=DisputeStatus.OPEN, description="Current status of the dispute")
    resolution: Optional[str] = Field(default=None, description="Resolution details once resolved")
