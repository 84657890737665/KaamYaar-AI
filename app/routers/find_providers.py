from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional
from app.services.maps_service import maps_service
from app.models.provider import Provider, Location, ProviderWithDistance
import firebase_admin
from firebase_admin import firestore
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/find-providers",
    tags=["find-providers"],
)

def get_db():
    try:
        firebase_admin.get_app()
    except ValueError:
        try:
            firebase_admin.initialize_app()
        except Exception as e:
            logger.error(f"Failed to initialize Firebase Admin: {e}")
            raise e
    return firestore.client()

class LocationInput(BaseModel):
    lat: float = Field(..., description="Latitude")
    lng: float = Field(..., description="Longitude")

class FindProvidersInput(BaseModel):
    service: str = Field(..., description="Service requested (e.g., 'AC repair')")
    location: LocationInput = Field(..., description="User coordinates")
    radius_km: float = Field(10.0, description="Search radius in kilometers")
    min_rating: Optional[float] = Field(None, description="Minimum provider rating")
    require_available: bool = Field(True, description="Filter only available providers")

@router.post("", response_model=List[ProviderWithDistance])
async def find_providers(request: FindProvidersInput):
    try:
        db = get_db()
    except Exception as e:
        logger.warning(f"Failed to connect to database: {str(e)}")
        db = None
    
    # 1. Query Firestore for providers matching the service type
    try:
        providers_ref = db.collection(Provider.COLLECTION_NAME)
        # Use exact match for service_type. If necessary, you could do partial matching in Python.
        query = providers_ref.where("service_type", "==", request.service)
        
        if request.require_available:
            query = query.where("availability", "==", True)
            
        docs = query.stream()
        providers = []
        for doc in docs:
            provider_data = doc.to_dict()
            provider = Provider.from_dict(doc.id, provider_data)
            
            # Apply rating filter in Python to avoid requiring a composite index in Firestore
            if request.min_rating is not None and provider.rating < request.min_rating:
                continue
                
            providers.append(provider)
            
    except Exception as e:
        logger.warning(f"Database query failed, using mock data: {str(e)}")
        from app.models.mock_data import MOCK_PROVIDERS
        
        # Use mock data and filter manually
        # Simple lowercase match on service name
        mock_service = request.service.lower()
        providers = [p for p in MOCK_PROVIDERS if mock_service in p.service_type.lower() or p.service_type.lower() in mock_service]
        
        if request.require_available:
            providers = [p for p in providers if p.availability]
            
        if request.min_rating is not None:
            providers = [p for p in providers if p.rating >= request.min_rating]
        
    # 2. Filter by radius and calculate distances
    results = []
    user_origin = f"{request.location.lat},{request.location.lng}"
    
    for provider in providers:
        provider_dest = f"{provider.location.lat},{provider.location.lng}"
        distance_data = maps_service.calculate_distance(user_origin, provider_dest)
        
        if distance_data:
            distance_meters = distance_data.get("distance_value", float('inf'))
            # Check if within radius
            if distance_meters <= request.radius_km * 1000:
                provider_with_distance = ProviderWithDistance(
                    **provider.model_dump(),
                    distance_text=distance_data["distance"],
                    distance_value=distance_meters,
                    duration_text=distance_data["duration"]
                )
                results.append(provider_with_distance)
                
    # 3. Sort by distance
    results.sort(key=lambda p: p.distance_value)
    
    return results
