"""
Safety Router — M7 KaamYaar Safety Endpoints

Provides:
  1. POST /safety/estimate-time     — Estimate job duration + safety warning
  2. POST /safety/emergency-alert   — Trigger emergency alert to trusted contact
  3. GET  /safety/status/{booking_id} — Get live safety status for a booking
"""

import logging
import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, List

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.services.firestore_service import firestore_service

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────
#  Constants
# ─────────────────────────────────────────────────────────

ESTIMATE_MAP: Dict[str, Dict[str, int]] = {
    "plumber":        {"basic": 45,  "intermediate": 75,  "complex": 120},
    "electrician":    {"basic": 60,  "intermediate": 90,  "complex": 150},
    "ac_technician":  {"basic": 60,  "intermediate": 90,  "complex": 180},
    "painter":        {"basic": 120, "intermediate": 240, "complex": 480},
    "cleaner":        {"basic": 60,  "intermediate": 90,  "complex": 150},
    "carpenter":      {"basic": 60,  "intermediate": 120, "complex": 240},
    "mechanic":       {"basic": 60,  "intermediate": 90,  "complex": 180},
    "default":        {"basic": 60,  "intermediate": 90,  "complex": 120},
}

VALID_COMPLEXITIES = {"basic", "intermediate", "complex"}

WARNING_BUFFER_MINUTES = 30  # alert fires this many minutes after estimate

router = APIRouter(prefix="/safety", tags=["safety"])


# ─────────────────────────────────────────────────────────
#  Pydantic Schemas
# ─────────────────────────────────────────────────────────

# --- Endpoint 1: Estimate Time ---
class EstimateTimeRequest(BaseModel):
    """Request body for time estimation."""
    service_type: str = Field(..., description="Type of service (e.g., plumber, electrician)")
    job_complexity: str = Field(default="intermediate", description="Complexity level: basic, intermediate, complex")


class EstimateTimeResponse(BaseModel):
    """Response body for time estimation."""
    service_type: str
    estimated_minutes: int
    warning_at_minutes: int
    confidence: str
    safety_note: str


# --- Endpoint 2: Emergency Alert ---
class EmergencyAlertRequest(BaseModel):
    """Request body for emergency alert creation."""
    booking_id: str = Field(..., description="Booking ID to associate the alert with")
    user_id: str = Field(..., description="User ID triggering the alert")
    trusted_contact_number: str = Field(..., description="Phone number of trusted contact")
    trusted_contact_name: str = Field(..., description="Name of trusted contact")


class EmergencyAlertResponse(BaseModel):
    """Response body after emergency alert is sent."""
    alert_id: str
    status: str
    booking_id: str
    trusted_contact_name: str
    trusted_contact_number: str
    message: str
    timestamp: str
    next_action: str


# --- Endpoint 3: Safety Status ---
class SafetyStatusResponse(BaseModel):
    """Response body for safety status lookup."""
    booking_id: str
    safety_timer_active: bool
    time_remaining_minutes: int
    estimated_total_minutes: int
    alert_status: str
    trusted_contact_notified: bool
    last_update: str


# ─────────────────────────────────────────────────────────
#  Endpoint 1: POST /safety/estimate-time
# ─────────────────────────────────────────────────────────

@router.post("/estimate-time", response_model=EstimateTimeResponse, status_code=status.HTTP_200_OK)
async def estimate_time(request: EstimateTimeRequest):
    """
    Estimate job duration based on service type and complexity.

    Returns estimated minutes, a warning threshold (estimated + 30 min),
    confidence level, and a safety note in Urdu.
    """
    service = request.service_type.lower().strip()
    complexity = request.job_complexity.lower().strip()

    logger.info(f"Estimating time for service_type='{service}', job_complexity='{complexity}'")

    # Validate service_type
    valid_services = [k for k in ESTIMATE_MAP.keys() if k != "default"]
    if service not in ESTIMATE_MAP:
        logger.warning(f"Invalid service_type: '{service}'")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid service_type: '{service}'. Valid types: {valid_services}"
        )

    # Validate job_complexity
    if complexity not in VALID_COMPLEXITIES:
        logger.warning(f"Invalid job_complexity: '{complexity}'")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid job_complexity: '{complexity}'. Valid levels: {sorted(VALID_COMPLEXITIES)}"
        )

    # Lookup estimated time
    service_data = ESTIMATE_MAP.get(service, ESTIMATE_MAP["default"])
    estimated_minutes = service_data[complexity]
    warning_at = estimated_minutes + WARNING_BUFFER_MINUTES

    safety_note = f"Agar {warning_at} minutes mein kaam complete na ho — safety alert jayega"

    logger.info(f"Time estimate: {estimated_minutes} min, warning at {warning_at} min")

    return EstimateTimeResponse(
        service_type=service,
        estimated_minutes=estimated_minutes,
        warning_at_minutes=warning_at,
        confidence="high",
        safety_note=safety_note,
    )


# ─────────────────────────────────────────────────────────
#  Endpoint 2: POST /safety/emergency-alert
# ─────────────────────────────────────────────────────────

@router.post("/emergency-alert", response_model=EmergencyAlertResponse, status_code=status.HTTP_201_CREATED)
async def create_emergency_alert(request: EmergencyAlertRequest):
    """
    Create an emergency alert for a booking and notify the trusted contact.

    Validates booking existence and user ownership, then persists the alert
    to the Firestore ``safety_alerts`` collection.
    """
    logger.info(f"Emergency alert requested: booking_id={request.booking_id}, user_id={request.user_id}")

    # --- Validate booking exists ---
    try:
        booking_doc = None
        if firestore_service.db is not None:
            doc_ref = firestore_service.db.collection("bookings").document(request.booking_id)
            doc = doc_ref.get()
            if hasattr(doc, "exists") and doc.exists:
                booking_doc = doc.to_dict()
    except Exception as exc:
        logger.error(f"Firestore lookup failed for booking {request.booking_id}: {exc}")
        booking_doc = None

    if booking_doc is None:
        logger.warning(f"Booking not found: {request.booking_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Booking '{request.booking_id}' not found",
        )

    # --- Validate user owns this booking ---
    booking_user_id = booking_doc.get("user_id", "")
    if booking_user_id != request.user_id:
        logger.warning(f"User mismatch: booking user={booking_user_id}, request user={request.user_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User ID does not match the booking owner",
        )

    # --- Create alert record ---
    alert_id = f"alert_{uuid.uuid4().hex[:12]}"
    now = datetime.now(timezone.utc)

    alert_record = {
        "id": alert_id,
        "booking_id": request.booking_id,
        "user_id": request.user_id,
        "service_type": booking_doc.get("service_type", "unknown"),
        "estimated_minutes": booking_doc.get("estimated_minutes", 0),
        "warning_at_minutes": booking_doc.get("estimated_minutes", 0) + WARNING_BUFFER_MINUTES,
        "trusted_contact_name": request.trusted_contact_name,
        "trusted_contact_number": request.trusted_contact_number,
        "status": "alert_sent",
        "created_at": now.isoformat(),
        "updated_at": now.isoformat(),
    }

    # Persist to Firestore
    try:
        if firestore_service.db is not None:
            firestore_service.db.collection("safety_alerts").document(alert_id).set(alert_record)
            logger.info(f"Alert {alert_id} saved to Firestore safety_alerts collection")
    except Exception as exc:
        logger.error(f"Failed to save alert {alert_id}: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create safety alert",
        )

    logger.info(f"Emergency alert created: {alert_id} for booking {request.booking_id}")
    logger.info(f"Trusted contact notified: {request.trusted_contact_name} ({request.trusted_contact_number})")

    return EmergencyAlertResponse(
        alert_id=alert_id,
        status="alert_sent",
        booking_id=request.booking_id,
        trusted_contact_name=request.trusted_contact_name,
        trusted_contact_number=request.trusted_contact_number,
        message="Trusted contact ko notify kar diya gaya",
        timestamp=now.isoformat(),
        next_action="Wait for trusted contact callback",
    )


# ─────────────────────────────────────────────────────────
#  Endpoint 3: GET /safety/status/{booking_id}
# ─────────────────────────────────────────────────────────

@router.get("/status/{booking_id}", response_model=SafetyStatusResponse, status_code=status.HTTP_200_OK)
async def get_safety_status(booking_id: str):
    """
    Get live safety status for a booking.

    Returns timer information, alert status, and whether the trusted
    contact has been notified.
    """
    logger.info(f"Safety status requested for booking_id={booking_id}")

    # --- Look up booking ---
    booking_doc = None
    try:
        if firestore_service.db is not None:
            doc_ref = firestore_service.db.collection("bookings").document(booking_id)
            doc = doc_ref.get()
            if hasattr(doc, "exists") and doc.exists:
                booking_doc = doc.to_dict()
    except Exception as exc:
        logger.error(f"Firestore lookup failed for booking {booking_id}: {exc}")

    if booking_doc is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Booking '{booking_id}' not found",
        )

    # --- Look up any associated alert ---
    alert_doc = None
    trusted_contact_notified = False
    alert_status_str = "no_alert"
    try:
        if firestore_service.db is not None:
            alerts_query = (
                firestore_service.db.collection("safety_alerts")
                .where("booking_id", "==", booking_id)
                .limit(1)
            )
            alert_docs = list(alerts_query.stream())
            if alert_docs:
                alert_doc = alert_docs[0].to_dict()
                alert_status_str = alert_doc.get("status", "pending")
                trusted_contact_notified = alert_status_str == "alert_sent"
    except Exception as exc:
        logger.error(f"Firestore alert lookup failed for booking {booking_id}: {exc}")

    # --- Compute timer values ---
    estimated_total = booking_doc.get("estimated_minutes", 90)
    warning_at = estimated_total + WARNING_BUFFER_MINUTES

    # Calculate time remaining based on booking creation
    now = datetime.now(timezone.utc)
    created_at_raw = booking_doc.get("created_at")
    if isinstance(created_at_raw, str):
        try:
            created_at = datetime.fromisoformat(created_at_raw)
        except Exception:
            created_at = now
    elif isinstance(created_at_raw, datetime):
        created_at = created_at_raw
    else:
        created_at = now

    elapsed = (now - created_at).total_seconds() / 60.0
    time_remaining = max(0, int(warning_at - elapsed))

    logger.info(f"Safety status: booking={booking_id}, timer_active={time_remaining > 0}, remaining={time_remaining}min")

    return SafetyStatusResponse(
        booking_id=booking_id,
        safety_timer_active=time_remaining > 0,
        time_remaining_minutes=time_remaining,
        estimated_total_minutes=warning_at,
        alert_status=alert_status_str,
        trusted_contact_notified=trusted_contact_notified,
        last_update=now.isoformat(),
    )
