from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

from app.services.dispute_resolver import dispute_resolver
from app.services.firestore_service import firestore_service
from app.models.dispute import Dispute

router = APIRouter(prefix="/disputes", tags=["disputes"])

class FileDisputeRequest(BaseModel):
    booking_id: str
    user_id: str
    reason: str
    evidence_urls: List[str] = []

class ResolveDisputeRequest(BaseModel):
    dispute_id: str
    resolution: str
    refund_amount: float = 0.0

@router.post("/file-dispute", response_model=Dict[str, Any])
def file_dispute(request: FileDisputeRequest):
    """
    Files a new dispute for a booking.
    """
    try:
        dispute = dispute_resolver.file_dispute(
            booking_id=request.booking_id,
            user_id=request.user_id,
            reason=request.reason,
            evidence_urls=request.evidence_urls
        )
        return {"status": "success", "dispute": dispute.to_dict()}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@router.get("/dispute-status/{dispute_id}", response_model=Dict[str, Any])
def get_dispute_status(dispute_id: str):
    """
    Retrieves the current status and details of a dispute.
    """
    dispute = firestore_service.get(Dispute.COLLECTION_NAME, dispute_id, Dispute)
    if not dispute:
        raise HTTPException(status_code=404, detail="Dispute not found")
    
    return dispute.to_dict()

@router.post("/analyze-dispute/{dispute_id}", response_model=Dict[str, Any])
async def analyze_dispute(dispute_id: str):
    """
    Triggers the AI agent to analyze a dispute and suggest a resolution.
    """
    try:
        analysis = await dispute_resolver.analyze_dispute(dispute_id)
        return {"status": "success", "analysis": analysis}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@router.post("/resolve-dispute", response_model=Dict[str, Any])
def resolve_dispute(request: ResolveDisputeRequest):
    """
    Resolves a dispute with a given resolution and optional refund.
    """
    try:
        dispute = dispute_resolver.resolve_dispute(
            dispute_id=request.dispute_id,
            resolution=request.resolution,
            refund_amount=request.refund_amount
        )
        return {"status": "success", "dispute": dispute.to_dict()}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
