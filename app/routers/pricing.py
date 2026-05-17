from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import Dict, Any
from app.services.pricing_engine import PricingEngine, price_cache
from app.services.firestore_service import firestore_service
from app.models.provider import Provider
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    tags=["pricing"],
)

class CalculatePriceRequest(BaseModel):
    provider_id: str = Field(..., description="ID of the selected provider")
    distance_km: float = Field(..., description="Distance between user and provider in kilometers")
    urgency: str = Field("normal", description="Urgency tier: normal, urgent, emergency")
    complexity: str = Field("simple", description="Complexity tier: simple, moderate, complex")
    discount: str = Field("none", description="Discount type: none, first_booking, repeat_customer")

@router.post("/calculate-price", response_model=Dict[str, float])
async def calculate_price_endpoint(request: CalculatePriceRequest):
    # Check cache first
    cache_key = f"{request.provider_id}_{request.distance_km}_{request.urgency}_{request.complexity}_{request.discount}"
    cached_price = price_cache.get(cache_key)
    if cached_price is not None:
        logger.info(f"Returning cached price estimate for {cache_key}")
        return cached_price

    # Fetch provider
    provider = None
    try:
        # Try fetching from Firestore
        if firestore_service.db is not None:
            provider = firestore_service.get(Provider.COLLECTION_NAME, request.provider_id, Provider)
    except Exception as e:
        logger.warning(f"Failed to fetch provider from Firestore: {e}")
        
    if not provider:
        # Fallback to mock data
        from app.models.mock_data import MOCK_PROVIDERS
        provider = next((p for p in MOCK_PROVIDERS if p.id == request.provider_id), None)
        
        if not provider:
            import os
            import json
            try:
                json_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "providers.json")
                if os.path.exists(json_path):
                    with open(json_path, "r", encoding="utf-8") as f:
                        json_providers = json.load(f)
                        for p_data in json_providers:
                            if p_data.get("id") == request.provider_id:
                                provider = Provider(**p_data)
                                break
            except Exception as e:
                logger.warning(f"Failed to read from providers.json: {e}")
        
    if not provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Provider with ID {request.provider_id} not found"
        )

    user_request = {
        "urgency": request.urgency,
        "complexity": request.complexity,
        "discount": request.discount
    }

    price_breakdown = PricingEngine.calculate_price(
        provider=provider,
        user_request=user_request,
        distance_km=request.distance_km
    )

    # Save to cache
    price_cache.set(cache_key, price_breakdown)

    return price_breakdown
