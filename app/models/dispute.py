from enum import Enum
from typing import Optional, ClassVar, List, Dict, Any
from pydantic import Field
from .base import BaseFirestoreModel

class DisputeStatus(str, Enum):
    OPEN = "OPEN"
    IN_REVIEW = "IN_REVIEW"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"

class DisputePriority(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class Dispute(BaseFirestoreModel):
    COLLECTION_NAME: ClassVar[str] = "disputes"
    
    booking_id: str = Field(..., description="ID of the booking this dispute is about")
    user_id: Optional[str] = Field(default="", description="ID of the user who filed the dispute")
    reason: str = Field(..., description="Reason for opening the dispute")
    evidence_urls: List[str] = Field(default_factory=list, description="URLs to evidence files (photos, etc.)")
    status: DisputeStatus = Field(default=DisputeStatus.OPEN, description="Current status of the dispute")
    priority: DisputePriority = Field(default=DisputePriority.LOW, description="Priority level of the dispute")
    resolution: Optional[str] = Field(default=None, description="Resolution details once resolved")
    refund_amount: float = Field(default=0.0, description="Refund amount if applicable")
    reasoning_audit_trail: List[Dict[str, Any]] = Field(default_factory=list, description="Audit trail of AI reasoning")
