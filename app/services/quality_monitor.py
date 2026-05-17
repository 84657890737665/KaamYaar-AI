from typing import List, Dict, Any, Optional
import logging
from datetime import datetime, timezone
from fastapi import HTTPException, status
from app.services.firestore_service import firestore_service
from app.models.provider import Provider
from app.models.booking import Booking, BookingStatus

logger = logging.getLogger(__name__)

class QualityMonitorService:
    def __init__(self):
        self.db = firestore_service.db
        
    def _ensure_db(self):
        if self.db is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database connection not available"
            )

    async def track_enroute(self, booking_id: str, provider_location: Dict[str, float]) -> Dict[str, Any]:
        """
        Real-time location tracking simulation.
        Updates the booking's last_location.
        """
        self._ensure_db()
        
        try:
            booking_ref = self.db.collection(Booking.COLLECTION_NAME).document(booking_id)
            booking_doc = booking_ref.get()
            
            if not booking_doc.exists:
                raise HTTPException(status_code=404, detail="Booking not found")
                
            booking_data = booking_doc.to_dict()
            
            if booking_data.get("status") not in [BookingStatus.CONFIRMED.value, BookingStatus.IN_PROGRESS.value]:
                logger.warning(f"Tracking location for booking {booking_id} which is in status {booking_data.get('status')}")
            
            # Update booking with new location
            booking_ref.update({
                "last_location": provider_location,
                "updated_at": datetime.now(timezone.utc)
            })
            
            # Optionally update the provider's current location as well
            provider_id = booking_data.get("provider_id")
            if provider_id:
                provider_ref = self.db.collection(Provider.COLLECTION_NAME).document(provider_id)
                provider_ref.update({
                    "location": provider_location
                })
            
            return {
                "status": "success",
                "message": "Location updated successfully",
                "booking_id": booking_id,
                "location": provider_location
            }
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error tracking enroute for booking {booking_id}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to track location: {str(e)}")

    async def collect_feedback(
        self, 
        booking_id: str, 
        rating: int, 
        review_text: str, 
        photo_urls: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Validates rating 1-5, Stores feedback in Firestore, Triggers provider rating recalculation.
        """
        self._ensure_db()
        
        if not 1 <= rating <= 5:
            raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
            
        photo_urls = photo_urls or []
        
        try:
            booking_ref = self.db.collection(Booking.COLLECTION_NAME).document(booking_id)
            booking_doc = booking_ref.get()
            
            booking_data = None
            if booking_doc.exists:
                booking_data = booking_doc.to_dict()
            else:
                try:
                    from app.models.mock_data import MOCK_BOOKINGS
                    for b in MOCK_BOOKINGS:
                        if b.id == booking_id:
                            booking_data = b.model_dump()
                            break
                except ImportError:
                    pass

            if not booking_data:
                raise HTTPException(status_code=404, detail="Booking not found")
            provider_id = booking_data.get("provider_id")
            user_id = booking_data.get("user_id")
            
            # Store feedback in Firestore
            feedback_ref = self.db.collection("feedback").document()
            feedback_data = {
                "id": feedback_ref.id,
                "booking_id": booking_id,
                "provider_id": provider_id,
                "user_id": user_id,
                "rating": rating,
                "review_text": review_text,
                "photo_urls": photo_urls, # Firebase Storage placeholder URLs
                "created_at": datetime.now(timezone.utc)
            }
            feedback_ref.set(feedback_data)
            
            # Trigger provider rating recalculation
            if provider_id:
                await self.update_provider_rating(provider_id, new_rating=rating)
                
            return {
                "status": "success",
                "message": "Feedback submitted successfully",
                "feedback_id": feedback_ref.id
            }
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error collecting feedback for booking {booking_id}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to collect feedback: {str(e)}")

    async def update_provider_rating(self, provider_id: str, new_rating: Optional[float] = None) -> Dict[str, Any]:
        """
        Recalculates weighted average rating, updates on_time_score and cancellation_rate.
        Formula: new_rating = (old_rating * total_jobs + new_rating) / (total_jobs + 1)
        """
        self._ensure_db()
        
        try:
            provider_ref = self.db.collection(Provider.COLLECTION_NAME).document(provider_id)
            provider_doc = provider_ref.get()
            
            provider_data = None
            if provider_doc.exists:
                provider_data = provider_doc.to_dict()
            else:
                # Fallback to mock data
                import json
                import os
                
                try:
                    from app.models.mock_data import MOCK_PROVIDERS
                    for p in MOCK_PROVIDERS:
                        if p.id == provider_id:
                            provider_data = p.model_dump()
                            break
                except ImportError:
                    pass
                
                if not provider_data:
                    try:
                        json_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "providers.json")
                        if os.path.exists(json_path):
                            with open(json_path, "r", encoding="utf-8") as f:
                                providers_json = json.load(f)
                                for p in providers_json:
                                    if p.get("id") == provider_id:
                                        provider_data = p
                                        break
                    except Exception as e:
                        logger.warning(f"Failed to read providers.json: {e}")

            if not provider_data:
                raise HTTPException(status_code=404, detail="Provider not found")
            current_rating = provider_data.get("rating", 0.0)
            total_jobs = provider_data.get("total_jobs", 0)
            
            update_data = {}
            
            # Calculate new rating if provided
            if new_rating is not None:
                updated_rating = (current_rating * total_jobs + new_rating) / (total_jobs + 1)
                update_data["rating"] = round(updated_rating, 2)
                update_data["total_jobs"] = total_jobs + 1
            
            # Update on_time_score and cancellation_rate based on history
            # Fetch past bookings for the provider
            bookings_query = self.db.collection(Booking.COLLECTION_NAME).where("provider_id", "==", provider_id).stream()
            bookings = [doc.to_dict() for doc in bookings_query]
            
            if bookings:
                total_bookings = len(bookings)
                completed_bookings = sum(1 for b in bookings if b.get("status") == BookingStatus.COMPLETED.value)
                cancelled_bookings = sum(1 for b in bookings if b.get("status") == BookingStatus.CANCELLED.value)
                
                # Mocking on-time logic since we don't have explicit arrival times in booking yet
                # We'll assume a high base on-time rate for completed bookings for demonstration
                on_time_count = completed_bookings  # Simplified logic
                
                if total_bookings > 0:
                    cancellation_rate = (cancelled_bookings / total_bookings) * 100
                    update_data["cancellation_rate"] = round(cancellation_rate, 2)
                    
                if completed_bookings > 0:
                    on_time_score = (on_time_count / completed_bookings) * 100
                    update_data["on_time_score"] = round(on_time_score, 2)

            if update_data:
                provider_ref.set(update_data, merge=True)
                
            return {
                "status": "success",
                "message": "Provider stats updated successfully",
                "provider_id": provider_id,
                "updates": update_data
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error updating rating for provider {provider_id}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to update provider stats: {str(e)}")

quality_monitor = QualityMonitorService()
