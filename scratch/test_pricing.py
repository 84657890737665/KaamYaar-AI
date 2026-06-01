"""
tests/pipeline test/test_pricing.py

Unit and pipeline tests for Agent 4 — Dynamic Pricing Engine.
Runs through standard pricing scenarios, budget-sensitivity checks,
and mocks API rate limits to verify the robustness of offline fallbacks.
"""

import sys
import logging
from pathlib import Path
from unittest.mock import MagicMock, patch

# Ensure UTF-8 output on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Add project root to sys.path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from agents.provider_discovery.schemas import ProviderCandidate
from agents.language_parser.schemas import ParsedServiceRequest, UrgencyLevel
from agents.pricing_engine.agent import PricingEngineAgent

# Set up logging to display details
logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
logger = logging.getLogger("test_pricing")

# ── Mock Data for Testing ──────────────────────────────────────────────────────

# Primary candidate
MOCK_PROVIDER = ProviderCandidate(
    provider_id="p-101",
    name="Sajid Plumber",
    service_types=["plumber"],
    location_name="G-13 Islamabad",
    distance_km=4.2,
    rating=4.8,
    on_time_score=0.95,
    cancellation_rate=0.03,
    base_rate_pkr=1200,
    is_available=True,
    skill_level="expert",
    years_experience=8,
    review_count=42
)

# Budget-friendly alternative candidate
MOCK_ALT_PROVIDER = ProviderCandidate(
    provider_id="p-102",
    name="Asghar Ali Plumber",
    service_types=["plumber"],
    location_name="G-11 Islamabad",
    distance_km=6.0,
    rating=4.2,
    on_time_score=0.88,
    cancellation_rate=0.08,
    base_rate_pkr=800,
    is_available=True,
    skill_level="intermediate",
    years_experience=3,
    review_count=15
)

# Parsed service request (Standard, not budget sensitive, medium urgency)
MOCK_REQUEST_STANDARD = ParsedServiceRequest(
    detected_languages=["Roman Urdu", "English"],
    primary_language="Roman Urdu",
    script_type="latin",
    normalized_text="Plumber chahiye pani ka leak theek karne ke liye G-13 Islamabad mein.",
    translated_english="Need a plumber to fix water leak in G-13 Islamabad.",
    confidence_score=0.92,
    detected_tone="neutral",
    contains_code_switching=True,
    service_type="pipe burst",  # Complexity: 600
    location="G-13 Islamabad",
    urgency=UrgencyLevel.MEDIUM,  # Urgency premium: 0
    budget="under 3000",
    preferences=[],
    original_text="Plumber chahiye pani ka leak theek karne ke liye G-13 Islamabad mein."
)

# Parsed service request (Budget sensitive, high urgency)
MOCK_REQUEST_BUDGET = ParsedServiceRequest(
    detected_languages=["Urdu"],
    primary_language="Urdu",
    script_type="urdu_nastaliq",
    normalized_text="فوری پلمبر بھیجیں، بجٹ تھوڑا کم ہے۔",
    translated_english="Send a plumber urgently, budget is a bit low.",
    confidence_score=0.95,
    detected_tone="urgent",
    contains_code_switching=False,
    service_type="pipe burst",  # Complexity: 600
    location="G-13 Islamabad",
    urgency=UrgencyLevel.HIGH,  # Urgency premium: 300
    budget="thoda kam budget hai",  # Budget keywords matched
    preferences=[],
    original_text="فوری پلمبر بھیجیں، بجٹ تھوڑا کم ہے۔"
)


# ── Test Suite ─────────────────────────────────────────────────────────────────

def run_tests():
    print("\n" + "="*70)
    print("KAAMYAAR AI — Pricing Engine Agent Unit & Fallback Tests")
    print("="*70)

    agent = PricingEngineAgent()

    # ──────────────────────────────────────────────────────────────────────────
    # Test 1: Standard Non-Budget Calculation (Regular path)
    # ──────────────────────────────────────────────────────────────────────────
    print("\n[Test 1] Testing Standard Non-Budget Quote Calculation...")
    
    # We patch Gemini client to avoid rate limits during basic logic test
    with patch.object(agent._client.models, 'generate_content') as mock_gen:
        # Mock Gemini structured JSON response
        mock_response = MagicMock()
        mock_response.text = '{"price_explanation": "Aap ka total quote Rs. 1863 hai. Isme base rate Rs. 1200 hai aur distance charges Rs. 63 hain.", "tradeoff": null}'
        mock_gen.return_value = mock_response

        input_data = {
            "provider": MOCK_PROVIDER,
            "parsed_request": MOCK_REQUEST_STANDARD,
            "alternative_provider": MOCK_ALT_PROVIDER
        }

        output = agent.run(input_data)

        # Expected calculations:
        # base_rate = 1200
        # distance_cost = round(4.2 * 15) = 63
        # urgency_premium = 0 (medium urgency)
        # complexity_addon = 600 (pipe burst)
        # total = 1200 + 63 + 0 + 600 = 1863
        
        print(f"  ✓ Total calculated : Rs. {output['price_breakdown']['total']} (Expected: 1863)")
        print(f"  ✓ Distance charges : Rs. {output['price_breakdown']['distance_cost']} (Expected: 63)")
        print(f"  ✓ Complexity addon: Rs. {output['price_breakdown']['complexity_addon']} (Expected: 600)")
        print(f"  ✓ Budget Sensitive : {output['is_budget_sensitive']} (Expected: False)")
        print(f"  ✓ Alternative Quote: {output['budget_alternative']} (Expected: None)")
        print(f"  ✓ Explanation text : {output['price_explanation']}")
        
        assert output['price_breakdown']['total'] == 1863
        assert output['price_breakdown']['distance_cost'] == 63
        assert output['price_breakdown']['complexity_addon'] == 600
        assert output['is_budget_sensitive'] is False
        assert output['budget_alternative'] is None

    # ──────────────────────────────────────────────────────────────────────────
    # Test 2: Budget-Sensitive Calculation (Urgency premium + Budget Alternative)
    # ──────────────────────────────────────────────────────────────────────────
    print("\n[Test 2] Testing Budget-Sensitive Quote with Urgency + Alternative...")

    with patch.object(agent._client.models, 'generate_content') as mock_gen:
        mock_response = MagicMock()
        mock_response.text = (
            '{"price_explanation": "آپ کا کل تخمینہ 2163 روپے ہے۔", '
            '"tradeoff": "اصغر علی 1790 روپے میں دستیاب ہیں جس سے آپ کی بچت ہوگی، لیکن وہ 6.0 کلومیٹر دور ہیں۔"}'
        )
        mock_gen.return_value = mock_response

        input_data = {
            "provider": MOCK_PROVIDER,
            "parsed_request": MOCK_REQUEST_BUDGET,
            "alternative_provider": MOCK_ALT_PROVIDER
        }

        output = agent.run(input_data)

        # Expected primary calculations:
        # base_rate = 1200
        # distance_cost = round(4.2 * 15) = 63
        # urgency_premium = 300 (high urgency)
        # complexity_addon = 600 (pipe burst)
        # total = 1200 + 63 + 300 + 600 = 2163

        # Expected budget alternative calculations:
        # alt_base_rate = 800
        # alt_distance_cost = round(6.0 * 15) = 90
        # alt_total = 800 + 90 + 300 + 600 = 1790

        print(f"  ✓ Primary Total    : Rs. {output['price_breakdown']['total']} (Expected: 2163)")
        print(f"  ✓ Urgency Premium  : Rs. {output['price_breakdown']['urgency_premium']} (Expected: 300)")
        print(f"  ✓ Budget Sensitive : {output['is_budget_sensitive']} (Expected: True)")
        print(f"  ✓ Alternative Name : {output['budget_alternative']['provider_name']} (Expected: Asghar Ali Plumber)")
        print(f"  ✓ Alternative Total: Rs. {output['budget_alternative']['total']} (Expected: 1790)")
        print(f"  ✓ Tradeoff Text    : {output['budget_alternative']['tradeoff']}")

        assert output['price_breakdown']['total'] == 2163
        assert output['price_breakdown']['urgency_premium'] == 300
        assert output['is_budget_sensitive'] is True
        assert output['budget_alternative'] is not None
        assert output['budget_alternative']['total'] == 1790
        assert output['budget_alternative']['provider_name'] == "Asghar Ali Plumber"

    # ──────────────────────────────────────────────────────────────────────────
    # Test 3: Simulated Gemini API Rate-Limit Error (Graceful Offline Fallback)
    # ──────────────────────────────────────────────────────────────────────────
    print("\n[Test 3] Testing Rate-Limit Quota Exhaustion (Graceful Fallback)...")

    # Force raise rate-limit error (Exception) when generate_content is called
    with patch.object(agent._client.models, 'generate_content', side_effect=Exception("RESOURCE_EXHAUSTED Quota Limit")):
        input_data = {
            "provider": MOCK_PROVIDER,
            "parsed_request": MOCK_REQUEST_BUDGET, # Urdu
            "alternative_provider": MOCK_ALT_PROVIDER
        }

        # Run method (should NOT throw error, but catch and use Urdu fallbacks)
        output = agent.run(input_data)

        print(f"  ✓ Total calculated : Rs. {output['price_breakdown']['total']} (Expected: 2163)")
        print(f"  ✓ Budget Sensitive : {output['is_budget_sensitive']} (Expected: True)")
        print(f"  ✓ Explanation Text : {output['price_explanation']}")
        print(f"  ✓ Tradeoff Text    : {output['budget_alternative']['tradeoff']}")

        assert output['price_breakdown']['total'] == 2163
        assert "تخمینہ" in output['price_explanation'] or "بنیادی" in output['price_explanation']
        assert "بچا سکتے ہیں" in output['budget_alternative']['tradeoff'] or "ریٹنگ" in output['budget_alternative']['tradeoff']
        print("  ✓ Graceful Urdu offline fallback matched perfectly!")

        # Let's test with a Roman Urdu request to verify Roman Urdu fallbacks
        mock_roman_budget = MOCK_REQUEST_BUDGET.model_copy(update={"primary_language": "Roman Urdu"})
        output_roman = agent.run({
            "provider": MOCK_PROVIDER,
            "parsed_request": mock_roman_budget,
            "alternative_provider": MOCK_ALT_PROVIDER
        })
        print(f"  ✓ Roman Urdu Exp   : {output_roman['price_explanation']}")
        print(f"  ✓ Roman Urdu Trade : {output_roman['budget_alternative']['tradeoff']}")
        assert "quote" in output_roman['price_explanation'].lower() or "addon" in output_roman['price_explanation'].lower()
        assert "rating" in output_roman['budget_alternative']['tradeoff'].lower()
        print("  ✓ Graceful Roman Urdu offline fallback matched perfectly!")

    print("\n" + "="*70)
    print("ALL TESTS PASSED SUCCESSFULLY!")
    print("="*70 + "\n")


if __name__ == "__main__":
    run_tests()
