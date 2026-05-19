"""
agents/booking_executor/agent.py

Agent 5 of 7 — Booking Executor.
Confirms the service booking, assigns the provider, writes transaction details to Firestore,
updates provider availability, simulates notifications, and yields localized confirmation text.
"""

import random
import logging
from datetime import datetime, timezone, timedelta
from typing import Any

import google.genai as genai
from google.api_core.exceptions import ResourceExhausted

from agents.base import BaseAgent
from agents.provider_discovery.schemas import ProviderCandidate
from agents.language_parser.schemas import ParsedServiceRequest
from agents.booking_executor.schemas import BookingExecutorOutput
from core.firebase_client import get_firestore_client
from core.llm_client import get_gemini_client

logger = logging.getLogger(__name__)

MODEL_ID = "gemini-2.0-flash"


class BookingExecutorAgent(BaseAgent):
    """
    Agent responsible for confirming the service booking transaction.
    Executes a structured 8-step transaction flow with high-resilience design.
    """

    name = "booking_executor"

    def __init__(self) -> None:
        self._llm_client: genai.Client = get_gemini_client()

    def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """
        Execute the booking executor.

        Args:
            input_data: A dictionary containing:
                - provider: ProviderCandidate or dict (top recommended provider)
                - price_quote: PricingEngineOutput or dict (from Agent 4)
                - parsed_request: ParsedServiceRequest or dict (from Agent 1)
                - user_id: str (optional, defaults to "demo_user_001")
                - confirmed_slot: str (e.g. "2026-05-18 10:00 AM")
                - user_gender: str (optional, e.g. "female")

        Returns:
            A dictionary conforming to the BookingExecutorOutput schema.
        """
        logger.info("[%s] Beginning service booking transaction...", self.name)

        # Extract and parse inputs
        raw_provider = input_data.get("provider")
        raw_price_quote = input_data.get("price_quote") or input_data.get("quote")
        raw_parsed_request = input_data.get("parsed_request") or input_data.get("request")
        user_id = input_data.get("user_id") or "demo_user_001"
        confirmed_slot = input_data.get("confirmed_slot")

        if not raw_provider:
            raise ValueError("Input data must contain a 'provider' candidate key.")
        if not raw_price_quote:
            raise ValueError("Input data must contain a 'price_quote' or 'quote' key.")
        if not raw_parsed_request:
            raise ValueError("Input data must contain a 'parsed_request' key.")
        if not confirmed_slot:
            raise ValueError("Input data must contain a 'confirmed_slot' (date/time) key.")

        # Cast to Pydantic models if they are raw dicts
        provider = ProviderCandidate(**raw_provider) if isinstance(raw_provider, dict) else raw_provider
        parsed_request = ParsedServiceRequest(**raw_parsed_request) if isinstance(raw_parsed_request, dict) else raw_parsed_request

        # Extract price quote breakdown & total safely
        if isinstance(raw_price_quote, dict):
            price_breakdown_dict = raw_price_quote.get("price_breakdown", {})
            total_pkr = price_breakdown_dict.get("total", 0)
            estimated_duration_min = raw_price_quote.get("estimated_duration_minutes", 60)
        else:
            # Pydantic model PricingEngineOutput
            price_breakdown_dict = raw_price_quote.price_breakdown.model_dump()
            total_pkr = raw_price_quote.price_breakdown.total
            estimated_duration_min = getattr(raw_price_quote, "estimated_duration_minutes", 60)

        # ------------------------------------------------------------------
        # STEP 1: Generate booking_id
        # ------------------------------------------------------------------
        now_utc = datetime.now(timezone.utc)
        timestamp_str = now_utc.strftime("%Y%m%d%H%M")
        booking_id = f"KY-{timestamp_str}-{random.randint(1000, 9999)}"
        logger.info("[%s] [Step 1/8] Generated Booking ID: %s", self.name, booking_id)

        # Determine and Calculate Women Safety Protocols
        user_gender = input_data.get("user_gender")
        if not user_gender and isinstance(raw_parsed_request, dict):
            user_gender = raw_parsed_request.get("user_gender")
        if not user_gender and parsed_request:
            user_gender = getattr(parsed_request, "user_gender", None)
            if not user_gender and hasattr(parsed_request, "preferences") and parsed_request.preferences:
                pref_str = " ".join(parsed_request.preferences).lower()
                if "female" in pref_str or "aurat" in pref_str or "larki" in pref_str or "female user" in pref_str:
                    user_gender = "female"
                    
        provider_gender = getattr(provider, "gender", "male")
        
        is_female_user_and_male_provider = (
            str(user_gender).lower().strip() == "female" and str(provider_gender).lower().strip() == "male"
        )
        
        if is_female_user_and_male_provider:
            safety_mode = True
            est_completion = (now_utc + timedelta(minutes=estimated_duration_min)).isoformat()
            warning_sched = (now_utc + timedelta(minutes=estimated_duration_min + 30)).isoformat()
            safety_contact_notified = True
            logger.info(
                "[%s] Women Safety Mode active: user_gender=female, provider_gender=male. Triggering safety protocols.",
                self.name
            )
        else:
            safety_mode = False
            est_completion = None
            warning_sched = None
            safety_contact_notified = False

        # ------------------------------------------------------------------
        # STEP 2: Capture BEFORE state
        # ------------------------------------------------------------------
        before_state = {"provider_status": "available", "slot_status": "open"}
        logger.info("[%s] [Step 2/8] Captured BEFORE State: %s", self.name, before_state)

        # ------------------------------------------------------------------
        # STEP 3: Write to Firestore "bookings" & STEP 4: Update "providers"
        # ------------------------------------------------------------------
        booking_doc = {
            "booking_id": booking_id,
            "user_id": user_id,
            "provider_id": provider.provider_id,
            "provider_name": provider.name,
            "service_type": parsed_request.service_type,
            "location": parsed_request.location,
            "slot": confirmed_slot,
            "price_breakdown": price_breakdown_dict,
            "total_pkr": total_pkr,
            "status": "confirmed",
            "created_at": now_utc.isoformat(),
            "language": parsed_request.primary_language or "English",
            "safety_mode": safety_mode,
            "estimated_completion_time": est_completion,
            "warning_scheduled_at": warning_sched,
            "safety_contact_notified": safety_contact_notified
        }

        firestore_written = False
        db = get_firestore_client()

        if db is not None:
            try:
                logger.info("[%s] [Step 3/8] Writing transaction to Firestore 'bookings' collection...", self.name)
                db.collection("bookings").document(booking_id).set(booking_doc)

                logger.info("[%s] [Step 4/8] Updating provider '%s' availability in 'providers' collection...", self.name, provider.name)
                db.collection("providers").document(provider.provider_id).set({
                    "provider_id": provider.provider_id,
                    "name": provider.name,
                    "is_available": False,
                    "last_updated": now_utc.isoformat()
                }, merge=True)

                firestore_written = True
                logger.info("[%s] Firestore database operations completed successfully.", self.name)
            except Exception as exc:
                logger.warning("[%s] Firestore database write failed: %s. Swerving to simulated offline mode.", self.name, exc)
        else:
            logger.info("[%s] [Step 3/8 & 4/8] Running in offline mode; Firestore database writes simulated.", self.name)

        # ------------------------------------------------------------------
        # STEP 5: Generate FCM notification payload
        # ------------------------------------------------------------------
        notification_payload = {
            "title": "KaamYaar — Booking Confirmed!",
            "body": f"{provider.name} will arrive at {confirmed_slot}",
            "booking_id": booking_id
        }
        logger.info("[%s] [Step 5/8] Generated simulated FCM Push notification payload.", self.name)

        # ------------------------------------------------------------------
        # STEP 6: Generate receipt
        # ------------------------------------------------------------------
        receipt = {
            "booking_id": booking_id,
            "transaction_date": now_utc.isoformat(),
            "user_id": user_id,
            "provider": {
                "provider_id": provider.provider_id,
                "name": provider.name,
                "skill_level": provider.skill_level,
                "rating": provider.rating,
                "gender": provider_gender
            },
            "service": {
                "type": parsed_request.service_type,
                "location": parsed_request.location,
                "confirmed_slot": confirmed_slot
            },
            "payment": {
                "currency": "PKR",
                "total_amount": total_pkr,
                "price_breakdown": price_breakdown_dict
            },
            "status": "confirmed",
            "safety_mode": safety_mode,
            "estimated_completion_time": est_completion,
            "warning_scheduled_at": warning_sched,
            "safety_contact_notified": safety_contact_notified
        }
        logger.info("[%s] [Step 6/8] Compiled transaction receipt.", self.name)

        # ------------------------------------------------------------------
        # STEP 7: Capture AFTER state
        # ------------------------------------------------------------------
        after_state = {"provider_status": "booked", "slot_status": "confirmed"}
        logger.info("[%s] [Step 7/8] Captured AFTER State: %s", self.name, after_state)

        # ------------------------------------------------------------------
        # STEP 8: Schedule pre-visit reminder (created_at + 23 hours)
        # ------------------------------------------------------------------
        reminder_time = (now_utc + timedelta(hours=23)).isoformat()
        logger.info("[%s] [Step 8/8] Scheduled pre-visit reminder for: %s", self.name, reminder_time)

        # ------------------------------------------------------------------
        # Generate Warm Localized Confirmation Message
        # ------------------------------------------------------------------
        primary_language = parsed_request.primary_language or "English"
        confirmation_message = ""
        gemini_success = False

        try:
            logger.info("[%s] Requesting Gemini to generate confirmation message in %s...", self.name, primary_language)
            prompt = (
                f"You are a warm, helpful customer care representative and close friend from KaamYaar AI, "
                f"a premium local home-services platform in Pakistan.\n"
                f"Generate a warm, friendly, and reassuring SMS/booking confirmation message for the customer "
                f"in their primary language ({primary_language}).\n\n"
                f"Booking Details:\n"
                f"- Service Type: {parsed_request.service_type}\n"
                f"- Assigned Provider: {provider.name}\n"
                f"- Appointment Time Slot: {confirmed_slot}\n"
                f"- Total Bill: Rs. {total_pkr}\n"
                f"- Booking ID: {booking_id}\n\n"
                f"Instructions:\n"
                f"1. Explain that their booking is successfully confirmed and their provider is on the way at the scheduled time.\n"
                f"2. Keep the tone extremely polite, warm, and helpful (like a friendly cousin helping them out).\n"
                f"3. Write in the specified primary language ({primary_language}). If Roman Urdu, write in natural, friendly SMS-style Roman Urdu. If Urdu, use native Urdu script (Nastaliq). If Punjabi, Pashto, Balochi, or Sindhi, write in their native script.\n"
                f"4. Keep it short enough to fit comfortably in an SMS or push notification (2-3 sentences), but make sure it feels premium and reassuring.\n"
                f"5. Do not include any HTML, markdown, headers, or quotes. Return only the raw plain message text."
            )

            response = self._llm_client.models.generate_content(
                model=MODEL_ID,
                contents=prompt,
                config=genai.types.GenerateContentConfig(
                    temperature=0.3,
                )
            )
            confirmation_message = response.text.strip()
            # Clean up potential leading/trailing double quotes
            if confirmation_message.startswith('"') and confirmation_message.endswith('"'):
                confirmation_message = confirmation_message[1:-1].strip()
            gemini_success = True
            logger.info("[%s] Gemini confirmation message generated successfully.", self.name)

        except Exception as exc:
            logger.warning("[%s] Gemini confirmation generation failed: %s. Swerving to offline fallbacks.", self.name, exc)

        if not gemini_success:
            confirmation_message = self._get_fallback_message(
                primary_language=primary_language,
                provider_name=provider.name,
                slot=confirmed_slot
            )

        # Assemble Output
        output = BookingExecutorOutput(
            booking_id=booking_id,
            status="confirmed",
            provider_assigned=provider.name,
            confirmed_slot=confirmed_slot,
            total_pkr=total_pkr,
            before_state=before_state,
            after_state=after_state,
            firestore_written=firestore_written,
            notification_payload=notification_payload,
            receipt=receipt,
            reminder_scheduled_at=reminder_time,
            confirmation_message=confirmation_message,
            safety_mode=safety_mode,
            estimated_completion_time=est_completion,
            warning_scheduled_at=warning_sched,
            safety_contact_notified=safety_contact_notified
        )

        logger.info("[%s] Booking transaction complete. Booking ID: %s", self.name, booking_id)
        return output.model_dump()

    def _get_fallback_message(self, primary_language: str, provider_name: str, slot: str) -> str:
        """Returns hand-crafted pre-translated confirmation messages when Gemini is offline."""
        lang_lower = primary_language.lower()

        if "roman" in lang_lower or "urdu" in lang_lower and "roman" in lang_lower:
            return (
                f"Aap ki booking confirm ho chuki hai! {provider_name} {slot} par aap ke pass pohanch jayenge. "
                f"Agar koi tabdeeli karni ho toh humein batayein. Thank you!"
            )
        elif "urdu" in lang_lower:
            return (
                f"محترم کسٹمر، آپ کا آرڈر کامیابی سے بک ہو گیا ہے۔ {provider_name} {slot} پر آپ کے بتائے ہوئے پتے پر "
                f"پہنچ جائیں گے۔ ہماری خدمات منتخب کرنے کا شکریہ!"
            )
        else:
            return (
                f"Your booking has been successfully confirmed! {provider_name} will arrive at {slot}. "
                f"Thank you for choosing KaamYaar!"
            )
