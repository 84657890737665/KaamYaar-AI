"""
agents/language_parser/schemas.py

Pydantic models defining the structured output for the
Multilingual Pakistani Language Parser Agent.

Supported languages:
    Urdu, Roman Urdu, English, Sindhi, Punjabi, Pashto,
    Balochi, Pahari/Hindko, Balti/Shina

Gemini is constrained to respond with JSON conforming to
ParsedServiceRequest.
"""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


# ── Enumerations ──────────────────────────────────────────────────────────────

class UrgencyLevel(str, Enum):
    """How urgently the service is needed."""
    LOW       = "low"
    MEDIUM    = "medium"
    HIGH      = "high"
    EMERGENCY = "emergency"


class ScriptType(str, Enum):
    """Writing system detected in the input."""
    URDU_NASTALIQ = "urdu_nastaliq"   # Native Urdu/Arabic script
    LATIN         = "latin"           # Roman/English letters only
    MIXED         = "mixed"           # Both scripts in same message
    ARABIC        = "arabic"          # Pure Arabic script (rare)
    OTHER         = "other"


class DetectedTone(str, Enum):
    """Emotional tone / register of the message."""
    URGENT      = "urgent"
    FRUSTRATED  = "frustrated"
    POLITE      = "polite"
    NEUTRAL     = "neutral"
    DISTRESSED  = "distressed"
    CASUAL      = "casual"
    FORMAL      = "formal"


class SupportedLanguage(str, Enum):
    """Pakistani regional languages and dialects this agent handles."""
    URDU        = "Urdu"
    ROMAN_URDU  = "Roman Urdu"
    ENGLISH     = "English"
    SINDHI      = "Sindhi"
    PUNJABI     = "Punjabi"
    PASHTO      = "Pashto"
    BALOCHI     = "Balochi"
    PAHARI      = "Pahari/Hindko"
    BALTI_SHINA = "Balti/Shina"
    MIXED       = "Mixed"


# ── Main Output Schema ────────────────────────────────────────────────────────

class ParsedServiceRequest(BaseModel):
    """
    Full structured output from the Pakistani Multilingual Language Parser.

    Combines language analysis fields with extracted service-request slots
    so downstream agents receive everything they need in a single object.
    """

    # ── Language Analysis ──────────────────────────────────────────────────

    detected_languages: list[str] = Field(
        description=(
            "All languages identified in the input, ordered by prominence. "
            "Use values from SupportedLanguage enum where possible, "
            "e.g. ['Roman Urdu', 'English']."
        ),
    )

    primary_language: str = Field(
        description=(
            "The dominant language of the request "
            "(e.g. 'Roman Urdu', 'Urdu', 'Punjabi')."
        ),
    )

    script_type: ScriptType = Field(
        description=(
            "Writing system used: 'urdu_nastaliq', 'latin', 'mixed', 'arabic', or 'other'."
        ),
    )

    normalized_text: str = Field(
        description=(
            "Cleaned version of the input: typos corrected, abbreviations expanded, "
            "informal/SMS spellings standardised, but original language preserved."
        ),
    )

    translated_english: str = Field(
        description=(
            "Full, natural English translation of the normalised text. "
            "Preserve the original intent, tone, and nuance."
        ),
    )

    confidence_score: float = Field(
        ge=0.0,
        le=1.0,
        description=(
            "Model's confidence in the language detection and slot extraction, "
            "between 0.0 (very uncertain) and 1.0 (very confident)."
        ),
    )

    detected_tone: DetectedTone = Field(
        description=(
            "Emotional tone of the message: urgent, frustrated, polite, neutral, "
            "distressed, casual, or formal."
        ),
    )

    contains_code_switching: bool = Field(
        description=(
            "True if the user mixed two or more languages within the same sentence "
            "or message (common in Pakistani conversational text)."
        ),
    )

    regional_dialect: Optional[str] = Field(
        default=None,
        description=(
            "Specific regional dialect or variation detected "
            "(e.g. 'Lahori Punjabi', 'Karachi Urdu', 'Peshawar Pashto'). "
            "Null if not determinable."
        ),
    )

    # ── Service Request Slots ──────────────────────────────────────────────

    service_type: Optional[str] = Field(
        default=None,
        description=(
            "Type of service being requested "
            "(e.g. 'plumber', 'electrician', 'house cleaning', 'AC repair')."
        ),
    )

    location: Optional[str] = Field(
        default=None,
        description=(
            "Location or area where the service is needed "
            "(e.g. 'DHA Karachi', 'Model Town Lahore', 'G-10 Islamabad')."
        ),
    )

    urgency: Optional[UrgencyLevel] = Field(
        default=None,
        description=(
            "Inferred urgency level: low, medium, high, or emergency. "
            "Infer from context if not explicitly stated."
        ),
    )

    budget: Optional[str] = Field(
        default=None,
        description=(
            "Budget or price range mentioned "
            "(e.g. '2000 rupay', 'under 5k', 'zyada nahi hai')."
        ),
    )

    preferences: list[str] = Field(
        default_factory=list,
        description=(
            "Distinct preferences or requirements extracted from the message "
            "(e.g. ['mard technician nahi chahiye', 'aaj hi chahiye', 'genuine parts'])."
        ),
    )

    original_text: str = Field(
        description="The raw, unmodified input text exactly as received.",
    )
