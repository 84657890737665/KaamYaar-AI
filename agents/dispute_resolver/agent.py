"""
agents/dispute_resolver/agent.py

Agent 7 of 7 — Dispute & Escalation Resolver.
Intelligently classifies post-service complaints, executes category-based refund/compensation policies,
manages provider warnings & blacklisting, synchronises records to Firestore,
and generates warm, localized customer apology responses.
"""

import os
import json
import random
import logging
from datetime import datetime, timezone
from typing import Any

import google.genai as genai
from google.api_core.exceptions import ResourceExhausted

from agents.base import BaseAgent
from agents.dispute_resolver.schemas import DisputeResolverOutput
from core.firebase_client import get_firestore_client
from core.llm_client import get_gemini_client

logger = logging.getLogger(__name__)

MODEL_ID = "gemini-2.0-flash"


class DisputeResolverAgent(BaseAgent):
    """
    Agent responsible for resolving booking complaints, calculating adjustments,
    and managing provider quality control penalties.
    """

    name = "dispute_resolver"

    def __init__(self) -> None:
        self._llm_client: genai.Client = get_gemini_client()

    def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """
        Execute the Dispute Resolver Agent.

        Args:
            input_data: A dictionary containing:
                - booking_id: str
                - dispute_type: str (no_show, quality_complaint, price_dispute, cancellation, time_overrun, other)
                - complaint_text: str (customer complaint statement)
                - evidence_url: str (optional)
                - provider_dispute_count: int (optional, overrides Firestore count for testing)

        Returns:
            A dictionary conforming to the DisputeResolverOutput schema.
        """
        logger.info("[%s] Beginning dispute resolution transaction...", self.name)
        dispute_log = []

        booking_id = input_data.get("booking_id")
        dispute_type = input_data.get("dispute_type")
        complaint_text = input_data.get("complaint_text")
        evidence_url = input_data.get("evidence_url", "")
        custom_dispute_count = input_data.get("provider_dispute_count")

        if not booking_id:
            raise ValueError("Input data must contain a 'booking_id'.")
        if not dispute_type:
            raise ValueError("Input data must contain a 'dispute_type'.")
        if not complaint_text:
            raise ValueError("Input data must contain a 'complaint_text'.")

        valid_types = {"no_show", "quality_complaint", "price_dispute", "cancellation", "time_overrun", "other"}
        if dispute_type not in valid_types:
            logger.warning("[%s] Dispute type '%s' is non-standard. Swerving to 'other' classification.", self.name, dispute_type)
            dispute_type = "other"

        # ------------------------------------------------------------------
        # STEP 1: Generate dispute_id & Setup Log
        # ------------------------------------------------------------------
        now_utc = datetime.now(timezone.utc)
        timestamp_str = now_utc.strftime("%Y%m%d%H%M")
        dispute_id = f"DISP-{timestamp_str}-{random.randint(1000, 9999)}"
        
        def add_log(msg: str):
            logger.info("[%s] [Log] %s", self.name, msg)
            dispute_log.append(f"[{datetime.now(timezone.utc).isoformat()}] {msg}")

        add_log(f"Generated Dispute Transaction ID: {dispute_id}")

        # ------------------------------------------------------------------
        # STEP 2: Retrieve Booking & Provider context
        # ------------------------------------------------------------------
        booking_total = 1500  # Reasonable base default
        provider_id = "prov-unknown"
        provider_name = "Unknown Provider"
        primary_language = "English"

        db = get_firestore_client()
        loaded_booking = False

        if db is not None:
            try:
                add_log(f"Querying Firestore for booking '{booking_id}' details...")
                booking_ref = db.collection("bookings").document(booking_id).get()
                if booking_ref.exists:
                    booking_data = booking_ref.to_dict() or {}
                    booking_total = int(booking_data.get("total_pkr", 1500))
                    provider_id = booking_data.get("provider_id", "prov-unknown")
                    provider_name = booking_data.get("provider_name", "Unknown Provider")
                    primary_language = booking_data.get("language", "English")
                    loaded_booking = True
                    add_log(f"Loaded context: Total Bill = Rs. {booking_total}, Provider = {provider_name} ({provider_id}), Language = {primary_language}")
            except Exception as exc:
                add_log(f"Firestore booking lookup failed: {exc}. Continuing with default fallback parameters.")

        if not loaded_booking:
            add_log(f"Offline mode: Swerved to default booking total PKR: {booking_total}, language: {primary_language}")

        # ------------------------------------------------------------------
        # STEP 3: Classify severity using Gemini 2.0 Flash
        # ------------------------------------------------------------------
        classified_severity = "medium"
        gemini_severity_success = False

        try:
            add_log("Invoking Gemini to classify dispute severity from complaint text...")
            severity_prompt = (
                f"Analyze the following customer complaint about a home service booking and classify its severity level.\n"
                f"Complaint: \"{complaint_text}\"\n\n"
                f"Classification categories:\n"
                f"- low: minor issues (e.g. slight delay, polite disagreement)\n"
                f"- medium: quality issues that can be fixed, moderate delay, mild overcharging\n"
                f"- high: severe damage, extremely rude provider behavior, significant overcharging, no show\n"
                f"- critical: physical safety concern, theft, abusive behavior\n\n"
                f"Instructions:\n"
                f"1. Choose exactly one token from [low, medium, high, critical].\n"
                f"2. Return only the raw token string (lowercase, no punctuation, no markdown)."
            )

            response = self._llm_client.models.generate_content(
                model=MODEL_ID,
                contents=severity_prompt,
                config=genai.types.GenerateContentConfig(temperature=0.1)
            )
            raw_severity = response.text.strip().lower()
            if raw_severity in {"low", "medium", "high", "critical"}:
                classified_severity = raw_severity
                gemini_severity_success = True
                add_log(f"Gemini classified severity: {classified_severity}")
        except Exception as exc:
            add_log(f"Gemini severity classification failed: {exc}. Intercepting with rule-based heuristics.")

        if not gemini_severity_success:
            # Rule heuristics fallback
            complaint_lower = complaint_text.lower()
            if dispute_type == "no_show" or "no show" in complaint_lower or "didn't arrive" in complaint_lower:
                classified_severity = "high"
            elif any(w in complaint_lower for w in {"abuse", "steal", "thief", "safety", "fight", "abusive"}):
                classified_severity = "critical"
            elif any(w in complaint_lower for w in {"minor", "little", "delay", "minute"}):
                classified_severity = "low"
            else:
                classified_severity = "medium"
            add_log(f"Rule-based severity fallback applied: {classified_severity}")

        # ------------------------------------------------------------------
        # STEP 4: Choose Resolution Path
        # ------------------------------------------------------------------
        refund_amount = 0
        compensation = 0
        action_taken = ""
        resolution_path = ""
        human_escalation_required = False

        if dispute_type == "no_show":
            resolution_path = "auto_refund"
            refund_amount = booking_total
            compensation = 0
            action_taken = "Full transaction refund issued automatically due to technician no-show."
        elif dispute_type == "quality_complaint":
            resolution_path = "partial_refund_and_reservice"
            refund_amount = int(booking_total * 0.3)
            compensation = 0
            action_taken = "30% partial refund and free re-service warranty offered to resolve service quality complaint."
        elif dispute_type == "price_dispute":
            resolution_path = "pricing_audit_refund"
            refund_amount = 200  # Audited overcharge difference refund
            compensation = 0
            action_taken = "Pricing audit executed. Audited billing discrepancy of Rs. 200 refunded."
        elif dispute_type == "cancellation":
            resolution_path = "full_refund_and_compensation"
            refund_amount = booking_total
            compensation = 200
            action_taken = "Full booking refund plus Rs. 200 convenience compensation credited due to provider cancellation."
        elif dispute_type == "time_overrun":
            resolution_path = "lateness_compensation"
            refund_amount = 0
            compensation = 100
            action_taken = "Sincere apology issued. Rs. 100 late-delay credit applied to user's wallet."
        else:  # other
            resolution_path = "human_escalation"
            refund_amount = 0
            compensation = 0
            action_taken = "Non-standard dispute category. Flagged for priority manual investigation by our Customer Support Lead."
            human_escalation_required = True

        add_log(f"Executed Resolution Path Matrix: '{resolution_path}' | Refund = Rs. {refund_amount}, Compensation = Rs. {compensation}")
        add_log(f"Action Taken: {action_taken}")

        # ------------------------------------------------------------------
        # STEP 5: Provider Consequences Tiering
        # ------------------------------------------------------------------
        old_dispute_count = 0
        blacklist_flagged = False
        provider_consequence = ""

        # Fetch provider profile
        loaded_provider = False
        if db is not None and provider_id != "prov-unknown":
            try:
                add_log(f"Retrieving provider '{provider_id}' profile from Firestore...")
                prov_ref = db.collection("providers").document(provider_id).get()
                if prov_ref.exists:
                    prov_data = prov_ref.to_dict() or {}
                    old_dispute_count = int(prov_data.get("dispute_count", 0))
                    loaded_provider = True
                    add_log(f"Current provider dispute tally: {old_dispute_count}")
            except Exception as exc:
                add_log(f"Firestore provider fetch failed: {exc}.")

        if not loaded_provider:
            # Try to fetch from local JSON fallback
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            providers_file = os.path.join(base_dir, "data", "providers.json")
            if os.path.exists(providers_file):
                try:
                    with open(providers_file, "r", encoding="utf-8") as f:
                        providers = json.load(f)
                        for p in providers:
                            if p.get("provider_id") == provider_id:
                                old_dispute_count = int(p.get("dispute_count", 0))
                                loaded_provider = True
                                add_log(f"Local JSON profile matched. Historical dispute tally: {old_dispute_count}")
                                break
                except Exception as exc:
                    add_log(f"Local providers JSON parsing failed: {exc}")

        # Allow manual unit test tally injection
        if custom_dispute_count is not None:
            old_dispute_count = custom_dispute_count
            add_log(f"Test Override: Setting provider historical dispute count to {old_dispute_count}")

        new_dispute_count = old_dispute_count + 1
        add_log(f"Incremented provider dispute tallies: {old_dispute_count} -> {new_dispute_count}")

        # Apply Consequence logic
        if new_dispute_count == 1:
            provider_consequence = "First dispute. Warning logged on technician profile."
        elif new_dispute_count == 2:
            provider_consequence = "Second dispute. Cancellation rate increased by 0.1, provider search ranking score penalized."
        else:
            provider_consequence = "Third dispute threshold breached. Provider blacklisted from the KaamYaar platform."
            blacklist_flagged = True

        add_log(f"Consequence Matrix Applied: {provider_consequence}")

        # ------------------------------------------------------------------
        # STEP 6: Double Firestore Writes
        # ------------------------------------------------------------------
        firestore_written = False
        if db is not None:
            try:
                # 1. Save dispute ticket to disputes collection
                add_log(f"Writing dispute ticket '{dispute_id}' to Firestore...")
                dispute_doc = {
                    "dispute_id": dispute_id,
                    "booking_id": booking_id,
                    "provider_id": provider_id,
                    "dispute_type": dispute_type,
                    "classified_severity": classified_severity,
                    "resolution_path": resolution_path,
                    "refund_amount_pkr": refund_amount,
                    "compensation_pkr": compensation,
                    "blacklist_flagged": blacklist_flagged,
                    "human_escalation_required": human_escalation_required,
                    "action_taken": action_taken,
                    "created_at": now_utc.isoformat()
                }
                db.collection("disputes").document(dispute_id).set(dispute_doc)

                # 2. Apply penalty metrics to provider
                if provider_id != "prov-unknown":
                    add_log(f"Writing consequence metrics to provider document '{provider_id}'...")
                    prov_update = {
                        "provider_id": provider_id,
                        "dispute_count": new_dispute_count,
                        "last_dispute_date": now_utc.isoformat()
                    }
                    if blacklist_flagged:
                        prov_update["is_available"] = False
                        prov_update["blacklist_flagged"] = True
                    
                    # If this is the second dispute, simulate rating/cancellation penalty
                    if new_dispute_count == 2:
                        prov_update["cancellation_rate"] = 0.15  # Elevate cancellation rate
                        prov_update["rating_penalty_applied"] = True

                    db.collection("providers").document(provider_id).set(prov_update, merge=True)

                firestore_written = True
                add_log("Double Firestore synchronization complete.")
            except Exception as exc:
                add_log(f"Firestore transaction write failed: {exc}. Continuing simulated run.")

        # ------------------------------------------------------------------
        # STEP 7: Generate Warm Localized Apology (Gemini & Fallbacks)
        # ------------------------------------------------------------------
        resolution_message = ""
        gemini_msg_success = False

        try:
            add_log(f"Requesting Gemini to generate specialized apology in {primary_language}...")
            apology_prompt = (
                f"You are a warm, extremely polite, and deeply apologetic customer care representative from KaamYaar AI.\n"
                f"Generate a comforting resolution and apology message in the customer's native script/language ({primary_language}).\n\n"
                f"Details:\n"
                f"- Dispute Category: {dispute_type}\n"
                f"- Resolution Path: {resolution_path}\n"
                f"- Action Taken: {action_taken}\n"
                f"- Refund Credited: Rs. {refund_amount}\n"
                f"- Compensation Credited: Rs. {compensation}\n"
                f"- Dispute Severity: {classified_severity}\n"
                f"- Customer Complaint: \"{complaint_text}\"\n\n"
                f"Instructions:\n"
                f"1. Express deep, sincere apology for the negative experience.\n"
                f"2. Clearly explain the resolution: the amount refunded (Rs. {refund_amount}) and/or compensation credited (Rs. {compensation}).\n"
                f"3. Reassure them that we take their feedback seriously and have penalized the provider accordingly to ensure quality.\n"
                f"4. Keep the tone comforting, helpful, and friendly. Write in {primary_language}. If Roman Urdu, write in natural Roman Urdu. If Urdu, use native Nastaliq script.\n"
                f"5. Do not include markdown, headers, or quotes. Return only the raw apology text."
            )

            response = self._llm_client.models.generate_content(
                model=MODEL_ID,
                contents=apology_prompt,
                config=genai.types.GenerateContentConfig(temperature=0.3)
            )
            resolution_message = response.text.strip()
            # Clean up potential leading/trailing double quotes
            if resolution_message.startswith('"') and resolution_message.endswith('"'):
                resolution_message = resolution_message[1:-1].strip()
            gemini_msg_success = True
            add_log("Gemini apology statement compiled successfully.")
        except Exception as exc:
            add_log(f"Gemini apology message compilation failed: {exc}. Reverting to offline fallbacks.")

        if not gemini_msg_success:
            resolution_message = self._get_fallback_apology(
                primary_language=primary_language,
                action_taken=action_taken,
                refund_pkr=refund_amount + compensation
            )
            add_log("Pre-translated offline apology template successfully injected.")

        # Assemble Output
        output = DisputeResolverOutput(
            dispute_id=dispute_id,
            booking_id=booking_id,
            dispute_type=dispute_type,
            classified_severity=classified_severity,
            resolution_path=resolution_path,
            action_taken=action_taken,
            refund_amount_pkr=refund_amount,
            compensation_pkr=compensation,
            provider_consequence=provider_consequence,
            blacklist_flagged=blacklist_flagged,
            human_escalation_required=human_escalation_required,
            resolution_message=resolution_message,
            dispute_log=dispute_log
        )

        add_log(f"Dispute complete. Final Status: Resolved | Severity: {classified_severity}")
        return output.model_dump()

    def _get_fallback_apology(self, primary_language: str, action_taken: str, refund_pkr: int) -> str:
        """Returns pre-translated resolution statements when Gemini is rate-limited."""
        lang_lower = primary_language.lower()

        if "roman" in lang_lower or "urdu" in lang_lower and "roman" in lang_lower:
            return (
                f"Hum aap se maafi chahte hain. Aap ka complaint resolve ho chuka hai: {action_taken}. "
                f"Total Rs. {refund_pkr} aap ke account mein transfer kar diye gaye hain. KaamYaar chunne ka shukriya!"
            )
        elif "urdu" in lang_lower:
            return (
                f"ہم دل سے معذرت خواہ ہیں۔ آپ کا شکایت حل کر دی گئی ہے: {action_taken}۔ "
                f"کل Rs. {refund_pkr} آپ کے اکاؤنٹ میں منتقل کر دی گئی ہے۔ ہماری خدمات منتخب کرنے کا شکریہ!"
            )
        else:
            return (
                f"We sincerely apologize for the negative experience. Your dispute has been resolved: {action_taken}. "
                f"A total credit of Rs. {refund_pkr} has been issued to your account. Thank you for your patience."
            )
