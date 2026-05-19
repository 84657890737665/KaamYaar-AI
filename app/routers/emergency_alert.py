import logging
from typing import List, Optional
from datetime import datetime, timezone
import uuid

from fastapi import APIRouter, HTTPException, status, Path
from pydantic import BaseModel, Field, field_validator

from app.models.emergency_alert import EmergencyAlert, AlertType, AlertStatus, Location as AlertLocation, ProviderInfo, BookingInfo
from app.models.booking import Booking, BookingStatus
from app.models.provider import Provider
from app.services.firestore_service import firestore_service

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Emergency Alert"])

class EmergencyAlertRequest(BaseModel):
    booking_id: str
    user_id: str
    alert_type: str
    message: Optional[str] = None
    location: dict

    @field_validator("alert_type")
    @classmethod
    def validate_alert_type(cls, v: str) -> str:
        try:
            AlertType(v)
            return v
        except ValueError:
            raise ValueError(f"Invalid alert_type. Must be one of: {[e.value for e in AlertType]}")

    @field_validator("location")
    @classmethod
    def validate_location(cls, v: dict) -> dict:
        if "lat" not in v or "lng" not in v:
            raise ValueError("Location must contain 'lat' and 'lng'")
        lat, lng = v["lat"], v["lng"]
        if not (-90 <= lat <= 90):
            raise ValueError("Latitude must be between -90 and 90")
        if not (-180 <= lng <= 180):
            raise ValueError("Longitude must be between -180 and 180")
        return v

class ResolveAlertRequest(BaseModel):
    resolution_notes: Optional[str] = None

@router.post("/booking/emergency-alert", status_code=status.HTTP_201_CREATED)
async def create_emergency_alert(request: EmergencyAlertRequest):
    """Create an emergency alert for a booking."""
    
    # 1. Fetch booking
    booking_dict = firestore_service.get_document(Booking.COLLECTION_NAME, request.booking_id)
    if not booking_dict:
        raise HTTPException(status_code=404, detail="Booking not found")
        
    booking = Booking(**booking_dict)
    
    # 2. Validate user_id
    if booking.user_id != request.user_id:
        raise HTTPException(status_code=403, detail="User ID does not match booking")
        
    # 3. Alert type is already validated by Pydantic validator, but we need to pass it to the model
    try:
        a_type = AlertType(request.alert_type)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid alert_type")
        
    # Location coordinates validation is handled by Pydantic validator
    
    # Fetch provider info to enrich the alert
    provider_dict = firestore_service.get_document(Provider.COLLECTION_NAME, booking.provider_id)
    provider_info_dict = {
        "provider_id": booking.provider_id,
        "provider_name": "Unknown",
        "provider_location": None
    }
    
    if provider_dict:
        provider = Provider(**provider_dict)
        provider_info_dict["provider_name"] = provider.name
        provider_info_dict["provider_location"] = provider.location.model_dump()
        
    # Create Alert
    alert_id = f"alert_{uuid.uuid4().hex[:8]}"
    
    alert = EmergencyAlert(
        id=alert_id,
        booking_id=request.booking_id,
        user_id=request.user_id,
        alert_type=a_type,
        message=request.message,
        location=AlertLocation(**request.location),
        status=AlertStatus.DISPATCHED,
        trusted_contacts_notified=2, # Mock value
        provider_info=ProviderInfo(**provider_info_dict),
        booking_info=BookingInfo(
            service_type=booking.service_type,
            address=booking.service_details.get("address", "Unknown Address") if booking.service_details else "Unknown Address"
        )
    )
    
    # 4. Mock SMS and FCM
    logger.info(f"MOCK SMS: Sent emergency alert to 2 trusted contacts for user {request.user_id}")
    logger.info(f"MOCK FCM: Sent emergency alert {alert_id} to KaamYaar Support")
    
    # 5. Update Booking Status
    booking.status = BookingStatus.SAFETY_CONCERN_RAISED
    booking.emergency_alert_id = alert_id
    booking.updated_at = datetime.now(timezone.utc)
    
    firestore_service.update_document(Booking.COLLECTION_NAME, booking.id, booking.model_dump(exclude_unset=True))
    
    # 6. Save Alert
    firestore_service.create_document(EmergencyAlert.COLLECTION_NAME, alert.id, alert.model_dump(exclude_unset=True))
    
    return {
        "alert_id": alert.id,
        "status": alert.status.value,
        "actions_taken": [
            "Trusted contacts notified: 2",
            "KaamYaar support alerted",
            "Booking status updated: safety_concern_raised"
        ],
        "eta_help": "5 minutes",
        "timestamp": alert.created_at.isoformat()
    }


@router.get("/booking/{booking_id}/emergency-alerts")
async def get_booking_alerts(booking_id: str):
    """Retrieve all alerts for a given booking"""
    filters = [{"field": "booking_id", "operator": "==", "value": booking_id}]
    alerts_data = firestore_service.query_documents(EmergencyAlert.COLLECTION_NAME, filters)
    
    # Sort by created_at descending (newest first)
    alerts = [EmergencyAlert(**a) for a in alerts_data]
    alerts.sort(key=lambda x: x.created_at, reverse=True)
    
    return alerts


@router.patch("/emergency-alert/{alert_id}/resolve")
async def resolve_alert(alert_id: str, request: ResolveAlertRequest):
    """Mark alert as resolved"""
    alert_dict = firestore_service.get_document(EmergencyAlert.COLLECTION_NAME, alert_id)
    if not alert_dict:
        raise HTTPException(status_code=404, detail="Alert not found")
        
    alert = EmergencyAlert(**alert_dict)
    alert.status = AlertStatus.RESOLVED
    alert.resolved_at = datetime.now(timezone.utc)
    if request.resolution_notes:
        alert.resolution_notes = request.resolution_notes
        
    firestore_service.update_document(EmergencyAlert.COLLECTION_NAME, alert.id, alert.model_dump(exclude_unset=True))
    
    # Optionally update booking status if needed, but not specified in requirements
    
    return {
        "status": "success",
        "message": f"Alert {alert_id} resolved",
        "resolved_at": alert.resolved_at.isoformat()
    }


@router.get("/emergency-alert/{alert_id}")
async def get_alert(alert_id: str):
    """Get single alert details"""
    alert_dict = firestore_service.get_document(EmergencyAlert.COLLECTION_NAME, alert_id)
    if not alert_dict:
        raise HTTPException(status_code=404, detail="Alert not found")
        
    return EmergencyAlert(**alert_dict)
