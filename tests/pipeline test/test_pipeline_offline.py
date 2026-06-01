"""
tests/pipeline test/test_pipeline_offline.py

End-to-end offline pipeline test:
Agent 1 (Parser) → Agent 2 (Discovery) → Agent 3 (Ranker) → Agent 4 (Pricing Engine)

Mocks all Gemini API calls to run the entire pipeline fully offline,
enabling robust validation even under rate limits.
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
sys.path.insert(0, str(project_root))

from agents.language_parser.agent import LanguageParserAgent
from agents.provider_discovery.agent import ProviderDiscoveryAgent
from agents.provider_discovery.schemas import ProviderCandidate
from agents.matching_ranker.agent import MatchingRankerAgent
from agents.pricing_engine.agent import PricingEngineAgent
from agents.booking_executor.agent import BookingExecutorAgent
from agents.quality_monitor.agent import QualityMonitorAgent
from agents.dispute_resolver.agent import DisputeResolverAgent

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
logger = logging.getLogger("offline_pipeline")

# Test user input: Roman Urdu, Budget Sensitive, High Urgency
TEST_INPUT = (
    "Bhai mera AC bilkul kaam nahi kar raha, "
    "G-13 Islamabad mein hoon, kal subah koi acha "
    "technician bhejo, budget thoda kam rakho."
)

def run_offline_pipeline():
    print("\n" + "="*80)
    print("KAAMYAAR AI — Integrated Offline Pipeline Test (Agent 1 → 2 → 3 → 4)")
    print("="*80)

    # 1. Initialize Agents
    a1 = LanguageParserAgent()
    a2 = ProviderDiscoveryAgent()
    a3 = MatchingRankerAgent()
    a4 = PricingEngineAgent()
    a5 = BookingExecutorAgent()
    a6 = QualityMonitorAgent()
    a7 = DisputeResolverAgent()

    # Mock for Agent 1 (Language Parser)
    mock_parser_response = MagicMock()
    mock_parser_response.text = """{
        "detected_languages": ["Roman Urdu", "English"],
        "primary_language": "Roman Urdu",
        "script_type": "latin",
        "normalized_text": "Bhai mera pipe phoot gaya hai, G-13 Islamabad mein hoon, kal subah koi acha technician bhejo, budget thoda kam rakho.",
        "translated_english": "Brother my pipe has burst, I am in G-13 Islamabad, send a good technician tomorrow morning, keep the budget a bit low.",
        "confidence_score": 0.98,
        "detected_tone": "neutral",
        "contains_code_switching": true,
        "service_type": "plumber",
        "location": "Islamabad",
        "urgency": "high",
        "budget": "budget thoda kam rakho",
        "preferences": ["kal subah", "acha technician"],
        "original_text": "Bhai mera pipe phoot gaya hai, G-13 Islamabad mein hoon, kal subah koi acha technician bhejo, budget thoda kam rakho."
    }"""

    # Mock for Agent 3 (Matching & Ranker summary)
    mock_ranker_response = MagicMock()
    mock_ranker_response.text = "Sajid AC is ranked #1 because he is located very close (1.8km) and has an expert skill level."

    # Mock for Agent 4 (Pricing explanation)
    mock_pricing_response = MagicMock()
    mock_pricing_response.text = """{
        "price_explanation": "Aap ka total quote Rs. 1570 hai. Isme base rate Rs. 1500 aur distance fee Rs. 70 shamil hai.",
        "tradeoff": "Asghar Ali Plumber aap ke Rs. 400 bacha sakte hain, lekin un ki rating 4.2 hai compared to Sajid's 4.8."
    }"""

    # Mock for Agent 5 (Booking Confirmation SMS)
    mock_booking_response = MagicMock()
    mock_booking_response.text = "Aap ki booking confirm ho chuki hai! Kal subah Kiran Qureshi aap ke bataye hue pates par pohanch jayenge. Thank you!"

    # Mock for Agent 7 (Dispute Severity)
    mock_dispute_severity_response = MagicMock()
    mock_dispute_severity_response.text = "medium"

    # Mock for Agent 7 (Dispute Apology)
    mock_dispute_apology_response = MagicMock()
    mock_dispute_apology_response.text = "Hum dil se maafi chahte hain. Aap ka complaint resolve ho chuka hai aur Rs. 200 refund transfer kar diya gaya hai. KaamYaar chunne ka shukriya!"

    # 2. Define conditional mock response handler
    def mock_generate_content(*args, **kwargs):
        # Combine args and kwargs to look up keywords
        prompt_str = ""
        if args:
            prompt_str += " ".join(str(a) for a in args)
        if kwargs:
            prompt_str += " " + " ".join(f"{k}:{v}" for k, v in kwargs.items())

        # Check request schema type or intent
        if "ParsedServiceRequest" in prompt_str or "detected_languages" in prompt_str:
            return mock_parser_response
        elif "reasoning_summary" in prompt_str or "ranked provider" in prompt_str or "best match" in prompt_str:
            return mock_ranker_response
        elif "Booking Details:" in prompt_str or "Booking ID:" in prompt_str or "Assigned Provider:" in prompt_str:
            return mock_booking_response
        elif "classify its severity level" in prompt_str.lower():
            return mock_dispute_severity_response
        elif "comforting resolution and apology" in prompt_str.lower():
            return mock_dispute_apology_response
        else:
            return mock_pricing_response

    with patch.object(a1._client.models, 'generate_content', side_effect=mock_generate_content):

        # --- Agent 1: Language Parser ---
        print("\n[Agent 1] Parsing input service request...")
        result1 = a1.run({"text": TEST_INPUT})
        parsed = result1["parsed_request"]
        print(f"  ✓ Primary Lang : {parsed.primary_language}")
        print(f"  ✓ Service Type : {parsed.service_type}")
        print(f"  ✓ Location     : {parsed.location}")
        print(f"  ✓ Urgency      : {parsed.urgency}")
        print(f"  ✓ Budget preference: {parsed.budget}")

        # --- Agent 2: Provider Discovery ---
        print("\n[Agent 2] Querying candidate service providers...")
        result2 = a2.run({
            "service_type": parsed.service_type,
            "location": parsed.location,
            "urgency": parsed.urgency,
            "budget": parsed.budget
        })
        print(f"  ✓ Candidates found: {result2['total_found']}")

        # --- Agent 3: Matching & Ranker ---
        print("\n[Agent 3] Matching & ranking candidates...")
        result3 = a3.run({
            "candidates": result2["candidates"],
            "parsed_request": parsed.model_dump() if hasattr(parsed, "model_dump") else parsed
        })
        top_provider = result3["top_recommendation"]
        if isinstance(top_provider, dict):
            top_provider = ProviderCandidate(**top_provider)

        if top_provider is not None:
            print(f"  ✓ Top Candidate : {top_provider.name} (Rating: {top_provider.rating}/5.0, Distance: {top_provider.distance_km}km)")
        else:
            print("  ✓ Top Candidate : None")
        print(f"  ✓ Match Reason  : {result3['reasoning_summary']}")

        # --- Agent 4: Pricing Engine ---
        print("\n[Agent 4] Running dynamic pricing calculations...")
        # Get second-ranked provider for budget alternative
        alternative = None
        if len(result3["ranked_providers"]) > 1:
            alternative = result3["ranked_providers"][1]["provider"]
            if isinstance(alternative, dict):
                alternative = ProviderCandidate(**alternative)

        result4 = a4.run({
            "provider": top_provider,
            "parsed_request": parsed,
            "alternative_provider": alternative
        })

        # --- Agent 5: Booking Executor ---
        print("\n[Agent 5] Executing service booking...")
        result5 = a5.run({
            "provider": top_provider,
            "parsed_request": parsed,
            "price_quote": result4,
            "confirmed_slot": "2026-05-19 10:00 AM",
            "user_id": "demo_user_001"
        })

        # --- Display Final Booking Summary ---
        print("\n" + "="*80)
        print("FINAL SERVICE BOOKING QUOTE SUMMARY")
        print("="*80)
        print(f"  Selected Provider: {top_provider.name} ({top_provider.skill_level})")
        print(f"  Estimated Time   : {result4['estimated_duration_minutes']} minutes")
        print(f"  Quote Validity   : {result4['validity_minutes']} minutes")
        
        breakdown = result4["price_breakdown"]
        print(f"\n  PRICE BREAKDOWN (PKR):")
        print(f"    Base Rate        : Rs. {breakdown['base_rate']}")
        print(f"    Distance Cost    : Rs. {breakdown['distance_cost']} (Rs. 15 per km)")
        print(f"    Urgency Premium  : Rs. {breakdown['urgency_premium']}")
        print(f"    Complexity Addon : Rs. {breakdown['complexity_addon']}")
        print(f"    Total Booking fee: Rs. {breakdown['total']}")
        
        print(f"\n  PRICE EXPLANATION ({parsed.primary_language}):")
        print(f"    {result4['price_explanation']}")

        if result4["is_budget_sensitive"] and result4["budget_alternative"]:
            alt = result4["budget_alternative"]
            print(f"\n  BUDGET ALTERNATIVE:")
            print(f"    Provider Name    : {alt['provider_name']}")
            print(f"    Alternative Total: Rs. {alt['total']}")
            print(f"    Tradeoff Detail  : {alt['tradeoff']}")

        print("\n" + "="*80)
        print("BOOKING TRANSACTION DETAILS")
        print("="*80)
        print(f"  Booking ID       : {result5['booking_id']}")
        print(f"  Status           : {result5['status']}")
        print(f"  Provider Assigned: {result5['provider_assigned']}")
        print(f"  Confirmed Slot   : {result5['confirmed_slot']}")
        print(f"  Firestore Written: {result5['firestore_written']}")
        print(f"  Reminder Time    : {result5['reminder_scheduled_at']}")
        print(f"  SMS Message      : {result5['confirmation_message']}")

        # --- Agent 6: Quality Monitor ---
        print("\n[Agent 6] Monitoring service lifecycle & collecting feedback...")
        result6 = a6.run({
            "booking_id": result5["booking_id"],
            "provider_id": top_provider.provider_id,
            "simulation_mode": True
        })

        print("\n" + "="*80)
        print("SERVICE LIFECYCLE MONITOR & CUSTOMER FEEDBACK")
        print("="*80)
        print(f"  Booking ID       : {result6['booking_id']}")
        print(f"  Final Status     : {result6['final_status']}")
        print(f"  DB Synchronized  : {result6['rating_updated_in_firestore']}")
        print(f"  Provider Rating  : {result6['old_provider_rating']} -> {result6['new_provider_rating']}")
        
        print("\n  STAGE TRANSITION LOGS:")
        for log in result6["stage_log"]:
            print(f"    - [{log['stage']}] {log['status']} ({log['timestamp']})")

        print("\n  CUSTOMER FEEDBACK:")
        fb = result6["customer_feedback"]
        print(f"    Rating: {fb['customer_rating']}/5.0")
        print(f"    Review: {fb['review_text']}")
        print(f"    Checklist Responses:")
        for k, v in fb["checklist"].items():
            print(f"      * {k}: {'✓ Yes' if v else '✗ No'}")

        print(f"\n  FUTURE MATCHING IMPACT ANALYSIS:")
        print(f"    {result6['future_matching_note']}")

        # --- Agent 7: Dispute Resolver ---
        print("\n[Agent 7] Simulating customer complaint & dispute resolution...")
        result7 = a7.run({
            "booking_id": result5["booking_id"],
            "dispute_type": "quality_complaint",
            "complaint_text": "Sajid ne leak to sahi kar di lekin cooling bohot halki hai aur gas poori nahi bhari.",
            "provider_dispute_count": 1 # Simulates second dispute
        })

        print("\n" + "="*80)
        print("CUSTOMER ESCALATION & DISPUTE RESOLUTION REPORT")
        print("="*80)
        print(f"  Dispute ID       : {result7['dispute_id']}")
        print(f"  Booking ID       : {result7['booking_id']}")
        print(f"  Category         : {result7['dispute_type']}")
        print(f"  Severity (AI)    : {result7['classified_severity'].upper()}")
        print(f"  Resolution Path  : {result7['resolution_path']}")
        print(f"  Action Taken     : {result7['action_taken']}")
        print(f"  Refund Issued    : Rs. {result7['refund_amount_pkr']}")
        print(f"  Compensation     : Rs. {result7['compensation_pkr']}")
        print(f"  Blacklisted      : {result7['blacklist_flagged']}")
        print(f"  Human Escalation : {result7['human_escalation_required']}")
        print(f"  Consequence      : {result7['provider_consequence']}")

        print(f"\n  LOCALIZED RESOLUTION MESSAGE ({parsed.primary_language}):")
        print(f"    {result7['resolution_message']}")

        print("\n  RESOLUTION STEP LOGS:")
        for log_entry in result7["dispute_log"]:
            print(f"    {log_entry}")

    print("\n" + "="*80)
    print("Integrated Offline Pipeline Test Complete!")
    print("="*80 + "\n")

if __name__ == "__main__":
    run_offline_pipeline()
