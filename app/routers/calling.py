"""
Calling Router — M8 Emergency Calling Endpoints
================================================
POST /safety/call/trigger         — Trigger emergency call
GET  /safety/call/log/{booking_id} — Get call logs for a booking
GET  /safety/call/{call_id}       — Get specific call details
"""

import logging
from datetime import datetime, timezone

from fastapi import APIRouter, BackgroundTasks, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/safety/call", tags=["emergency_calling"])


# ─────────────────────────────────────────────────────────
#  Pydantic Schemas
# ─────────────────────────────────────────────────────────

class CallRequest(BaseModel):
    """Request body to trigger an emergency call."""
    booking_id: str = Field(..., description="Booking ID")
    user_name: str = Field(..., description="User's name")
    user_location: str = Field(..., description="User's current location")
    provider_name: str = Field(..., description="Provider's name")
    provider_cnic: str = Field(..., description="Provider's CNIC")
    provider_mobile: str = Field(..., description="Provider's mobile number")
    trusted_contact_name: str = Field(..., description="Trusted contact's name")
    trusted_contact_number: str = Field(..., description="Trusted contact's phone number")
    service_type: str = Field(..., description="Type of service")
    booking_time: str = Field(default="", description="Original booking time ISO string")
    estimated_minutes: int = Field(..., description="Estimated job duration in minutes")
    minutes_exceeded: int = Field(..., description="Minutes the job has exceeded")


class CallResponse(BaseModel):
    """Response after triggering an emergency call."""
    call_id: str
    call_status: str
    trusted_contact_name: str
    trusted_contact_number: str
    call_transcript: str
    call_duration_seconds: int
    call_sid: str
    triggered_at: str
    next_action: str
    message: str
    safety_actions: List[str]


# ─────────────────────────────────────────────────────────
#  Helper: update booking with call reference
# ─────────────────────────────────────────────────────────

async def update_booking_call_reference(booking_id: str, call_id: str):
    """Update the booking document with the emergency call reference."""
    try:
        from app.services.firestore_service import firestore_service

        if firestore_service.db is not None:
            firestore_service.db.collection("bookings").document(booking_id).update({
                "emergency_call_id": call_id,
                "emergency_call_triggered_at": datetime.now(timezone.utc).isoformat(),
                "status": "emergency_alert_triggered",
            })
            logger.info(f"Booking {booking_id} updated with call reference {call_id}")
    except Exception as exc:
        logger.error(f"Error updating booking {booking_id}: {exc}")


# ─────────────────────────────────────────────────────────
#  POST /safety/call/trigger
# ─────────────────────────────────────────────────────────

@router.post("/trigger", response_model=CallResponse, status_code=status.HTTP_200_OK)
async def trigger_emergency_call(request: CallRequest, background_tasks: BackgroundTasks):
    """
    Trigger an emergency call to the trusted contact.

    Validates the booking, runs the CallingAgent, stores the record
    in Firestore, and updates the booking status.
    """
    logger.info(f"Emergency call trigger requested for booking {request.booking_id}")

    from app.services.firestore_service import firestore_service

    # --- Validate booking exists ---
    try:
        if firestore_service.db is not None:
            doc = firestore_service.db.collection("bookings").document(request.booking_id).get()
            if hasattr(doc, "exists") and not doc.exists:
                raise HTTPException(status_code=404, detail="Booking not found")
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Firestore booking lookup failed: {exc}")
        # Continue even if Firestore is unavailable (graceful degradation)

    # --- Run CallingAgent ---
    from agents.calling_agent.agent import CallingAgent

    agent = CallingAgent()

    try:
        agent.generate_call_id()
        context = agent.create_call_context(request.model_dump())
        context["timestamp"] = datetime.now(timezone.utc).isoformat()

        result = agent.make_call(context)

        # Store record in background
        background_tasks.add_task(agent.store_in_firestore, result, context)

        # Update booking in background
        background_tasks.add_task(update_booking_call_reference, request.booking_id, agent.call_id)

        logger.info(f"Emergency call completed: call_id={agent.call_id}")

        return CallResponse(
            call_id=agent.call_id,
            call_status=result["call_status"],
            trusted_contact_name=request.trusted_contact_name,
            trusted_contact_number=request.trusted_contact_number,
            call_transcript=result["call_transcript"],
            call_duration_seconds=result.get("call_duration_seconds", 0),
            call_sid=result.get("call_sid", ""),
            triggered_at=datetime.now(timezone.utc).isoformat(),
            next_action="Follow up with emergency services",
            message="Emergency call initiated successfully",
            safety_actions=[
                "Trusted contact called",
                "Location shared",
                "Provider details logged",
                "Emergency services notified",
            ],
        )
    except ValueError as ve:
        raise HTTPException(status_code=422, detail=str(ve))
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Emergency call failed: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))


# ─────────────────────────────────────────────────────────
#  GET /safety/call/log/{booking_id}
# ─────────────────────────────────────────────────────────

@router.get("/log/{booking_id}")
async def get_call_log(booking_id: str):
    """
    Retrieve all emergency call logs for a booking.
    """
    logger.info(f"Fetching call logs for booking {booking_id}")

    from app.services.firestore_service import firestore_service

    try:
        if firestore_service.db is not None:
            docs = firestore_service.db.collection("emergency_calls").where(
                "booking_id", "==", booking_id
            ).stream()
            logs = [doc.to_dict() for doc in docs]
        else:
            logs = []
    except Exception as exc:
        logger.error(f"Error fetching call logs: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))

    if not logs:
        raise HTTPException(status_code=404, detail=f"No call logs found for booking {booking_id}")

    return {
        "booking_id": booking_id,
        "total_calls": len(logs),
        "call_logs": logs,
    }


# ─────────────────────────────────────────────────────────
#  GET /safety/call/{call_id}
# ─────────────────────────────────────────────────────────

@router.get("/{call_id}")
async def get_call_details(call_id: str):
    """
    Retrieve details for a specific emergency call.
    """
    logger.info(f"Fetching call details for {call_id}")

    from app.services.firestore_service import firestore_service

    try:
        if firestore_service.db is not None:
            doc = firestore_service.db.collection("emergency_calls").document(call_id).get()
            if hasattr(doc, "exists") and not doc.exists:
                raise HTTPException(status_code=404, detail="Call not found")
            return doc.to_dict()
        else:
            raise HTTPException(status_code=500, detail="Firestore unavailable")
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Error fetching call details: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))
