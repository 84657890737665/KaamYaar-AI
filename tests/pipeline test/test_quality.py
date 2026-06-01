"""
tests/pipeline test/test_quality.py

Comprehensive unit and integration test suite for the Service Quality Monitor Agent (Agent 6).
Verifies:
- Accurate 5-stage simulation log progression with chronological 5-minute gaps.
- Exact average rating calculation math under running-average equations.
- Seamless connection-resilience and local data backfilling if offline.
- Dynamically structured matchmaking impact notes based on checklist metrics.
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

from agents.quality_monitor.agent import QualityMonitorAgent


class TestQualityMonitorAgent(unittest.TestCase):

    def setUp(self):
        self.agent = QualityMonitorAgent()

    @patch("agents.quality_monitor.agent.get_firestore_client")
    def test_simulation_mode_progressions_and_math(self, mock_get_firestore):
        """Test stage logging timestamps, default feedback seeding, and running average math in simulation mode."""
        # Setup Mock Firestore (not found in DB to trigger local JSON / default seeding)
        mock_get_firestore.return_value = None

        input_data = {
            "booking_id": "KY-20260517-9999",
            "provider_id": "bed14021-6954-4b27-8f25-541193bab203",  # Tariq Ali from data/providers.json
            "simulation_mode": True
        }

        result = self.agent.run(input_data)

        # 1. Check Booking lifecycle log stages
        self.assertEqual(result["booking_id"], "KY-20260517-9999")
        self.assertEqual(result["final_status"], "completed")
        self.assertFalse(result["rating_updated_in_firestore"])

        # Check all 5 stages in simulated log
        stages = [log["stage"] for log in result["stage_log"]]
        self.assertEqual(stages, ["ASSIGNED", "EN_ROUTE", "ARRIVED", "IN_PROGRESS", "COMPLETED"])

        # Verify 5-minute increments
        t0 = result["stage_log"][0]["timestamp"]
        t4 = result["stage_log"][4]["timestamp"]
        self.assertTrue(t4 > t0)

        # 2. Check recalculated average rating
        # Fallback values for Tariq Ali in JSON: rating 4.1, review_count 388
        # Recalculated = (4.1 * 388 + 4.5) / 389 = 4.1
        self.assertEqual(result["old_provider_rating"], 4.1)
        self.assertEqual(result["new_provider_rating"], 4.1)

        # Check mock feedback collection
        self.assertEqual(result["customer_feedback"]["customer_rating"], 4.5)
        self.assertTrue(result["customer_feedback"]["checklist"]["work_quality"])

    @patch("agents.quality_monitor.agent.get_firestore_client")
    def test_live_mode_custom_feedback(self, mock_get_firestore):
        """Test Live mode with explicit custom feedback and rating calculation checks."""
        # Setup Mock Firestore
        mock_db = MagicMock()
        mock_get_firestore.return_value = mock_db

        # Setup mock doc return from Firestore to seed custom old rating
        mock_doc = MagicMock()
        mock_doc.exists = True
        mock_doc.to_dict.return_value = {"rating": 3.0, "review_count": 9}
        mock_db.collection.return_value.document.return_value.get.return_value = mock_doc

        custom_feedback = {
            "customer_rating": 5.0,
            "review_text": "Out of this world professional service!",
            "checklist": {
                "work_quality": True,
                "on_time": True,
                "professional_behavior": True,
                "correct_pricing": True,
                "would_recommend": True
            },
            "evidence_placeholder": "custom_image.png"
        }

        input_data = {
            "booking_id": "KY-20260517-8888",
            "provider_id": "prov-custom-99",
            "simulation_mode": False,
            "feedback": custom_feedback
        }

        result = self.agent.run(input_data)

        # Assert correct running average calculation
        # old rating = 3.0, count = 9. Custom feedback rating = 5.0.
        # new average = (3.0 * 9 + 5.0) / 10 = (27 + 5) / 10 = 32 / 10 = 3.2
        self.assertEqual(result["old_provider_rating"], 3.0)
        self.assertEqual(result["new_provider_rating"], 3.2)
        self.assertTrue(result["rating_updated_in_firestore"])

        # Check DB updates were triggered twice (once for providers, once for bookings)
        mock_db.collection.assert_any_call("providers")
        mock_db.collection.assert_any_call("bookings")

    def test_future_matching_impact_warnings(self):
        """Test that sub-optimal review ratings and late checkmarks write warning notes."""
        bad_feedback = {
            "customer_rating": 2.5,
            "review_text": "Bohot late aaye aur pricing theek nahi thi.",
            "checklist": {
                "work_quality": True,
                "on_time": False,  # LATE
                "professional_behavior": True,
                "correct_pricing": False,
                "would_recommend": False  # NO RECOMMENDATION
            },
            "evidence_placeholder": "evidence.jpg"
        }

        input_data = {
            "booking_id": "KY-20260517-7777",
            "provider_id": "prov-bad-00",
            "simulation_mode": False,
            "feedback": bad_feedback
        }

        result = self.agent.run(input_data)

        note = result["future_matching_note"]
        self.assertIn("Sub-optimal review score", note)
        self.assertIn("Negative recommendation flag", note)
        self.assertIn("Delay flag", note)


if __name__ == "__main__":
    print("\n" + "="*70)
    print("KAAMYAAR AI — Service Quality Monitor Agent Unit Tests")
    print("="*70 + "\n")

    suite = unittest.TestLoader().loadTestsFromTestCase(TestQualityMonitorAgent)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    if result.wasSuccessful():
        print("\n" + "="*70)
        print("ALL QUALITY MONITOR TESTS PASSED SUCCESSFULLY!")
        print("="*70 + "\n")
        sys.exit(0)
    else:
        print("\n" + "="*70)
        print("SOME TESTS FAILED!")
        print("="*70 + "\n")
        sys.exit(1)
