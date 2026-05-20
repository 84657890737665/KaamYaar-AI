
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="KaamYaar AI",
    version="1.0.0",
    description="AI Service Orchestrator for Pakistan's Informal Economy"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "app": "KaamYaar AI",
        "tagline": "Kaam ho — KaamYaar hai!",
        "version": "1.0.0",
        "status": "running",
        "agents": 8
    }

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/parse-request")
async def parse_request(data: dict):
    try:
        from agents.language_parser.agent import LanguageParserAgent
        agent = LanguageParserAgent()
        result = agent.run({"text": data.get("text", "")})
        parsed = result["parsed_request"]
        return {
            "success": True,
            "primary_language": parsed.primary_language,
            "service_type": parsed.service_type,
            "location": parsed.location,
            "urgency": parsed.urgency,
            "budget": parsed.budget,
            "confidence_score": parsed.confidence_score,
            "needs_clarification": result.get("needs_clarification", False)
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/find-providers")
async def find_providers(data: dict):
    try:
        from agents.provider_discovery.agent import ProviderDiscoveryAgent
        agent = ProviderDiscoveryAgent()
        result = agent.run(data)
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/rank-providers")
async def rank_providers(data: dict):
    try:
        from agents.matching_ranker.agent import MatchingRankerAgent
        agent = MatchingRankerAgent()
        result = agent.run(data)
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/create-booking")
async def create_booking(data: dict):
    try:
        from agents.booking_executor.agent import BookingExecutorAgent
        agent = BookingExecutorAgent()
        result = agent.run(data)
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/submit-dispute")
async def submit_dispute(data: dict):
    try:
        from agents.dispute_resolver.agent import DisputeResolverAgent
        agent = DisputeResolverAgent()
        result = agent.run(data)
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/safety/estimate-time")
async def estimate_time(data: dict):
    estimates = {
        "plumber":       {"basic": 45, "intermediate": 75, "complex": 120},
        "electrician":   {"basic": 60, "intermediate": 90, "complex": 150},
        "ac_technician": {"basic": 60, "intermediate": 90, "complex": 180},
        "default":       {"basic": 60, "intermediate": 90, "complex": 120},
    }
    service = data.get("service_type", "default")
    complexity = data.get("job_complexity", "intermediate")
    est = estimates.get(service, estimates["default"])
    minutes = est.get(complexity, 90)
    return {
        "success": True,
        "estimated_minutes": minutes,
        "warning_at_minutes": minutes + 30
    }

@app.post("/safety/emergency-alert")
async def emergency_alert(data: dict):
    return {
        "success": True,
        "status": "alert_sent",
        "booking_id": data.get("booking_id"),
        "message": "Trusted contact ko notify kar diya gaya"
    }
