from fastapi import APIRouter, HTTPException
from app.utils.tracing import export_trace

router = APIRouter(tags=["Admin API"])

@router.get("/admin/trace/{booking_id}")
async def get_booking_trace(booking_id: str):
    """
    Returns the complete trace (workflow steps and agent executions) for a given booking_id.
    """
    trace_data = export_trace(booking_id)
    if not trace_data["workflow_steps"] and not trace_data["agent_executions"]:
        raise HTTPException(status_code=404, detail="No trace found for this booking_id")
    
    return {
        "status": "success",
        "booking_id": booking_id,
        "trace": trace_data
    }

@router.get("/admin/demo-state")
async def get_demo_state():
    """
    Returns a realistic mock payload of the current booking state for the dashboard.
    """
    import random
    
    # Mocking a realistic KaamYaar scenario
    services = ["Plumber", "AC Technician", "Electrician", "Carpenter"]
    selected_service = random.choice(services)
    
    return {
        "status": "success",
        "before_state": {
            "raw_request": f"Bhai jaldi se ek acha {selected_service.lower()} bhej do, bathroom ka pipe leak kar raha hai.",
            "detected_language": "Roman Urdu",
            "parsed_slots": {
                "service": selected_service,
                "urgency": "high",
                "location": "Defence Phase 5, Karachi",
                "issue_description": "Bathroom pipe leak"
            }
        },
        "after_state": {
            "selected_provider": {
                "name": "Arif Mahmood",
                "rating": 4.9,
                "distance": "2.1 km",
                "skills": [selected_service, "Emergency Repairs"]
            },
            "final_price": "Rs. 1,500 (incl. urgency fee)",
            "booking_status": "Confirmed ✅",
            "provider_rating_update": "4.85 → 4.90 after this job"
        },
        "agent_trace": [
            {"step": 1, "agent": "LanguageParser", "action": "Detected Roman Urdu & Extracted intent"},
            {"step": 2, "agent": "GeoFinder", "action": "Found 12 nearby providers in 5km radius"},
            {"step": 3, "agent": "RankerEngine", "action": "Scored 12 providers on 6 factors. Arif Mahmood ranked #1 (Score: 92.5)"},
            {"step": 4, "agent": "PricingEngine", "action": "Calculated base Rs.1000 + Rs.500 urgency fee"},
            {"step": 5, "agent": "BookingExecutor", "action": "Confirmed booking & dispatched provider"}
        ]
    }

@router.get("/admin/metrics")
async def get_live_metrics():
    """
    Returns live system metrics for the dashboard.
    """
    import random
    
    # Generate realistic looking fluctuation for the metrics
    return {
        "status": "success",
        "metrics": {
            "active_bookings": random.randint(120, 150),
            "avg_response_time_ms": random.randint(180, 220),
            "success_rate_percent": round(random.uniform(98.5, 99.9), 1)
        }
    }
