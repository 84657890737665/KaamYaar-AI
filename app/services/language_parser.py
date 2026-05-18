import logging
import json
from typing import Optional
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from app.config import settings
from app.utils.language_detector import detect_language_fallback
from app.utils.tracing import trace_agent_execution, Timer

logger = logging.getLogger(__name__)

class ParseRequestOutput(BaseModel):
    service: Optional[str] = Field(None, description="The requested service (e.g., 'AC technician', 'plumber').")
    location: Optional[str] = Field(None, description="The location mentioned in the request.")
    time: Optional[str] = Field(None, description="The requested time or timeframe.")
    urgency: Optional[str] = Field(None, description="Urgency level (e.g., 'urgent', 'normal').")
    budget: Optional[str] = Field(None, description="Budget mentioned, if any.")
    language: Optional[str] = Field(None, description="Detected language of the input. Must be one of: urdu, roman_urdu, english, punjabi, sindhi, pashto, balochi, shina")
    language_confidence: float = Field(0.0, description="Confidence score of the detected language (0.0 to 1.0).")
    confidence: float = Field(..., description="Overall confidence score of the parsing (0.0 to 1.0).")

class LanguageParserService:
    def __init__(self):
        self.api_key = settings.gemini_api_key
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)
        else:
            self.client = None

    async def parse_request(self, text: str) -> ParseRequestOutput:
        if not self.client:
            logger.warning("Gemini API key is not configured. Falling back to mock data.")
            fallback_lang = detect_language_fallback(text)
            return ParseRequestOutput(
                service="AC technician",
                location="G-13",
                time=None,
                urgency="urgent",
                budget=None,
                language=fallback_lang,
                language_confidence=0.4,
                confidence=0.5
            )

        system_instruction = (
            "You are an AI assistant for 'KaamYaar', an informal economy platform in Pakistan. "
            "Your task is to parse unstructured text requests for services and extract specific slots. "
            "The text can be in any of these languages: English, Urdu, Roman Urdu, Punjabi, Sindhi, Pashto, Balochi, or Shina/Pahari. "
            "Extract the following information: "
            "- service: What service is the user asking for? "
            "- location: Where do they need the service? "
            "- time: When do they need it? "
            "- urgency: Is it urgent or normal? "
            "- budget: What is their budget? "
            "- language: What is the language of the request? (Must be one of: urdu, roman_urdu, english, punjabi, sindhi, pashto, balochi, shina) "
            "- language_confidence: Your confidence in the detected language as a float between 0.0 and 1.0. "
            "- confidence: Your overall confidence in this extraction as a float between 0.0 and 1.0. "
            "Respond ONLY with a valid JSON object matching the requested schema."
        )

        try:
            with Timer() as timer:
                response = self.client.models.generate_content(
                    model='gemini-2.0-flash',
                    contents=text,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    response_mime_type="application/json",
                    response_schema=ParseRequestOutput,
                    temperature=0.1,
                )
            )
            
            parsed_data = json.loads(response.text)
            
            # Validate language field
            valid_languages = ['urdu', 'roman_urdu', 'english', 'punjabi', 'sindhi', 'pashto', 'balochi', 'shina']
            if parsed_data.get('language') not in valid_languages:
                parsed_data['language'] = detect_language_fallback(text)
                parsed_data['language_confidence'] = 0.4
                
            
            result = ParseRequestOutput(**parsed_data)
            
            trace_agent_execution(
                agent_name="language_parser",
                input_data={"text": text},
                output_data=parsed_data,
                reasoning_steps=["Called gemini-2.0-flash", "Parsed JSON response"],
                latency=timer.elapsed_ms,
                confidence=result.confidence,
                booking_id=None # Pre-booking phase
            )
            
            return result
            
        except Exception as e:
            logger.warning(f"Failed to parse request with Gemini: {str(e)}. Using fallback data.")
            fallback_lang = detect_language_fallback(text)
            return ParseRequestOutput(
                service="AC technician",
                location="G-13",
                time=None,
                urgency="urgent",
                budget=None,
                language=fallback_lang,
                language_confidence=0.4,
                confidence=0.5
            )

language_parser = LanguageParserService()
