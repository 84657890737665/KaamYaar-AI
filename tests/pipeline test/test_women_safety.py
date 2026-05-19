import os
import sys
from pathlib import Path

# Ensure UTF-8 output on Windows to prevent UnicodeEncodeError for emojis
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Add project root to sys.path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from agents.matching_ranker.agent import MatchingRankerAgent
from agents.provider_discovery.schemas import ProviderCandidate

def test_matching_ranker_women_safety():
    print("="*60)
    print("TESTING WOMEN SAFETY MODE IN MATCHING RANKER AGENT")
    print("="*60)
    
    agent = MatchingRankerAgent()
    
    # Mock LLM summary explanation call to ensure instant and reliable offline test execution
    agent._generate_reasoning_summary = lambda lang, svc, candidates, safety_mode=False: "Mocked comparative summary."
    
    # Define two candidates: one CNIC verified, one not
    candidates = [
        ProviderCandidate(
            provider_id="PRV001",
            name="CNIC Verified Plumber",
            service_types=["plumber"],
            location_name="F-10, Islamabad",
            distance_km=2.0,
            rating=4.5,
            on_time_score=0.90,
            cancellation_rate=0.02,
            base_rate_pkr=1200,
            is_available=True,
            skill_level="expert",
            years_experience=5,
            review_count=30,
            is_cnic_verified=True
        ),
        ProviderCandidate(
            provider_id="PRV002",
            name="Unverified Plumber",
            service_types=["plumber"],
            location_name="F-10, Islamabad",
            distance_km=2.1,
            rating=4.8,
            on_time_score=0.95,
            cancellation_rate=0.01,
            base_rate_pkr=1100,
            is_available=True,
            skill_level="expert",
            years_experience=6,
            review_count=35,
            is_cnic_verified=False
        )
    ]
    
    # -------------------------------------------------------------
    # Scenario 1: Non-female user (Standard Mode)
    # -------------------------------------------------------------
    print("\n[Scenario 1] Standard Mode (user_gender='male')")
    input_data_standard = {
        "candidates": [c.model_dump() for c in candidates],
        "parsed_request": {
            "service_type": "plumber",
            "urgency": "medium",
            "primary_language": "English"
        },
        "user_gender": "male"
    }
    
    result_standard = agent.run(input_data_standard)
    ranked_standard = result_standard["ranked_providers"]
    
    print(f"Total ranked providers in Standard Mode: {len(ranked_standard)}")
    for rp in ranked_standard:
        print(f"  - {rp['provider']['name']} | Score: {rp['total_score']} | CNIC Verified: {rp['provider']['is_cnic_verified']}")
        
    assert len(ranked_standard) == 2, "Should rank both providers in standard mode"
    print("✅ Scenario 1 Passed: Both providers ranked correctly.")
    
    # -------------------------------------------------------------
    # Scenario 2: Female user (Women Safety Mode)
    # -------------------------------------------------------------
    print("\n[Scenario 2] Women Safety Mode (user_gender='female')")
    input_data_safety = {
        "candidates": [c.model_dump() for c in candidates],
        "parsed_request": {
            "service_type": "plumber",
            "urgency": "medium",
            "primary_language": "English"
        },
        "user_gender": "female"
    }
    
    result_safety = agent.run(input_data_safety)
    ranked_safety = result_safety["ranked_providers"]
    
    print(f"Total ranked providers in Safety Mode: {len(ranked_safety)}")
    for rp in ranked_safety:
        print(f"  - {rp['provider']['name']} | Score: {rp['total_score']} | CNIC Verified: {rp['provider']['is_cnic_verified']}")
        print(f"    Reasoning: {rp['reasoning']}")
        
    assert len(ranked_safety) == 1, "Should filter out the unverified provider in safety mode"
    assert ranked_safety[0]["provider"]["provider_id"] == "PRV001", "Only the verified provider should be returned"
    
    # Check that safety reasoning was added
    expected_reasoning_phrase = "Provider selected with CNIC verification for enhanced safety"
    assert expected_reasoning_phrase in ranked_safety[0]["reasoning"], f"Reasoning must contain the safety verification phrase. Found: {ranked_safety[0]['reasoning']}"
    
    # Check that safety_verified_score is present in breakdown
    breakdown = ranked_safety[0]["score_breakdown"]
    assert "safety_verified_score" in breakdown, "Score breakdown must contain safety_verified_score factor"
    assert breakdown["safety_verified_score"] > 0, "safety_verified_score should be positive and non-zero"
    
    print("✅ Scenario 2 Passed: Safety filtering, weight adjustment, scoring, and reasoning successfully verified.")
    print("\n🎉 ALL WOMEN SAFETY TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_matching_ranker_women_safety()
