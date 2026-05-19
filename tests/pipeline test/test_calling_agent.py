import sys
from pathlib import Path
import unittest
from datetime import datetime, timezone, timedelta
from unittest.mock import MagicMock, patch

# Ensure UTF-8 output on Windows to prevent UnicodeEncodeError
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Add project root to sys.path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from agents.calling_agent.agent import CallingAgent


class TestCallingAgent(unittest.TestCase):

    def setUp(self):
        self.agent = CallingAgent()
        # Mock Gemini call script output
        self.agent._generate_transcript = lambda *args, **kwargs: "Mocked spoken Urdu transcript."
        
        # Base standard input data that passes trigger validation
        self.warning_time = (datetime.now(timezone.utc) - timedelta(minutes=45)).isoformat()
        self.current_time = datetime.now(timezone.utc).isoformat()
        
        self.base_inputs = {
            "booking_id": "KY-20260519-9988",
            "user_name": "Ayesha Khan",
            "user_location": "G-11 Islamabad",
            "provider_name": "Sajid Plumber",
            "provider_cnic": "37405-1234567-1",
            "provider_mobile": "0300-1234567",
            "trusted_contact_name": "Baji Amina",
            "trusted_contact_number": "0321-9876543",
            "service_type": "plumber",
            "booking_time": "10:00 AM",
            "estimated_minutes": 60,
            "minutes_exceeded": 45,
            
            # Triggers
            "user_responded": False,
            "provider_responded": False,
            "safety_mode": True,
            "warning_at_time": self.warning_time,
            "current_time": self.current_time
        }

    @patch("agents.calling_agent.agent.get_firestore_client")
    def test_calling_agent_successful_simulation(self, mock_get_firestore):
        """Test standard trigger conditions met: generates transcripts, logs calls, updates bookings."""
        mock_get_firestore.return_value = None  # Offline mode

        result = self.agent.run(self.base_inputs)
        
        # Conformance checks
        self.assertTrue(result["call_id"].startswith("CALL-"))
        self.assertTrue(result["call_sid"].startswith("KY-CALL-"))
        self.assertEqual(result["call_status"], "initiated")
        self.assertEqual(result["trusted_contact_name"], "Baji Amina")
        self.assertEqual(result["trusted_contact_number"], "0321-9876543")
        self.assertIn("Ayesha Khan", result["call_transcript"])
        self.assertIn("Sajid Plumber", result["call_transcript"])
        self.assertEqual(result["call_duration_seconds"], 45)
        self.assertFalse(result["firestore_logged"])
        self.assertFalse(result["booking_updated"])
        self.assertEqual(result["next_action"], "await_user_response")

    @patch("agents.calling_agent.agent.get_firestore_client")
    def test_calling_agent_escalate_to_authorities(self, mock_get_firestore):
        """Test that next_action escalates to authorities when minutes_exceeded is 60+."""
        mock_get_firestore.return_value = None
        
        inputs = self.base_inputs.copy()
        inputs["minutes_exceeded"] = 75
        
        result = self.agent.run(inputs)
        self.assertEqual(result["next_action"], "escalate_to_authorities")

    def test_validation_fails_safety_mode_inactive(self):
        """Verify validation failure when safety mode is inactive."""
        inputs = self.base_inputs.copy()
        inputs["safety_mode"] = False
        
        with self.assertRaises(ValueError) as ctx:
            self.agent.run(inputs)
        self.assertIn("safety_mode is False", str(ctx.exception))

    def test_validation_fails_time_not_exceeded(self):
        """Verify validation failure when warning time has elapsed less than 30 minutes."""
        inputs = self.base_inputs.copy()
        # warning was 10 minutes ago, not 30+
        warning_time = (datetime.now(timezone.utc) - timedelta(minutes=10)).isoformat()
        inputs["warning_at_time"] = warning_time
        
        with self.assertRaises(ValueError) as ctx:
            self.agent.run(inputs)
        self.assertIn("warning time has not been exceeded by 30+ minutes", str(ctx.exception))

    def test_validation_fails_user_responded(self):
        """Verify validation failure when customer has responded to warnings."""
        inputs = self.base_inputs.copy()
        inputs["user_responded"] = True
        
        with self.assertRaises(ValueError) as ctx:
            self.agent.run(inputs)
        self.assertIn("user has responded", str(ctx.exception))

    def test_validation_fails_provider_responded(self):
        """Verify validation failure when provider has responded to warnings."""
        inputs = self.base_inputs.copy()
        inputs["provider_responded"] = True
        
        with self.assertRaises(ValueError) as ctx:
            self.agent.run(inputs)
        self.assertIn("provider has responded", str(ctx.exception))


if __name__ == "__main__":
    print("\n" + "="*70)
    print("KAAMYAAR AI — Emergency Calling Agent (Agent 8) Unit & Validation Tests")
    print("="*70 + "\n")
    
    suite = unittest.TestLoader().loadTestsFromTestCase(TestCallingAgent)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    if result.wasSuccessful():
        print("\n" + "="*70)
        print("ALL EMERGENCY CALLING AGENT TESTS PASSED SUCCESSFULLY!")
        print("="*70 + "\n")
        sys.exit(0)
    else:
        print("\n" + "="*70)
        print("SOME TESTS FAILED!")
        print("="*70 + "\n")
        sys.exit(1)
