import random
import logging
from datetime import datetime, timezone, timedelta
from typing import Any, Dict

import google.genai as genai
from google.genai import types

from agents.base import BaseAgent
from agents.calling_agent.schemas import CallingAgentInput, CallingAgentOutput
from core.firebase_client import get_firestore_client
from core.llm_client import get_gemini_client

logger = logging.getLogger(__name__)

MODEL_ID = "gemini-2.0-flash"


class CallingAgent(BaseAgent):
    """
    Agent 8: Emergency Calling Agent.
    Triggered only when Women Safety Mode is active and both user and provider
    fail to respond after a warning, exceeding safety timers.
    """

    name = "calling_agent"

    def __init__(self) -> None:
        self._llm_client: genai.Client = get_gemini_client()

    def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """
        Execute the Emergency Calling Agent.

        Args:
            input_data: A dictionary containing inputs conforming to CallingAgentInput.

        Returns:
            A dictionary conforming to CallingAgentOutput.
        """
        logger.info("[%s] Beginning emergency calling validation and simulation...", self.name)

        # 1. Parse and validate inputs
        params = CallingAgentInput(**input_data)
        booking_id = params.booking_id

        # 2. Retrieve booking safety parameters (from Firestore if available, otherwise from input)
        safety_mode = params.safety_mode
        warning_at = params.warning_at_time
        user_responded = params.user_responded
        provider_responded = params.provider_responded

        db = get_firestore_client()
        if db is not None:
            try:
                logger.info("[%s] Fetching booking '%s' from Firestore for safety verification...", self.name, booking_id)
                doc_ref = db.collection("bookings").document(booking_id).get()
                if doc_ref.exists:
                    b_data = doc_ref.to_dict()
                    safety_mode = b_data.get("safety_mode", safety_mode)
                    warning_at = b_data.get("warning_scheduled_at") or b_data.get("warning_at_time") or warning_at
                    logger.info("[%s] Firestore retrieved: safety_mode=%s, warning_at_time=%s", self.name, safety_mode, warning_at)
                else:
                    logger.warning("[%s] Booking '%s' not found in Firestore. Using parameter inputs.", self.name, booking_id)
            except Exception as exc:
                logger.warning("[%s] Firestore query failed: %s. Using parameter inputs.", self.name, exc)

        # Parse times for validation
        if params.current_time:
            current_dt = datetime.fromisoformat(params.current_time)
        else:
            current_dt = datetime.now(timezone.utc)

        if not warning_at:
            raise ValueError("warning_at_time is required to validate trigger conditions.")

        warning_dt = datetime.fromisoformat(warning_at)

        # Validate trigger conditions
        logger.info("[%s] Validating trigger conditions...", self.name)
        
        if not safety_mode:
            raise ValueError(f"Trigger validation failed: safety_mode is False for booking '{booking_id}'.")
            
        time_elapsed = current_dt - warning_dt
        if time_elapsed < timedelta(minutes=30):
            raise ValueError(
                f"Trigger validation failed: warning time has not been exceeded by 30+ minutes. "
                f"Warning at: {warning_at}, Current time: {current_dt.isoformat()}, Elapsed: {time_elapsed.total_seconds() / 60:.2f} mins."
            )
            
        if user_responded:
            raise ValueError("Trigger validation failed: user has responded to safety alerts.")
            
        if provider_responded:
            raise ValueError("Trigger validation failed: provider has responded to safety alerts.")

        logger.info("[%s] All trigger conditions met. Safety escalation confirmed.", self.name)

        # 3. Generate Urdu script calling transcript using Gemini
        now_utc = datetime.now(timezone.utc)
        timestamp_str = now_utc.strftime("%Y%m%d%H%M%S")
        
        prompt = (
            f"You are the KaamYaar AI Automated Safety Assistant.\n"
            f"Convert the following emergency template into a natural, spoken Urdu (Nastaliq script) voice message.\n"
            f"The message should sound urgent, calm, and highly professional.\n\n"
            f"Template to adapt:\n"
            f"\"Assalam o Alaikum, {params.trusted_contact_name} sahab/baji.\n"
            f"Main KaamYaar AI hun. \n"
            f"{params.user_name} ne {params.service_type} ki booking ki thi \n"
            f"aaj {params.booking_time} ko, {params.user_location} mein.\n"
            f"Service provider {params.provider_name} aya tha,\n"
            f"CNIC number {params.provider_cnic}.\n"
            f"Estimated time {params.estimated_minutes} minute thi,\n"
            f"lekin {params.minutes_exceeded} minute zyada ho gaye hain.\n"
            f"{params.user_name} ne abhi tak koi response nahi diya.\n"
            f"Meherbani farma ke unhe check karein.\n"
            f"Agar koi masla ho to 15 immediately madad karein.\n"
            f"Shukriya. KaamYaar AI safety service.\"\n\n"
            f"Instructions:\n"
            f"1. Return ONLY the spoken Urdu Nastaliq translation/adaptation of the message.\n"
            f"2. Do not include markdown headers, quotes, introduction, or English translation.\n"
            f"3. Ensure the names, location, times, and CNIC are correctly embedded."
        )

        call_transcript = ""
        gemini_success = False

        try:
            logger.info("[%s] Querying Gemini for Urdu script transcript...", self.name)
            response = self._llm_client.models.generate_content(
                model=MODEL_ID,
                contents=prompt,
                config=types.GenerateContentConfig(temperature=0.3)
            )
            call_transcript = response.text.strip()
            # Clean quotes if returned
            if call_transcript.startswith('"') and call_transcript.endswith('"'):
                call_transcript = call_transcript[1:-1].strip()
            gemini_success = True
            logger.info("[%s] Gemini call transcript generated successfully.", self.name)
        except Exception as exc:
            logger.warning("[%s] Gemini transcript generation failed: %s. Swerving to template fallback.", self.name, exc)

        if not gemini_success:
            call_transcript = (
                f"Assalam o Alaikum, {params.trusted_contact_name} sahab/baji. "
                f"Main KaamYaar AI hun. "
                f"{params.user_name} ne {params.service_type} ki booking ki thi aaj {params.booking_time} ko, {params.user_location} mein. "
                f"Service provider {params.provider_name} aya tha, CNIC number {params.provider_cnic}. "
                f"Estimated time {params.estimated_minutes} minute thi, lekin {params.minutes_exceeded} minute zyada ho gaye hain. "
                f"{params.user_name} ne abhi tak koi response nahi diya. Meherbani farma ke unhe check karein. "
                f"Agar koi masla ho to 15 immediately madad karein. Shukriya. KaamYaar AI safety service."
            )

        # 4. Simulate call attempt
        call_id = f"CALL-{timestamp_str}-{random.randint(1000, 9999)}"
        call_sid = f"KY-CALL-{timestamp_str}"
        call_status = "initiated"
        call_duration = 45

        logger.info("[%s] Simulating automated call to safety contact %s...", self.name, params.trusted_contact_number)

        # 5. Write call log to Firestore "emergency_calls" collection
        call_doc = {
            "call_id": call_id,
            "booking_id": booking_id,
            "triggered_at": now_utc.isoformat(),
            "trusted_contact_number": params.trusted_contact_number,
            "trusted_contact_name": params.trusted_contact_name,
            "call_status": call_status,
            "call_transcript": call_transcript,
            "provider_cnic": params.provider_cnic,
            "provider_mobile": params.provider_mobile,
            "user_location": params.user_location,
            "minutes_exceeded": params.minutes_exceeded,
            "call_sid": call_sid
        }

        firestore_logged = False
        booking_updated = False

        if db is not None:
            try:
                logger.info("[%s] Logging emergency call record to Firestore 'emergency_calls'...", self.name)
                db.collection("emergency_calls").document(call_id).set(call_doc)
                firestore_logged = True

                logger.info("[%s] Updating safety call status in booking '%s'...", self.name, booking_id)
                db.collection("bookings").document(booking_id).update({
                    "safety_call_made": True,
                    "safety_call_at": now_utc.isoformat(),
                    "safety_call_status": "completed"
                })
                booking_updated = True
                logger.info("[%s] Firestore updates completed.", self.name)
            except Exception as exc:
                logger.warning("[%s] Firestore transaction failed: %s. Continuing simulation.", self.name, exc)
        else:
            logger.info("[%s] Firestore database is offline; database writes simulated.", self.name)

        # Determine next action
        # - "escalate_to_authorities" (if 60+ min exceeded)
        # - "await_user_response" (otherwise)
        if params.minutes_exceeded >= 60:
            next_action = "escalate_to_authorities"
        else:
            next_action = "await_user_response"

        trigger_reason = f"Customer and provider failed to respond 30+ minutes past safety warning. Minutes exceeded: {params.minutes_exceeded}."

        output = CallingAgentOutput(
            call_id=call_id,
            booking_id=booking_id,
            call_status="completed" if gemini_success else "initiated",
            trusted_contact_name=params.trusted_contact_name,
            trusted_contact_number=params.trusted_contact_number,
            call_transcript=call_transcript,
            call_duration_seconds=call_duration,
            call_sid=call_sid,
            firestore_logged=firestore_logged,
            booking_updated=booking_updated,
            trigger_reason=trigger_reason,
            minutes_exceeded=params.minutes_exceeded,
            next_action=next_action
        )

        logger.info("[%s] Emergency calling process completed. Call SID: %s, Action: %s", self.name, call_sid, next_action)
        return output.model_dump()
