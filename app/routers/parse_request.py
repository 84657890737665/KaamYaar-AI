from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional
from app.config import settings
from google import genai
from google.genai import types
import json
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/parse-request",
    tags=["parse-request"],
)

class ParseRequestInput(BaseModel):
    raw_text: str = Field(..., description="The raw input text from the user.")
    language_hint: Optional[str] = Field("auto", description="Language hint, e.g., 'auto', 'en', 'ur', 'roman_ur'.")

class ParseRequestOutput(BaseModel):
    service: Optional[str] = Field(None, description="The requested service (e.g., 'AC technician', 'plumber').")
    location: Optional[str] = Field(None, description="The location mentioned in the request.")
    time: Optional[str] = Field(None, description="The requested time or timeframe.")
    urgency: Optional[str] = Field(None, description="Urgency level (e.g., 'urgent', 'normal').")
    budget: Optional[str] = Field(None, description="Budget mentioned, if any.")
    language: Optional[str] = Field(None, description="Detected language of the input.")
    confidence: float = Field(..., description="Confidence score of the parsing (0.0 to 1.0).")

@router.post("", response_model=ParseRequestOutput)
async def parse_request(request: ParseRequestInput):
    if not settings.gemini_api_key:
        logger.warning("Gemini API key is not configured. Falling back to mock data.")
        return ParseRequestOutput(
            service="AC technician",
            location="G-13",
            time=None,
            urgency="urgent",
            budget=None,
            language="auto",
            confidence=0.5
        )

    try:
        client = genai.Client(api_key=settings.gemini_api_key)
        
        system_instruction = (
            "You are an AI assistant for 'KaamYaar', an informal economy platform in Pakistan. "
            "Your task is to parse unstructured text requests for services and extract specific slots. "
            "The text can be in English, Urdu, or Roman Urdu. "
            "Extract the following information: "
            "- service: What service is the user asking for? "
            "- location: Where do they need the service? "
            "- time: When do they need it? "
            "- urgency: Is it urgent or normal? "
            "- budget: What is their budget? "
            "- language: What is the language of the request (English, Urdu, or Roman Urdu)? "
            "- confidence: Your confidence in this extraction as a float between 0.0 and 1.0. "
            "Respond ONLY with a valid JSON object matching the requested schema."
        )

        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=request.raw_text,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                response_mime_type="application/json",
                response_schema=ParseRequestOutput,
                temperature=0.1,
            )
        )
        
        parsed_data = json.loads(response.text)
        return ParseRequestOutput(**parsed_data)
        
    except Exception as e:
        logger.warning(f"Failed to parse request with Gemini: {str(e)}. Using fallback data.")
        return ParseRequestOutput(
            service="AC technician",
            location="G-13",
            time=None,
            urgency="urgent",
            budget=None,
            language="auto",
            confidence=0.5
        )
