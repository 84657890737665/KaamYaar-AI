from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
from app.services.firestore_service import firestore_service
from app.models.provider import Provider

router = APIRouter(tags=["Provider Verification"])

class UploadCNICRequest(BaseModel):
    provider_id: str
    cnic_front_base64: str
    cnic_back_base64: str

class VerifyFaceRequest(BaseModel):
    provider_id: str
    face_photo_base64: str

@router.post("/provider/upload-cnic")
async def upload_cnic(req: UploadCNICRequest):
    # Mocking storage URL generation
    cnic_front_url = f"https://storage.kaamyaar/cnic_front_{req.provider_id}.jpg"
    cnic_back_url = f"https://storage.kaamyaar/cnic_back_{req.provider_id}.jpg"
    
    # Update Firestore
    try:
        updated = firestore_service.update("providers", req.provider_id, {
            "cnic_front_url": cnic_front_url,
            "cnic_back_url": cnic_back_url,
            "verification_status": "pending"
        })
        if not updated:
            raise HTTPException(status_code=404, detail="Provider not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update provider: {str(e)}")
        
    return {
        "success": True,
        "cnic_front_url": cnic_front_url,
        "cnic_back_url": cnic_back_url,
        "message": "CNIC uploaded, pending verification"
    }

@router.post("/provider/verify-face")
async def verify_face(req: VerifyFaceRequest):
    # Mocking storage URL generation
    face_photo_url = f"https://storage.kaamyaar/face_{req.provider_id}.jpg"
    
    # Update Firestore
    try:
        updated = firestore_service.update("providers", req.provider_id, {
            "face_photo_url": face_photo_url,
            "is_face_verified": True,
            "verification_status": "verified"
        })
        if not updated:
            raise HTTPException(status_code=404, detail="Provider not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update provider: {str(e)}")
        
    return {
        "success": True,
        "face_photo_url": face_photo_url,
        "is_face_verified": True,
        "verification_status": "verified"
    }

@router.get("/provider/verified-only")
async def get_verified_only(
    user_gender: str = Query(..., description="User gender: male or female"),
    service_type: Optional[str] = Query(None, description="Optional service type filter")
):
    try:
        all_providers = firestore_service.get_all("providers", Provider)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch providers: {str(e)}")
        
    providers = []
    for p in all_providers:
        if service_type and p.service_type != service_type:
            continue
        providers.append(p)
    
    # Apply gender-based filtering logic
    filtered_providers = []
    verified_only_applied = False
    
    if user_gender.lower() == "female":
        verified_only_applied = True
        # Rule: If user_gender == "female" -> ONLY verified providers
        filtered_providers = [p for p in providers if p.is_cnic_verified is True]
    else:
        # Rule: If user_gender == "male" -> all providers (verified + unverified)
        filtered_providers = providers

    return {
        "providers": [p.to_dict() for p in filtered_providers],
        "total": len(filtered_providers),
        "filters_applied": {
            "verified_only": verified_only_applied,
            "user_gender": user_gender.lower()
        }
    }
