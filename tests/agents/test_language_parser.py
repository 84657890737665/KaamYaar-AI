"""
tests/agents/test_language_parser.py

Unit tests for the Pakistani Multilingual Language Parser Agent.
All Gemini API calls are mocked — no real network requests needed.

Run with:
    pytest tests/ -v
"""

import pytest
from unittest.mock import MagicMock, patch

from agents.language_parser import LanguageParserAgent
from agents.language_parser.schemas import (
    ParsedServiceRequest,
    UrgencyLevel,
    ScriptType,
    DetectedTone,
)


# ── Fixtures & helpers ─────────────────────────────────────────────────────────

MOCK_PARSED = ParsedServiceRequest(
    # Language analysis
    detected_languages=["Roman Urdu", "English"],
    primary_language="Roman Urdu",
    script_type=ScriptType.LATIN,
    normalized_text="Bhai mujhe abhi ek plumber chahiye. Pipe phoot gayi hai DHA Karachi mein. Budget 3000 rupay tak.",
    translated_english="Brother, I need a plumber right now. The pipe has burst in DHA Karachi. Budget up to 3000 rupees.",
    confidence_score=0.96,
    detected_tone=DetectedTone.URGENT,
    contains_code_switching=True,
    regional_dialect="Karachi Urdu",
    # Service slots
    service_type="plumber",
    location="DHA Karachi",
    urgency=UrgencyLevel.EMERGENCY,
    budget="3000 rupay",
    preferences=["abhi chahiye"],
    original_text="Bhai mujhe abhi ek plumber chahiye. Pipe phoot gayi hai DHA Karachi mein. Budget 3000 rupay tak.",
)


@pytest.fixture
def agent() -> LanguageParserAgent:
    """Return a LanguageParserAgent with a fully mocked Gemini client."""
    with patch("agents.language_parser.agent.get_gemini_client") as mock_factory:
        mock_client = MagicMock()
        mock_factory.return_value = mock_client

        mock_response = MagicMock()
        mock_response.text = MOCK_PARSED.model_dump_json()
        mock_client.models.generate_content.return_value = mock_response

        yield LanguageParserAgent()


# ── Tests ──────────────────────────────────────────────────────────────────────

class TestLanguageParserAgent:

    # ── Interface ──────────────────────────────────────────────────────────

    def test_run_returns_expected_keys(self, agent: LanguageParserAgent) -> None:
        result = agent.run({"text": "Bhai plumber chahiye."})
        assert "parsed_request" in result
        assert "raw_text" in result

    def test_parse_request_returns_model(self, agent: LanguageParserAgent) -> None:
        parsed = agent.parse_request("Bhai plumber chahiye.")
        assert isinstance(parsed, ParsedServiceRequest)

    def test_empty_text_raises_value_error(self, agent: LanguageParserAgent) -> None:
        with pytest.raises(ValueError, match="must not be empty"):
            agent.run({"text": "   "})

    def test_original_text_preserved_in_result(self, agent: LanguageParserAgent) -> None:
        raw = "Pipe leak ho rahi hai, help karo!"
        result = agent.run({"text": raw})
        assert result["raw_text"] == raw

    # ── Language Analysis fields ───────────────────────────────────────────

    def test_detected_languages_is_list(self, agent: LanguageParserAgent) -> None:
        parsed = agent.parse_request("test")
        assert isinstance(parsed.detected_languages, list)
        assert len(parsed.detected_languages) >= 1

    def test_primary_language_is_roman_urdu(self, agent: LanguageParserAgent) -> None:
        parsed = agent.parse_request("test")
        assert parsed.primary_language == "Roman Urdu"

    def test_script_type_is_latin(self, agent: LanguageParserAgent) -> None:
        parsed = agent.parse_request("test")
        assert parsed.script_type == ScriptType.LATIN

    def test_code_switching_detected(self, agent: LanguageParserAgent) -> None:
        parsed = agent.parse_request("test")
        assert parsed.contains_code_switching is True

    def test_confidence_score_in_range(self, agent: LanguageParserAgent) -> None:
        parsed = agent.parse_request("test")
        assert 0.0 <= parsed.confidence_score <= 1.0

    def test_detected_tone_valid(self, agent: LanguageParserAgent) -> None:
        parsed = agent.parse_request("test")
        assert isinstance(parsed.detected_tone, DetectedTone)

    def test_regional_dialect_is_set(self, agent: LanguageParserAgent) -> None:
        parsed = agent.parse_request("test")
        assert parsed.regional_dialect == "Karachi Urdu"

    def test_normalized_text_is_string(self, agent: LanguageParserAgent) -> None:
        parsed = agent.parse_request("test")
        assert isinstance(parsed.normalized_text, str) and len(parsed.normalized_text) > 0

    def test_translated_english_is_string(self, agent: LanguageParserAgent) -> None:
        parsed = agent.parse_request("test")
        assert isinstance(parsed.translated_english, str) and len(parsed.translated_english) > 0

    # ── Service Request Slots ──────────────────────────────────────────────

    def test_service_type_extracted(self, agent: LanguageParserAgent) -> None:
        parsed = agent.parse_request("test")
        assert parsed.service_type == "plumber"

    def test_location_extracted(self, agent: LanguageParserAgent) -> None:
        parsed = agent.parse_request("test")
        assert parsed.location == "DHA Karachi"

    def test_urgency_is_emergency(self, agent: LanguageParserAgent) -> None:
        parsed = agent.parse_request("test")
        assert parsed.urgency == UrgencyLevel.EMERGENCY

    def test_budget_extracted(self, agent: LanguageParserAgent) -> None:
        parsed = agent.parse_request("test")
        assert "3000" in parsed.budget

    def test_preferences_is_list(self, agent: LanguageParserAgent) -> None:
        parsed = agent.parse_request("test")
        assert isinstance(parsed.preferences, list)
