from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from pydantic import BaseModel
from typing import List, Optional

from app.middleware.auth import verify_firebase_token

router = APIRouter(tags=["Mobile API"])

class ParseVoiceRequest(BaseModel):
    audio_base64: str

class Location(BaseModel):
    lat: float
    lng: float

class NearbyProvidersRequest(BaseModel):
    location: Location
    radius_km: float = 5.0
    service_type: Optional[str] = None

class BookServiceRequest(BaseModel):
    provider_id: str
    service_type: str
    location: Location
    urgency: str = "standard"

@router.post("/mobile/parse-voice")
async def parse_voice(request: ParseVoiceRequest, uid: str = Depends(verify_firebase_token)):
    """
    Accepts base64 audio and returns parsed service request slots.
    Mocked for now as requested.
    """
    return {
        "status": "success",
        "slots": {
            "service_type": "plumber",
            "urgency": "high",
            "issue_description": "Leaking pipe in the kitchen"
        }
    }

@router.post("/mobile/nearby-providers")
async def get_nearby_providers(request: NearbyProvidersRequest, uid: str = Depends(verify_firebase_token)):
    """
    Optimized for map view. Returns a lightweight list of nearby providers.
    """
    mock_providers = [
        {"id": "prov1", "lat": request.location.lat + 0.01, "lng": request.location.lng + 0.01, "rating": 4.8, "service_type": request.service_type or "electrician"},
        {"id": "prov2", "lat": request.location.lat - 0.01, "lng": request.location.lng - 0.02, "rating": 4.5, "service_type": request.service_type or "plumber"}
    ]
    return {"status": "success", "providers": mock_providers}

@router.post("/mobile/book-service")
async def book_service(request: BookServiceRequest, uid: str = Depends(verify_firebase_token)):
    """
    One-tap booking with minimal payload.
    """
    return {
        "status": "success",
        "booking_id": "booking-mobile-12345",
        "provider_id": request.provider_id,
        "estimated_arrival": "15 mins"
    }

@router.get("/mobile/booking-status/{booking_id}")
async def get_booking_status(booking_id: str, uid: str = Depends(verify_firebase_token)):
    """
    Real-time status polling endpoint. Fast lookups.
    """
    return {
        "status": "success",
        "booking_id": booking_id,
        "current_state": "en_route",
        "provider_location": {"lat": 24.86, "lng": 67.00}
    }

@router.post("/mobile/upload-feedback-media")
async def upload_feedback_media(file: UploadFile = File(...), uid: str = Depends(verify_firebase_token)):
    """
    Multipart form for photo/video upload. Returns a Firebase Storage placeholder URL.
    """
    placeholder_url = f"https://firebasestorage.googleapis.com/v0/b/kaamyaar-placeholder.appspot.com/o/feedback%2F{file.filename}?alt=media"
    
    return {
        "status": "success",
        "media_url": placeholder_url
    }
