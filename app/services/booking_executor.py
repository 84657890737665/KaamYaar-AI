import logging
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from google.cloud.firestore import Transaction, transactional

from app.services.firestore_service import firestore_service
from app.models.booking import Booking, BookingStatus, PriceBreakdown
from app.utils.tracing import log_workflow_step

logger = logging.getLogger(__name__)

class BookingExecutor:
    
    @staticmethod
    def create_booking(user_id: str, provider_id: str, price_breakdown: Dict[str, Any], service_details: Dict[str, Any]) -> Booking:
        booking_id = str(uuid.uuid4())
        
        before_state = {
            "action": "creation",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        booking_data = {
            "id": booking_id,
            "user_id": user_id,
            "provider_id": provider_id,
            "service_type": service_details.get("service_type", "General"),
            "status": BookingStatus.PENDING.value,
            "price_breakdown": price_breakdown,
            "before_state": before_state,
            "service_details": service_details,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        
        if firestore_service.db:
            doc_ref = firestore_service.db.collection(Booking.COLLECTION_NAME).document(booking_id)
            doc_ref.set(booking_data)
        else:
            logger.warning("Firestore not connected, generated mock booking data but did not save to DB.")
            
        log_workflow_step(
            step_name="Booking Created",
            booking_id=booking_id,
            metadata={
                "user_id": user_id,
                "provider_id": provider_id,
                "service_type": booking_data["service_type"]
            }
        )
            
        return Booking(**booking_data)

    @staticmethod
    def update_status(booking_id: str, new_status: str, location_update: Optional[Dict[str, float]] = None) -> Booking:
        if not firestore_service.db:
            raise Exception("Firestore connection required for state machine updates")
            
        doc_ref = firestore_service.db.collection(Booking.COLLECTION_NAME).document(booking_id)
        transaction = firestore_service.db.transaction()
        
        @transactional
        def _update_in_transaction(transaction: Transaction, doc_ref) -> Booking:
            snapshot = doc_ref.get(transaction=transaction)
            if not snapshot.exists:
                raise ValueError(f"Booking {booking_id} not found")
                
            data = snapshot.to_dict()
            data['id'] = doc_ref.id
            booking = Booking(**data)
            current_status = booking.status
            
            valid_transitions = {
                BookingStatus.PENDING: [BookingStatus.CONFIRMED, BookingStatus.CANCELLED],
                BookingStatus.CONFIRMED: [BookingStatus.IN_PROGRESS, BookingStatus.CANCELLED],
                BookingStatus.IN_PROGRESS: [BookingStatus.COMPLETED, BookingStatus.CANCELLED],
                BookingStatus.COMPLETED: [],
                BookingStatus.CANCELLED: []
            }
            
            try:
                new_status_enum = BookingStatus(new_status.upper())
            except ValueError:
                raise ValueError(f"Invalid status: {new_status}")
                
            if new_status_enum not in valid_transitions.get(current_status, []):
                raise ValueError(f"Invalid state transition from {current_status.value} to {new_status_enum.value}")
                
            update_data = {
                "status": new_status_enum.value,
                "updated_at": datetime.now(timezone.utc)
            }
            
            if location_update:
                update_data["last_location"] = location_update
                
            if new_status_enum == BookingStatus.COMPLETED:
                update_data["after_state"] = {
                    "action": "completion",
                    "final_location": location_update,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
                
            transaction.update(doc_ref, update_data)
            data.update(update_data)
            
            log_workflow_step(
                step_name=f"Status Updated to {new_status_enum.value}",
                booking_id=booking_id,
                metadata={
                    "previous_status": current_status.value,
                    "location_update": location_update is not None
                }
            )
            
            return Booking(**data)
            
        return _update_in_transaction(transaction, doc_ref)

    @staticmethod
    def simulate_fcm_notification(user_id: str, title: str, body: str) -> Dict[str, Any]:
        """Simulates sending an FCM notification to a user"""
        notification_id = str(uuid.uuid4())
        logger.info(f"FCM Notification sent to {user_id} - Title: '{title}', Body: '{body}' [ID: {notification_id}]")
        
        return {
            "sent": True,
            "notification_id": notification_id,
            "user_id": user_id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
