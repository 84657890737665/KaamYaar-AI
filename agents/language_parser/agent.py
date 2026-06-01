"""
agents/language_parser/agent.py

Pakistani Multilingual Language Parser Agent — Agent 1 of 7.

Goal    : Detect language, normalize text, translate to English, and extract
          structured service-request slots from multilingual Pakistani input.
Model   : Gemini 1.5 Flash
Inputs  : Raw user text (Urdu, Roman Urdu, English, Sindhi, Punjabi, Pashto,
          Balochi, Pahari/Hindko, Balti/Shina, or any mix thereof)
Outputs : ParsedServiceRequest (language analysis + service slots)
"""

import logging
import time

import google.genai as genai
from google.genai import types
from google.api_core.exceptions import ResourceExhausted

from agents.base import BaseAgent
from agents.language_parser.prompts import SYSTEM_PROMPT
from agents.language_parser.schemas import ParsedServiceRequest
from core.llm_client import get_gemini_client

logger = logging.getLogger(__name__)

MODEL_ID = "gemini-1.5-flash"


class LanguageParserAgent(BaseAgent):
    """
    Parses multilingual Pakistani service requests and returns:
      - Full language analysis (languages, script, normalization, translation,
        tone, code-switching, dialect, confidence)
      - Extracted service slots (type, location, urgency, budget, preferences)

    Uses Gemini Flash with native structured (JSON) output to guarantee
    a response that exactly matches the ParsedServiceRequest Pydantic schema.
    """

    name = "language_parser"

    def __init__(self) -> None:
        self._client: genai.Client = get_gemini_client()

    # ------------------------------------------------------------------
    # Public interface (BaseAgent contract)
    # ------------------------------------------------------------------

    def run(self, input_data: dict) -> dict:
        """
        Entry point conforming to the BaseAgent interface.

        Args:
            input_data: Must contain a "text" key with the raw service request.

        Returns:
            {
                "parsed_request": ParsedServiceRequest,
                "raw_text": str,
            }
        """
        raw_text: str = input_data.get("text", "")
        if not raw_text.strip():
            raise ValueError("input_data['text'] must not be empty.")

        parsed = self.parse_request(raw_text)
        return {
            "parsed_request": parsed,
            "raw_text": raw_text,
        }

    # ------------------------------------------------------------------
    # Core parsing method
    # ------------------------------------------------------------------

    def parse_request(self, text: str) -> ParsedServiceRequest:
        """
        Send `text` to Gemini Flash and return a fully validated
        ParsedServiceRequest with language analysis + service slots.

        Automatically falls back to alternative models in a chain on 429 rate limits.

        Args:
            text: Raw user input in any supported Pakistani language/dialect.

        Returns:
            ParsedServiceRequest with all fields populated.
        """
        logger.info(
            "[%s] Parsing input (%d chars): %s…",
            self.name,
            len(text),
            text[:60].replace("\n", " "),
        )

        FALLBACK_MODELS = [
            "gemini-2.0-flash",
            "gemini-2.0-flash-lite",
            "gemini-2.5-flash",
            "gemini-1.5-flash",
            "gemini-1.5-flash-8b",
        ]

        config = types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            response_mime_type="application/json",
            response_schema=ParsedServiceRequest,
            temperature=0.0,
        )

        response = None
        last_exception = None

        for model_id in FALLBACK_MODELS:
            logger.info("[%s] Attempting parsing with model: %s", self.name, model_id)
            try:
                response = self._client.models.generate_content(
                    model=model_id,
                    contents=text,
                    config=config,
                )
                logger.info("[%s] Success with model: %s", self.name, model_id)
                break
            except Exception as exc:
                exc_msg = str(exc)
                logger.warning(
                    "[%s] Model %s failed to parse: %s. Trying next fallback...",
                    self.name,
                    model_id,
                    exc_msg,
                )
                last_exception = exc
                continue

        if response is None:
            if last_exception:
                raise last_exception
            raise RuntimeError("All fallback models failed to generate content.")

        # Validate JSON response into our Pydantic model
        parsed = ParsedServiceRequest.model_validate_json(response.text)

        # Safety: ensure original_text is always the real input
        if not parsed.original_text:
            parsed = parsed.model_copy(update={"original_text": text})

        logger.info(
            "[%s] ✓ primary=%s | script=%s | code_switch=%s | "
            "service=%s | urgency=%s | tone=%s | confidence=%.2f",
            self.name,
            parsed.primary_language,
            parsed.script_type,
            parsed.contains_code_switching,
            parsed.service_type,
            parsed.urgency,
            parsed.detected_tone,
            parsed.confidence_score,
        )

        return parsed
