"""
CallingAgent — M8 Emergency Calling Agent
==========================================
Handles emergency calls to trusted contacts when safety timers expire.
Mock Twilio integration (production-ready structure).
"""

import uuid
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class CallingAgent:
    """
    Emergency calling agent — handles emergency calls to trusted contacts.
    """

    def __init__(self):
        self.call_id: Optional[str] = None
        self.call_sid: Optional[str] = None
        self.call_status: str = "initiated"

    # ─────────────────────────────────────────────────
    #  Public API
    # ─────────────────────────────────────────────────

    def run(self, request_data: dict) -> dict:
        """
        Main agent entry point.

        Validates input, generates call context, makes the call,
        stores the record in Firestore, and returns the result.
        """
        logger.info(f"CallingAgent.run() invoked for booking {request_data.get('booking_id')}")

        # 1. Validate
        self.validate_inputs(request_data)

        # 2. Generate unique call_id
        self.generate_call_id()

        # 3. Build context
        context = self.create_call_context(request_data)
        context["timestamp"] = datetime.now(timezone.utc).isoformat()

        # 4. Make call (mock / Twilio)
        result = self.make_call(context)
        self.call_status = result["call_status"]
        self.call_sid = result.get("call_sid")

        # 5. Store in Firestore
        self.store_in_firestore(result, context)

        # 6. Build response
        response = {
            "call_id": self.call_id,
            "call_status": result["call_status"],
            "trusted_contact_name": request_data["trusted_contact_name"],
            "trusted_contact_number": request_data["trusted_contact_number"],
            "call_transcript": result["call_transcript"],
            "call_duration_seconds": result.get("call_duration_seconds", 0),
            "call_sid": result.get("call_sid", ""),
            "next_action": "Follow up with emergency services",
            "safety_actions": [
                "Trusted contact notified",
                "Police alert sent",
                "Booking provider flagged",
            ],
        }

        logger.info(f"CallingAgent.run() completed — call_id={self.call_id}, status={self.call_status}")
        return response

    # ─────────────────────────────────────────────────
    #  Validation
    # ─────────────────────────────────────────────────

    def validate_inputs(self, data: dict) -> bool:
        """Validate all required fields are present."""
        required = [
            "booking_id",
            "user_name",
            "user_location",
            "provider_name",
            "provider_cnic",
            "provider_mobile",
            "trusted_contact_name",
            "trusted_contact_number",
            "service_type",
            "estimated_minutes",
            "minutes_exceeded",
        ]
        for field in required:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")
        return True

    # ─────────────────────────────────────────────────
    #  Call ID
    # ─────────────────────────────────────────────────

    def generate_call_id(self) -> str:
        """Generate a unique call ID."""
        self.call_id = f"call_{uuid.uuid4().hex[:8]}"
        logger.info(f"Generated call_id: {self.call_id}")
        return self.call_id

    # ─────────────────────────────────────────────────
    #  Context
    # ─────────────────────────────────────────────────

    def create_call_context(self, data: dict) -> dict:
        """Create detailed context dict for the call."""
        return {
            "call_id": self.call_id,
            "booking_id": data["booking_id"],
            "user_name": data["user_name"],
            "user_location": data["user_location"],
            "provider_name": data["provider_name"],
            "provider_cnic": data["provider_cnic"],
            "provider_mobile": data["provider_mobile"],
            "trusted_contact_name": data["trusted_contact_name"],
            "trusted_contact_number": data["trusted_contact_number"],
            "service_type": data["service_type"],
            "estimated_minutes": data["estimated_minutes"],
            "minutes_exceeded": data["minutes_exceeded"],
            "alert_reason": f"Service time exceeded: {data['minutes_exceeded']} minutes overdue",
        }

    # ─────────────────────────────────────────────────
    #  Call execution (Mock Twilio)
    # ─────────────────────────────────────────────────

    def make_call(self, context: dict) -> dict:
        """
        Simulate / make an actual call via Twilio.

        Current implementation is a **mock** — swap the body of this
        method with real ``twilio.rest.Client`` calls for production.
        """
        try:
            call_transcript = self._generate_transcript(context)
            call_sid = f"SM{context['call_id']}"
            self.call_sid = call_sid

            logger.info(
                f"Mock call placed to {context['trusted_contact_name']} "
                f"({context['trusted_contact_number']}) — SID {call_sid}"
            )

            return {
                "call_status": "completed",
                "call_sid": call_sid,
                "call_transcript": call_transcript,
                "call_duration_seconds": 180,
                "contact_reached": True,
                "contact_response": "Will reach location in 5 minutes",
            }
        except Exception as exc:
            logger.error(f"Call failed: {exc}")
            return {
                "call_status": "failed",
                "call_sid": "",
                "error": str(exc),
                "call_transcript": "",
                "call_duration_seconds": 0,
                "contact_reached": False,
                "contact_response": "",
            }

    # ─────────────────────────────────────────────────
    #  Transcript
    # ─────────────────────────────────────────────────

    def _generate_transcript(self, context: dict) -> str:
        """Generate a realistic call transcript."""
        transcript = (
            "EMERGENCY CALL TRANSCRIPT\n"
            "========================\n"
            f"Call ID: {context['call_id']}\n"
            f"Time: {context.get('timestamp', 'N/A')}\n"
            "\n"
            "Caller: KaamYaar Emergency System\n"
            f"To: {context['trusted_contact_name']} ({context['trusted_contact_number']})\n"
            "\n"
            'SYSTEM: "Assalamu Alaikum! KaamYaar emergency alert."\n'
            f'SYSTEM: "Your friend {context["user_name"]} needs help."\n'
            f'SYSTEM: "Service: {context["service_type"]}"\n'
            f'SYSTEM: "Location: {context["user_location"]}"\n'
            f'SYSTEM: "Provider: {context["provider_name"]}"\n'
            f'SYSTEM: "Reason: {context["alert_reason"]}"\n'
            "\n"
            'CONTACT: "Yes, I\'m coming right away!"\n'
            "\n"
            'SYSTEM: "Thank you. Police has been alerted. Stay safe."\n'
            'SYSTEM: "Call ended."\n'
            "\n"
            "Duration: 3 minutes\n"
            "Status: COMPLETED"
        )
        return transcript

    # ─────────────────────────────────────────────────
    #  Firestore persistence
    # ─────────────────────────────────────────────────

    def store_in_firestore(self, result: dict, context: dict) -> bool:
        """Store the call record in the ``emergency_calls`` Firestore collection."""
        try:
            from app.services.firestore_service import firestore_service

            now = datetime.now(timezone.utc).isoformat()
            record = {
                "call_id": context["call_id"],
                "booking_id": context["booking_id"],
                "user_name": context["user_name"],
                "user_location": context["user_location"],
                "provider_name": context["provider_name"],
                "provider_cnic": context["provider_cnic"],
                "provider_mobile": context["provider_mobile"],
                "trusted_contact_name": context["trusted_contact_name"],
                "trusted_contact_number": context["trusted_contact_number"],
                "service_type": context["service_type"],
                "estimated_minutes": context["estimated_minutes"],
                "minutes_exceeded": context["minutes_exceeded"],
                "call_status": result["call_status"],
                "call_sid": result.get("call_sid", ""),
                "call_transcript": result.get("call_transcript", ""),
                "call_duration_seconds": result.get("call_duration_seconds", 0),
                "contact_reached": result.get("contact_reached", False),
                "contact_response": result.get("contact_response", ""),
                "created_at": now,
                "updated_at": now,
            }

            if firestore_service.db is not None:
                firestore_service.db.collection("emergency_calls").document(
                    context["call_id"]
                ).set(record)
                logger.info(f"Call record {context['call_id']} saved to Firestore")

            return True
        except Exception as exc:
            logger.error(f"Error storing call record: {exc}")
            return False
