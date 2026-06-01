import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# Force UTF-8 encoding to avoid errors with special characters like '→'
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Load .env from the project root
from dotenv import load_dotenv
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
load_dotenv(os.path.join(project_root, ".env"))

from agents.language_parser.agent import LanguageParserAgent
from agents.provider_discovery.agent import ProviderDiscoveryAgent
from agents.provider_discovery.schemas import ProviderCandidate
from agents.matching_ranker.agent import MatchingRankerAgent
from agents.pricing_engine.agent import PricingEngineAgent
from agents.booking_executor.agent import BookingExecutorAgent

# Test request
TEST_INPUT = (
    "Bhai mera AC bilkul kaam nahi kar raha, "
    "G-13 Islamabad mein hoon, kal subah koi acha "
    "technician bhejo, budget thoda kam rakho."
)

print("\n" + "="*60)
print("KAAMYAAR AI — Pipeline Test (Agent 1 → 2 → 3)")
print("="*60)

# Agent 1
print("\n[Agent 1] Parsing request...")
a1 = LanguageParserAgent()
result1 = a1.run({"text": TEST_INPUT})
parsed = result1["parsed_request"]
print(f"  Language  : {parsed.primary_language}")
print(f"  Service   : {parsed.service_type}")
print(f"  Location  : {parsed.location}")
print(f"  Urgency   : {parsed.urgency}")
print(f"  Budget    : {parsed.budget}")
print(f"  Confidence: {parsed.confidence_score:.2f}")

# Agent 2
print("\n[Agent 2] Finding providers...")
a2 = ProviderDiscoveryAgent()
result2 = a2.run({
    "service_type": parsed.service_type,
    "location": parsed.location,
    "urgency": parsed.urgency,
    "budget": parsed.budget
})
print(f"  Found     : {result2['total_found']} providers")
print(f"  Fallback  : {result2['fallback_triggered']}")

# Agent 3
print("\n[Agent 3] Ranking providers...")
a3 = MatchingRankerAgent()
result3 = a3.run({
    "candidates": result2["candidates"],
    "parsed_request": parsed.model_dump() if hasattr(parsed, "model_dump") else parsed
})
print(f"\n  TOP RECOMMENDATION:")
top = result3["top_recommendation"]
if isinstance(top, dict):
    top = ProviderCandidate(**top)
if top is not None:
    print(f"  Name      : {top.name}")
    print(f"  Rating    : {top.rating}/5.0")
    print(f"  Distance  : {top.distance_km}km")
    print(f"  Rate      : Rs.{top.base_rate_pkr}")
else:
    print("  Name      : None")
print(f"\n  REASONING:")
print(f"  {result3['reasoning_summary']}")

# Agent 4
print("\n[Agent 4] Generating quote breakdown...")
a4 = PricingEngineAgent()
# Take second ranked provider as budget alternative if available
alternative = None
ranked_providers = result3.get("ranked_providers", [])
if len(ranked_providers) > 1:
    alternative = ranked_providers[1].get("provider")
    if isinstance(alternative, dict):
        alternative = ProviderCandidate(**alternative)

result4 = a4.run({
    "provider": top,
    "parsed_request": parsed,
    "alternative_provider": alternative
})

print(f"\n  QUOTE DETAILS:")
print(f"  Selected Provider: {top.name}")
breakdown = result4["price_breakdown"]
print(f"  Base Rate        : Rs. {breakdown['base_rate']}")
print(f"  Distance Cost    : Rs. {breakdown['distance_cost']}")
print(f"  Urgency Premium  : Rs. {breakdown['urgency_premium']}")
print(f"  Complexity Addon : Rs. {breakdown['complexity_addon']}")
print(f"  Total Quote      : Rs. {breakdown['total']}")
print(f"  Duration Estimate: {result4['estimated_duration_minutes']} minutes")
print(f"  Budget Sensitive : {result4['is_budget_sensitive']}")

if result4["is_budget_sensitive"] and result4["budget_alternative"]:
    alt = result4["budget_alternative"]
    print(f"\n  BUDGET ALTERNATIVE:")
    print(f"  Name             : {alt['provider_name']}")
    print(f"  Total Quote      : Rs. {alt['total']}")
    print(f"  Tradeoff Explanation:")
    print(f"    {alt['tradeoff']}")

print(f"\n  PRICE EXPLANATION ({parsed.primary_language}):")
print(f"  {result4['price_explanation']}")

# Agent 5
print("\n[Agent 5] Executing service booking...")
a5 = BookingExecutorAgent()
result5 = a5.run({
    "provider": top,
    "parsed_request": parsed,
    "price_quote": result4,
    "confirmed_slot": "2026-05-19 10:00 AM",
    "user_id": "demo_user_001"
})

print(f"\n  BOOKING TRANSACTION DETAILS:")
print(f"  Booking ID       : {result5['booking_id']}")
print(f"  Status           : {result5['status']}")
print(f"  Provider Assigned: {result5['provider_assigned']}")
print(f"  Confirmed Slot   : {result5['confirmed_slot']}")
print(f"  Firestore Written: {result5['firestore_written']}")
print(f"  Reminder Time    : {result5['reminder_scheduled_at']}")
print(f"  SMS Message      : {result5['confirmation_message']}")

print("\n" + "="*60)
print("Pipeline test complete!")
print("="*60 + "\n")