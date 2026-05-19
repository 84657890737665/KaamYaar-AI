import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.routers import parse_request, find_providers, rank_providers, pricing, booking, quality, disputes, mobile_api, admin, provider_verification, time_estimation, safety_timer, emergency_alert, safety, calling
from app.middleware.tracing import TracingMiddleware
from app.services.firestore_service import firestore_service

# Proper logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup Event
    logger.info("Starting up KaamYaar Backend application...")
    
    # Initialize Firestore connection on startup if not already connected
    if firestore_service.db is None:
        logger.info("Attempting to connect to Firestore during startup...")
        firestore_service._initialize_with_retries()
        
    if firestore_service.db is not None:
        logger.info("Firestore connection verified on startup.")
    else:
        logger.warning("Firestore connection failed on startup. Application will use fallback mechanisms.")
        
    yield
    
    # Shutdown Event
    logger.info("Shutting down KaamYaar Backend application...")
    # If there were active connections to cleanly close, they would be handled here.
    logger.info("Cleanup complete.")

app = FastAPI(
    title=settings.project_name,
    description="FastAPI backend for KaamYaar AI Service Orchestrator",
    version="1.0.0",
    lifespan=lifespan
)

# Add Tracing Middleware
app.add_middleware(TracingMiddleware)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Versioning prefix
api_prefix = "/api/v1"

# Include all routers with API version prefix
app.include_router(parse_request.router, prefix=api_prefix)
app.include_router(find_providers.router, prefix=api_prefix)
app.include_router(rank_providers.router, prefix=api_prefix)
app.include_router(pricing.router, prefix=api_prefix)
app.include_router(booking.router, prefix=api_prefix)
app.include_router(quality.router, prefix=api_prefix)
app.include_router(disputes.router, prefix=api_prefix)
app.include_router(mobile_api.router, prefix=api_prefix)
app.include_router(admin.router, prefix=api_prefix)
app.include_router(provider_verification.router, prefix=api_prefix)
app.include_router(time_estimation.router, prefix=api_prefix)
app.include_router(safety_timer.router, prefix=api_prefix)
app.include_router(emergency_alert.router, prefix=api_prefix)
app.include_router(safety.router, prefix=api_prefix)
app.include_router(calling.router, prefix=api_prefix)

# Mount Dashboard Static Files
app.mount("/dashboard", StaticFiles(directory="dashboard", html=True), name="dashboard")

@app.get("/health", tags=["health"])
def health_check():
    """
    Health check endpoint to verify API and Firestore connection status.
    """
    is_connected = firestore_service.db is not None
    db_status = "connected" if is_connected else "disconnected"
    
    response_data = {
        "status": "ok" if is_connected else "degraded", 
        "service": "kaamyaar-backend", 
        "database": db_status
    }
    
    # Return 200 OK even if DB is down to signify API is responsive, 
    # but indicate 'degraded' status. Alternatively, 503 can be used for strict liveness checks.
    status_code = status.HTTP_200_OK if is_connected else status.HTTP_503_SERVICE_UNAVAILABLE
    
    return JSONResponse(status_code=status_code, content=response_data)
