"""
tests/pipeline test/test_dispute.py

Comprehensive unit and integration test suite for the Dispute & Escalation Resolver Agent (Agent 7).
Verifies:
- Accurate refund percentages and wallet compensation PKRs for each dispute type.
- Exact tier consequence logic (1st warning, 2nd search penalty, 3rd blacklisting).
- Seamless Firestore resilience when offline or credentials are missing.
- Pre-translated apology message overrides under simulated Gemini rate-limits.
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

from agents.dispute_resolver.agent import DisputeResolverAgent


class TestDisputeResolverAgent(unittest.TestCase):

    @patch("agents.dispute_resolver.agent.get_firestore_client")
    def setUp(self, mock_get_firestore):
        mock_get_firestore.return_value = None
        self.agent = DisputeResolverAgent()

    @patch("agents.dispute_resolver.agent.get_firestore_client")
    @patch("google.genai.Client")
    def test_no_show_resolution_and_severity_classification(self, mock_client, mock_get_firestore):
        """Test 'no_show' yields 100% refund, high severity, warning logged, and Gemini localized message."""
        mock_get_firestore.return_value = None

        # Mock Gemini Client returns for severity and apology message
        mock_sev_response = MagicMock()
        mock_sev_response.text = "high"
        mock_apology_response = MagicMock()
        mock_apology_response.text = "We are deeply sorry for the no-show. A full refund of Rs. 1500 has been credited to your account."
        
        mock_client.return_value.models.generate_content.side_effect = [
            mock_sev_response,
            mock_apology_response
        ]

        # Explicitly set the mocked client inside the agent
        self.agent._llm_client = mock_client.return_value

        input_data = {
            "booking_id": "KY-20260518-1234",
            "dispute_type": "no_show",
            "complaint_text": "The provider didn't show up today. I waited for two hours.",
            "provider_dispute_count": 0  # First dispute
        }

        result = self.agent.run(input_data)

        self.assertEqual(result["booking_id"], "KY-20260518-1234")
        self.assertEqual(result["dispute_type"], "no_show")
        self.assertEqual(result["classified_severity"], "high")
        self.assertEqual(result["refund_amount_pkr"], 1500)
        self.assertEqual(result["compensation_pkr"], 0)
        self.assertIn("Warning logged", result["provider_consequence"])
        self.assertFalse(result["blacklist_flagged"])
        self.assertFalse(result["human_escalation_required"])
        self.assertEqual(result["resolution_message"], "We are deeply sorry for the no-show. A full refund of Rs. 1500 has been credited to your account.")
        self.assertTrue(len(result["dispute_log"]) > 0)

    @patch("agents.dispute_resolver.agent.get_firestore_client")
    @patch("google.genai.Client")
    def test_quality_complaint_partial_refund_and_fallbacks(self, mock_client, mock_get_firestore):
        """Test 'quality_complaint' yields 30% refund, re-service, and triggers offline Roman Urdu fallback on rate limit."""
        mock_get_firestore.return_value = None

        # Simulate Gemini API quota failure for both calls (throws ResourceExhausted)
        from google.api_core.exceptions import ResourceExhausted
        mock_client.return_value.models.generate_content.side_effect = Exception("Quota exceeded")
        self.agent._llm_client = mock_client.return_value

        # Test booking loaded context from mock Firestore
        mock_db = MagicMock()
        mock_get_firestore.return_value = mock_db
        mock_doc = MagicMock()
        mock_doc.exists = True
        mock_doc.to_dict.return_value = {
            "total_pkr": 2000,
            "provider_id": "prov-222",
            "provider_name": "Sajid AC",
            "language": "Roman Urdu"
        }
        mock_db.collection.return_value.document.return_value.get.return_value = mock_doc

        input_data = {
            "booking_id": "KY-20260518-5678",
            "dispute_type": "quality_complaint",
            "complaint_text": "AC ki cooling bilkul theek nahi hui, leak wese hi hai.",
            "provider_dispute_count": 1  # 2nd dispute -> count becomes 2
        }

        result = self.agent.run(input_data)

        # Assert correct partial refund math: 30% of Rs. 2000 = Rs. 600
        self.assertEqual(result["refund_amount_pkr"], 600)
        self.assertEqual(result["compensation_pkr"], 0)
        self.assertEqual(result["resolution_path"], "partial_refund_and_reservice")
        
        # Consequence penalty for 2nd dispute: cancel rate increase & warning
        self.assertIn("Second dispute", result["provider_consequence"])
        self.assertFalse(result["blacklist_flagged"])

        # Roman Urdu pre-translated apology statement injection check
        self.assertIn("Hum aap se maafi chahte hain", result["resolution_message"])
        self.assertIn("Total Rs. 600", result["resolution_message"])

    @patch("agents.dispute_resolver.agent.get_firestore_client")
    @patch("google.genai.Client")
    def test_provider_blacklist_consequence(self, mock_client, mock_get_firestore):
        """Test provider reaches 3rd dispute and is blacklisted."""
        mock_get_firestore.return_value = None
        mock_client.return_value.models.generate_content.side_effect = Exception("Offline")
        self.agent._llm_client = mock_client.return_value

        input_data = {
            "booking_id": "KY-20260518-9999",
            "dispute_type": "cancellation",
            "complaint_text": "Technician cancelled at the very last moment.",
            "provider_dispute_count": 2  # 3rd dispute -> count becomes 3
        }

        result = self.agent.run(input_data)

        self.assertEqual(result["refund_amount_pkr"], 1500)
        self.assertEqual(result["compensation_pkr"], 200)
        self.assertTrue(result["blacklist_flagged"])
        self.assertIn("blacklisted from the KaamYaar platform", result["provider_consequence"])

    @patch("agents.dispute_resolver.agent.get_firestore_client")
    @patch("google.genai.Client")
    def test_other_escalation_path(self, mock_client, mock_get_firestore):
        """Test 'other' category dispute results in human escalation flags."""
        mock_get_firestore.return_value = None
        mock_client.return_value.models.generate_content.side_effect = Exception("Offline")
        self.agent._llm_client = mock_client.return_value

        input_data = {
            "booking_id": "KY-20260518-0000",
            "dispute_type": "other",
            "complaint_text": "Random non-standard dispute complaint text.",
            "provider_dispute_count": 0
        }

        result = self.agent.run(input_data)

        self.assertTrue(result["human_escalation_required"])
        self.assertEqual(result["resolution_path"], "human_escalation")
        self.assertEqual(result["refund_amount_pkr"], 0)
        self.assertEqual(result["compensation_pkr"], 0)


if __name__ == "__main__":
    print("\n" + "="*70)
    print("KAAMYAAR AI — Dispute & Escalation Resolver Agent Unit Tests")
    print("="*70 + "\n")

    suite = unittest.TestLoader().loadTestsFromTestCase(TestDisputeResolverAgent)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    if result.wasSuccessful():
        print("\n" + "="*70)
        print("ALL DISPUTE RESOLVER TESTS PASSED SUCCESSFULLY!")
        print("="*70 + "\n")
        sys.exit(0)
    else:
        print("\n" + "="*70)
        print("SOME TESTS FAILED!")
        print("="*70 + "\n")
        sys.exit(1)
