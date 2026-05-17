from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

from app.services.booking_executor import BookingExecutor
from app.models.booking import Booking

router = APIRouter(
    tags=["booking"],
)

class CreateBookingRequest(BaseModel):
    user_id: str = Field(..., description="ID of the user making the booking")
    provider_id: str = Field(..., description="ID of the selected provider")
    price_breakdown: Dict[str, Any] = Field(..., description="Price breakdown dictionary")
    service_details: Dict[str, Any] = Field(..., description="Details of the service requested")

class UpdateStatusRequest(BaseModel):
    booking_id: str = Field(..., description="ID of the booking to update")
    new_status: str = Field(..., description="New status (e.g. CONFIRMED, IN_PROGRESS, COMPLETED)")
    location_update: Optional[Dict[str, float]] = Field(None, description="Optional lat/lng location update")

@router.post("/create-booking", response_model=Booking)
async def create_booking_endpoint(request: CreateBookingRequest):
    try:
        booking = BookingExecutor.create_booking(
            user_id=request.user_id,
            provider_id=request.provider_id,
            price_breakdown=request.price_breakdown,
            service_details=request.service_details
        )
        
        # Simulate FCM Notification to provider
        BookingExecutor.simulate_fcm_notification(
            user_id=request.provider_id,
            title="New Booking Request",
            body=f"You have a new booking request for {request.service_details.get('service_type', 'service')}."
        )
        return booking
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/update-status", response_model=Booking)
async def update_status_endpoint(request: UpdateStatusRequest):
    try:
        booking = BookingExecutor.update_status(
            booking_id=request.booking_id,
            new_status=request.new_status,
            location_update=request.location_update
        )
        
        # Simulate FCM Notification to user
        BookingExecutor.simulate_fcm_notification(
            user_id=booking.user_id,
            title="Booking Status Update",
            body=f"Your booking status has been updated to {request.new_status}."
        )
        return booking
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
