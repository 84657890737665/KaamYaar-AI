from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Application Settings configuration.
    Uses pydantic-settings to validate and load variables from the environment or a .env file.
    """
    project_name: str = "KaamYaar AI Service Orchestrator"
    
    # Gemini API Key: Required for interacting with Gemini AI models for orchestration.
    gemini_api_key: Optional[str] = None
    
    # Google Maps API Key: Required for the maps_service (geocoding, distance matrix).
    google_maps_api_key: Optional[str] = None
    
    # Firebase Configuration: Required for Firebase Admin SDK initialization.
    firebase_project_id: Optional[str] = None
    firebase_private_key: Optional[str] = None
    firebase_client_email: Optional[str] = None
    
    # Cloud Run Service URL: Used when deployed to Google Cloud Run to identify the base URL.
    cloud_run_service_url: Optional[str] = None
    
    # Port: The port on which the FastAPI application will run. Default is 8000.
    port: int = 8000
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
