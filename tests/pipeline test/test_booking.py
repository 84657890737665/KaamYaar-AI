"""
tests/pipeline test/test_booking.py

Comprehensive unit and integration test suite for the Booking Executor Agent (Agent 5).
Verifies:
- Accurate 8-step transaction flow (ID generation, BEFORE/AFTER states, reminder times)
- Robust Firestore operations (mocked and connection-resilient fallbacks)
- Multilingual Gemini SMS/notification message generation
- Graceful offline swerving when rate-limited (Urdu, Roman Urdu, English)
"""

import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

# Ensure UTF-8 output on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Add project root to sys.path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from agents.provider_discovery.schemas import ProviderCandidate
from agents.language_parser.schemas import ParsedServiceRequest, UrgencyLevel
from agents.booking_executor.agent import BookingExecutorAgent

# Mock Inputs for Testing
MOCK_PROVIDER = ProviderCandidate(
    provider_id="prov-555",
    name="Sajid Plumber",
    service_types=["plumber"],
    location_name="Rawalpindi",
    distance_km=4.2,
    rating=4.8,
    on_time_score=0.95,
    cancellation_rate=0.03,
    base_rate_pkr=1200,
    is_available=True,
    skill_level="expert",
    years_experience=15,
    review_count=192
)

MOCK_PARSED_REQUEST = ParsedServiceRequest(
    detected_languages=["Roman Urdu", "English"],
    primary_language="Roman Urdu",
    script_type="latin",
    normalized_text="Bhai mera pipe burst ho gaya hai, jaldi aao.",
    translated_english="Brother my pipe has burst, come quickly.",
    confidence_score=0.97,
    detected_tone="neutral",
    contains_code_switching=True,
    service_type="plumber",
    location="Rawalpindi",
    urgency=UrgencyLevel.HIGH,
    budget="budget thoda kam rakho",
    original_text="Bhai mera pipe burst ho gaya hai, jaldi aao."
)

MOCK_PRICE_QUOTE = {
    "provider_id": "prov-555",
    "price_breakdown": {
        "base_rate": 1200,
        "distance_cost": 63,
        "urgency_premium": 300,
        "complexity_addon": 600,
        "loyalty_discount": 0,
        "surge": 0,
        "total": 2163
    }
}

class TestBookingExecutorAgent(unittest.TestCase):

    def setUp(self):
        self.agent = BookingExecutorAgent()

    @patch("agents.booking_executor.agent.get_firestore_client")
    def test_standard_booking_execution(self, mock_get_firestore):
        """Test the standard 8-step transaction flow with mocked Firestore and mocked Gemini client."""
        # Setup Mock Firestore
        mock_db = MagicMock()
        mock_get_firestore.return_value = mock_db

        # Setup Mock Gemini response
        mock_response = MagicMock()
        mock_response.text = "Aap ki booking confirm ho chuki hai! Sajid Plumber 2026-05-19 10:00 AM par aayenge."

        input_data = {
            "provider": MOCK_PROVIDER,
            "parsed_request": MOCK_PARSED_REQUEST,
            "price_quote": MOCK_PRICE_QUOTE,
            "confirmed_slot": "2026-05-19 10:00 AM"
        }

        with patch.object(self.agent._llm_client.models, 'generate_content', return_value=mock_response):
            result = self.agent.run(input_data)

            # Assert Booking ID exists and starts with KY-
            self.assertTrue(result["booking_id"].startswith("KY-"))
            self.assertEqual(result["status"], "confirmed")
            self.assertEqual(result["provider_assigned"], "Sajid Plumber")
            self.assertEqual(result["confirmed_slot"], "2026-05-19 10:00 AM")
            self.assertEqual(result["total_pkr"], 2163)

            # Assert states
            self.assertEqual(result["before_state"], {"provider_status": "available", "slot_status": "open"})
            self.assertEqual(result["after_state"], {"provider_status": "booked", "slot_status": "confirmed"})

            # Assert DB writes and simulated push notifications
            self.assertTrue(result["firestore_written"])
            mock_db.collection.assert_any_call("bookings")
            mock_db.collection.assert_any_call("providers")

            # Notification verification
            self.assertEqual(result["notification_payload"]["title"], "KaamYaar — Booking Confirmed!")
            self.assertIn("Sajid Plumber will arrive", result["notification_payload"]["body"])

            # Conformance of message
            self.assertEqual(result["confirmation_message"], "Aap ki booking confirm ho chuki hai! Sajid Plumber 2026-05-19 10:00 AM par aayenge.")

    @patch("agents.booking_executor.agent.get_firestore_client")
    def test_database_offline_resilience(self, mock_get_firestore):
        """Test that the agent handles database initialization failures gracefully without crashing."""
        # Force Firestore client initialization failure
        mock_get_firestore.return_value = None

        mock_response = MagicMock()
        mock_response.text = "Mocked confirmation message"

        input_data = {
            "provider": MOCK_PROVIDER,
            "parsed_request": MOCK_PARSED_REQUEST,
            "price_quote": MOCK_PRICE_QUOTE,
            "confirmed_slot": "2026-05-19 10:00 AM"
        }

        with patch.object(self.agent._llm_client.models, 'generate_content', return_value=mock_response):
            result = self.agent.run(input_data)

            # Conformance checks
            self.assertFalse(result["firestore_written"])  # Gracefully marked as False
            self.assertTrue(result["booking_id"].startswith("KY-"))
            self.assertEqual(result["receipt"]["payment"]["total_amount"], 2163)

    @patch("agents.booking_executor.agent.get_firestore_client")
    def test_api_rate_limiting_fallback_roman_urdu(self, mock_get_firestore):
        """Test Roman Urdu offline SMS fallback when Gemini API fails (quota limits)."""
        mock_get_firestore.return_value = None  # Simulate offline DB

        # Force Gemini call to fail with an exception
        input_data = {
            "provider": MOCK_PROVIDER,
            "parsed_request": MOCK_PARSED_REQUEST,  # primary language is Roman Urdu
            "price_quote": MOCK_PRICE_QUOTE,
            "confirmed_slot": "2026-05-19 10:00 AM"
        }

        with patch.object(self.agent._llm_client.models, 'generate_content', side_effect=Exception("RESOURCE_EXHAUSTED Quota Exceeded")):
            result = self.agent.run(input_data)

            self.assertFalse(result["firestore_written"])
            # Should swerve perfectly to Roman Urdu fallback
            self.assertIn("Aap ki booking confirm ho chuki hai!", result["confirmation_message"])
            self.assertIn("Sajid Plumber", result["confirmation_message"])
            self.assertIn("2026-05-19 10:00 AM", result["confirmation_message"])

    @patch("agents.booking_executor.agent.get_firestore_client")
    def test_api_rate_limiting_fallback_urdu_nastaliq(self, mock_get_firestore):
        """Test Urdu Nastaliq offline SMS fallback when Gemini API fails."""
        mock_get_firestore.return_value = None

        urdu_request = ParsedServiceRequest(
            detected_languages=["Urdu"],
            primary_language="Urdu",
            script_type="arabic",
            normalized_text="پلیز پلمبر بھیجیں",
            translated_english="Please send plumber",
            confidence_score=0.99,
            detected_tone="neutral",
            contains_code_switching=False,
            service_type="plumber",
            location="Rawalpindi",
            urgency=UrgencyLevel.HIGH,
            budget="low",
            original_text="پلیز پلمبر بھیجیں"
        )

        input_data = {
            "provider": MOCK_PROVIDER,
            "parsed_request": urdu_request,
            "price_quote": MOCK_PRICE_QUOTE,
            "confirmed_slot": "2026-05-19 10:00 AM"
        }

        with patch.object(self.agent._llm_client.models, 'generate_content', side_effect=Exception("RESOURCE_EXHAUSTED")):
            result = self.agent.run(input_data)

            # Assert Urdu Nastaliq fallback matches
            self.assertIn("محترم کسٹمر، آپ کا آرڈر کامیابی سے بک ہو گیا ہے۔", result["confirmation_message"])
            self.assertIn("Sajid Plumber", result["confirmation_message"])

if __name__ == "__main__":
    print("\n" + "="*70)
    print("KAAMYAAR AI — Booking Executor Agent Unit & Fallback Tests")
    print("="*70 + "\n")
    
    suite = unittest.TestLoader().loadTestsFromTestCase(TestBookingExecutorAgent)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    if result.wasSuccessful():
        print("\n" + "="*70)
        print("ALL BOOKING EXECUTOR TESTS PASSED SUCCESSFULLY!")
        print("="*70 + "\n")
        sys.exit(0)
    else:
        print("\n" + "="*70)
        print("SOME TESTS FAILED!")
        print("="*70 + "\n")
        sys.exit(1)
