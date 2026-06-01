"""
agents/quality_monitor/agent.py

Agent 6 of 7 — Service Quality Monitor.
Tracks the post-booking service lifecycle stages, collects customer reviews/checklists,
updates provider rating statistics in Firestore, and documents future matching score impacts.
"""

import os
import json
import logging
from datetime import datetime, timezone, timedelta
from typing import Any

from agents.base import BaseAgent
from agents.quality_monitor.schemas import QualityMonitorOutput, CustomerFeedback
from core.firebase_client import get_firestore_client

logger = logging.getLogger(__name__)


class QualityMonitorAgent(BaseAgent):
    """
    Agent responsible for service stage simulation, customer feedback processing,
    and provider rating adjustments.
    """

    name = "quality_monitor"

    def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """
        Execute the Quality Monitor Agent.

        Args:
            input_data: A dictionary containing:
                - booking_id: str
                - provider_id: str
                - simulation_mode: bool = True (default)
                - feedback: dict (optional, required if simulation_mode is False)

        Returns:
            A dictionary conforming to the QualityMonitorOutput schema.
        """
        logger.info("[%s] Beginning service quality monitoring...", self.name)

        booking_id = input_data.get("booking_id")
        provider_id = input_data.get("provider_id")
        simulation_mode = input_data.get("simulation_mode", True)
        raw_feedback = input_data.get("feedback")

        if not booking_id:
            raise ValueError("Input data must contain a 'booking_id'.")
        if not provider_id:
            raise ValueError("Input data must contain a 'provider_id'.")

        # ------------------------------------------------------------------
        # STAGE SIMULATION & FEEDBACK SEEDING
        # ------------------------------------------------------------------
        now_utc = datetime.now(timezone.utc)
        stage_log = []

        if simulation_mode:
            logger.info("[%s] Running in SIMULATION mode. Progressing through stages...", self.name)
            # Auto-generate logs with 5-minute increments
            stage_log = [
                {
                    "stage": "ASSIGNED",
                    "status": "provider confirmed, heading to location",
                    "timestamp": now_utc.isoformat()
                },
                {
                    "stage": "EN_ROUTE",
                    "status": "provider is on the way",
                    "timestamp": (now_utc + timedelta(minutes=5)).isoformat()
                },
                {
                    "stage": "ARRIVED",
                    "status": "provider reached location",
                    "timestamp": (now_utc + timedelta(minutes=10)).isoformat()
                },
                {
                    "stage": "IN_PROGRESS",
                    "status": "work started",
                    "timestamp": (now_utc + timedelta(minutes=15)).isoformat()
                },
                {
                    "stage": "COMPLETED",
                    "status": "work done",
                    "timestamp": (now_utc + timedelta(minutes=20)).isoformat()
                }
            ]

            # Log stage transitions clearly for traces
            for log in stage_log:
                logger.info("[%s] Stage Transition: %s | %s at %s", self.name, log["stage"], log["status"], log["timestamp"])

            # Seeding positive mock feedback if none is provided
            if not raw_feedback:
                raw_feedback = {
                    "customer_rating": 4.5,
                    "review_text": "MashaAllah, bohot zabardast kaam kiya! Waqt par aaye aur professional tareeqay se pipe leak theek kiya.",
                    "checklist": {
                        "work_quality": True,
                        "on_time": True,
                        "professional_behavior": True,
                        "correct_pricing": True,
                        "would_recommend": True
                    },
                    "evidence_placeholder": "photo/video upload supported"
                }
                logger.info("[%s] Auto-generated simulated feedback with 4.5 rating.", self.name)
        else:
            logger.info("[%s] Running in LIVE mode.", self.name)
            if not raw_feedback:
                raise ValueError("In live mode (simulation_mode=False), 'feedback' dictionary is required.")

            stage_log = [
                {
                    "stage": "COMPLETED",
                    "status": "work done, feedback collected",
                    "timestamp": now_utc.isoformat()
                }
            ]
            logger.info("[%s] Stage Transition: COMPLETED at %s", self.name, now_utc.isoformat())

        # Validate feedback against schema
        feedback = CustomerFeedback(**raw_feedback)
        feedback_dict = feedback.model_dump()
        customer_rating = feedback.customer_rating

        # ------------------------------------------------------------------
        # RECALCULATE PROVIDER RATING
        # ------------------------------------------------------------------
        old_rating = 4.5
        old_review_count = 10
        db = get_firestore_client()
        loaded_from_firestore = False

        if db is not None:
            try:
                logger.info("[%s] Fetching provider '%s' stats from Firestore...", self.name, provider_id)
                prov_ref = db.collection("providers").document(provider_id).get()
                if prov_ref.exists:
                    prov_data = prov_ref.to_dict() or {}
                    old_rating = float(prov_data.get("rating", 4.5))
                    old_review_count = int(prov_data.get("review_count", 10))
                    loaded_from_firestore = True
                    logger.info("[%s] Loaded Firestore stats: Rating = %s, Reviews = %d", self.name, old_rating, old_review_count)
            except Exception as exc:
                logger.warning("[%s] Failed to fetch provider stats from Firestore: %s. Swerving to local database fallback.", self.name, exc)

        if not loaded_from_firestore:
            # Fallback: try loading from data/providers.json local file to maintain simulation fidelity
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            providers_file = os.path.join(base_dir, "data", "providers.json")

            if os.path.exists(providers_file):
                try:
                    logger.info("[%s] Seeding old provider stats from local JSON file...", self.name)
                    with open(providers_file, "r", encoding="utf-8") as f:
                        providers = json.load(f)
                        for p in providers:
                            if p.get("provider_id") == provider_id:
                                old_rating = float(p.get("rating", 4.5))
                                old_review_count = int(p.get("review_count", 10))
                                loaded_from_firestore = True
                                logger.info("[%s] Found local provider stats: Rating = %s, Reviews = %d", self.name, old_rating, old_review_count)
                                break
                except Exception as exc:
                    logger.warning("[%s] Failed to parse local providers.json: %s", self.name, exc)

            if not loaded_from_firestore:
                logger.info("[%s] No historical record found for provider '%s'. Using defaults (4.5 rating, 10 reviews).", self.name, provider_id)

        # Running average recalculation
        new_rating = (old_rating * old_review_count + customer_rating) / (old_review_count + 1)
        new_rating = round(new_rating, 2)
        new_review_count = old_review_count + 1
        logger.info("[%s] Recalculated provider rating: %s -> %s (Reviews: %d -> %d)",
                    self.name, old_rating, new_rating, old_review_count, new_review_count)

        # ------------------------------------------------------------------
        # DOUBLE FIRESTORE WRITE-BACK
        # ------------------------------------------------------------------
        rating_updated_in_firestore = False

        if db is not None:
            try:
                # 1. Update provider collection stats
                logger.info("[%s] Writing updated rating to 'providers' collection in Firestore...", self.name)
                db.collection("providers").document(provider_id).set({
                    "provider_id": provider_id,
                    "rating": new_rating,
                    "review_count": new_review_count,
                    "last_updated": now_utc.isoformat()
                }, merge=True)

                # 2. Update booking status & feedback in bookings collection
                logger.info("[%s] Updating booking document '%s' to status 'completed' in Firestore...", self.name, booking_id)
                db.collection("bookings").document(booking_id).set({
                    "status": "completed",
                    "feedback": feedback_dict,
                    "stage_log": stage_log,
                    "completed_at": now_utc.isoformat()
                }, merge=True)

                rating_updated_in_firestore = True
                logger.info("[%s] Firestore database synchronization complete.", self.name)
            except Exception as exc:
                logger.warning("[%s] Firestore database update failed: %s. Continuing offline simulation.", self.name, exc)
        else:
            logger.info("[%s] Running offline; Firestore dual write-backs simulated.", self.name)

        # ------------------------------------------------------------------
        # COMPOSE FUTURE MATCHING note
        # ------------------------------------------------------------------
        impact_notes = []

        if customer_rating >= 4.0:
            impact_notes.append(f"Excellent review score ({customer_rating}/5.0) will boost this provider's ranking score in future requests.")
        else:
            impact_notes.append(f"Sub-optimal review score ({customer_rating}/5.0) will penalize this provider's ranking score in future matching rounds.")

        if feedback.checklist.would_recommend:
            impact_notes.append("The positive 'Would Recommend' flag will prioritize this provider for repeat matching requests from this customer.")
        else:
            impact_notes.append("Negative recommendation flag will de-prioritize this technician for future matching attempts by this customer.")

        if not feedback.checklist.on_time:
            impact_notes.append("Delay flag will negatively impact the provider's on-time reliability score.")

        future_matching_note = " ".join(impact_notes)
        logger.info("[%s] Quality Monitor check complete. Future Matching Note: %s", self.name, future_matching_note)

        # Assemble Output Envelope
        output = QualityMonitorOutput(
            booking_id=booking_id,
            final_status="completed",
            stage_log=stage_log,
            customer_feedback=feedback_dict,
            old_provider_rating=old_rating,
            new_provider_rating=new_rating,
            rating_updated_in_firestore=rating_updated_in_firestore,
            future_matching_note=future_matching_note
        )

        return output.model_dump()
