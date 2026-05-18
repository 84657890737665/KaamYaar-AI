import logging
import json
from typing import Optional, List, Dict, Any
from google import genai
from google.genai import types
from datetime import datetime, timezone
import uuid

from app.config import settings
from app.services.firestore_service import firestore_service
from app.models.dispute import Dispute, DisputeStatus, DisputePriority
from app.models.booking import Booking
from app.models.provider import Provider
from app.utils.tracing import trace_agent_execution, Timer

logger = logging.getLogger(__name__)

class DisputeResolverService:
    def __init__(self):
        self.api_key = settings.gemini_api_key
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)
        else:
            self.client = None

    def file_dispute(self, booking_id: str, user_id: str, reason: str, evidence_urls: List[str] = []) -> Dispute:
        # Fetch the booking to determine priority
        booking = firestore_service.get(Booking.COLLECTION_NAME, booking_id, Booking)
        if not booking:
            raise ValueError(f"Booking with ID {booking_id} not found.")

        # Determine priority based on booking total price
        total_price = booking.price_breakdown.total
        if total_price > 5000:
            priority = DisputePriority.HIGH
        elif total_price > 1000:
            priority = DisputePriority.MEDIUM
        else:
            priority = DisputePriority.LOW

        dispute_id = f"dispute-{uuid.uuid4().hex[:8]}"
        
        dispute = Dispute(
            id=dispute_id,
            booking_id=booking_id,
            user_id=user_id,
            reason=reason,
            evidence_urls=evidence_urls,
            status=DisputeStatus.OPEN,
            priority=priority,
            reasoning_audit_trail=[]
        )

        firestore_service.create(Dispute.COLLECTION_NAME, dispute.id, dispute.to_dict())
        logger.info(f"Created new dispute {dispute.id} for booking {booking_id} with priority {priority}")
        return dispute

    async def analyze_dispute(self, dispute_id: str) -> Dict[str, Any]:
        dispute = firestore_service.get(Dispute.COLLECTION_NAME, dispute_id, Dispute)
        if not dispute:
            raise ValueError(f"Dispute with ID {dispute_id} not found.")

        booking = firestore_service.get(Booking.COLLECTION_NAME, dispute.booking_id, Booking)
        provider = None
        if booking:
            try:
                if firestore_service.db is not None:
                    provider = firestore_service.get(Provider.COLLECTION_NAME, booking.provider_id, Provider)
            except Exception as e:
                logger.warning(f"Failed to fetch provider from Firestore: {e}")
            
            if not provider:
                # Fallback to mock data
                from app.models.mock_data import MOCK_PROVIDERS
                provider = next((p for p in MOCK_PROVIDERS if p.id == booking.provider_id), None)
                
                if not provider:
                    import os
                    try:
                        json_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "providers.json")
                        if os.path.exists(json_path):
                            with open(json_path, "r", encoding="utf-8") as f:
                                json_providers = json.load(f)
                                for p_data in json_providers:
                                    if p_data.get("id") == booking.provider_id:
                                        provider = Provider(**p_data)
                                        break
                    except Exception as e:
                        logger.warning(f"Failed to read from providers.json: {e}")
        # Update status to under review
        dispute.status = DisputeStatus.IN_REVIEW
        firestore_service.update(Dispute.COLLECTION_NAME, dispute.id, {"status": dispute.status})

        if not self.client:
            logger.warning("Gemini API key is not configured. Falling back to mock analysis.")
            analysis_result = {
                "suggested_resolution": "refund_50%",
                "confidence": 0.85,
                "reasoning": "Mock reasoning: based on standard policies, a 50% refund is suggested due to lack of API key for deep analysis."
            }
            self._append_audit_trail(dispute, analysis_result)
            return analysis_result

        # Prepare context for Gemini
        context = f"""
        Analyze the following dispute from an informal economy service platform (KaamYaar).
        
        Dispute Details:
        - Reason: {dispute.reason}
        - Priority: {dispute.priority}
        
        Booking Context:
        - Service Type: {booking.service_type if booking else 'Unknown'}
        - Total Price: {booking.price_breakdown.total if booking else 'Unknown'} PKR
        - Booking Status: {booking.status if booking else 'Unknown'}
        """

        if provider:
            context += f"""
            Provider Context:
            - Rating: {provider.rating}
            - Completed Jobs: {provider.total_jobs}
            - Cancellation Rate: {provider.cancellation_rate}%
            """

        system_instruction = (
            "You are an AI Dispute Resolution Agent for KaamYaar. "
            "Analyze the provided dispute and suggest a resolution. "
            "Return ONLY a JSON object with the following keys: "
            "1. 'suggested_resolution': A string indicating the action to take (e.g., 'refund_full', 'refund_50%', 'reject_dispute', 'provider_warning'). "
            "2. 'confidence': A float between 0.0 and 1.0 representing your confidence in this resolution. "
            "3. 'reasoning': A detailed string explaining why you reached this conclusion based on the context."
        )

        try:
            with Timer() as timer:
                response = self.client.models.generate_content(
                    model='gemini-2.0-flash',
                    contents=context,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        response_mime_type="application/json",
                        temperature=0.2,
                    )
                )
            analysis_result = json.loads(response.text)
            
            # Append to audit trail and save
            self._append_audit_trail(dispute, analysis_result)
            
            trace_agent_execution(
                agent_name="dispute_resolver",
                input_data={"context": context},
                output_data=analysis_result,
                reasoning_steps=["Called gemini-2.0-flash", "Parsed JSON resolution"],
                latency=timer.elapsed_ms,
                confidence=analysis_result.get("confidence", 0.0),
                booking_id=dispute.booking_id
            )
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Error analyzing dispute with Gemini: {str(e)}")
            fallback_result = {
                "suggested_resolution": "manual_review_required",
                "confidence": 0.0,
                "reasoning": f"Error calling AI: {str(e)}"
            }
            self._append_audit_trail(dispute, fallback_result)
            return fallback_result

    def _append_audit_trail(self, dispute: Dispute, result: Dict[str, Any]):
        audit_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "analysis": result
        }
        dispute.reasoning_audit_trail.append(audit_entry)
        firestore_service.update(
            Dispute.COLLECTION_NAME, 
            dispute.id, 
            {"reasoning_audit_trail": dispute.reasoning_audit_trail}
        )

    def resolve_dispute(self, dispute_id: str, resolution: str, refund_amount: float = 0.0) -> Dispute:
        dispute = firestore_service.get(Dispute.COLLECTION_NAME, dispute_id, Dispute)
        if not dispute:
            raise ValueError(f"Dispute with ID {dispute_id} not found.")

        dispute.status = DisputeStatus.RESOLVED
        dispute.resolution = resolution
        dispute.refund_amount = refund_amount

        update_data = {
            "status": dispute.status,
            "resolution": dispute.resolution,
            "refund_amount": dispute.refund_amount
        }
        
        firestore_service.update(Dispute.COLLECTION_NAME, dispute.id, update_data)

        # Update booking if there is a refund
        if refund_amount > 0:
            booking = firestore_service.get(Booking.COLLECTION_NAME, dispute.booking_id, Booking)
            if booking:
                # Calculate new total, ensuring it doesn't go below 0
                new_total = max(0.0, booking.price_breakdown.total - refund_amount)
                booking.price_breakdown.total = new_total
                
                # Update the booking
                firestore_service.update(
                    Booking.COLLECTION_NAME, 
                    booking.id, 
                    {"price_breakdown": booking.price_breakdown.model_dump()}
                )
                logger.info(f"Updated booking {booking.id} with refund {refund_amount}. New total: {new_total}")

        # Simulate FCM Notification
        logger.info(f"[FCM Simulation] Notifying User {dispute.user_id} and Provider about dispute resolution.")
        logger.info(f"[FCM Simulation] Dispute {dispute.id} resolved. Resolution: {resolution}. Refund: {refund_amount}")

        return dispute

dispute_resolver = DisputeResolverService()
