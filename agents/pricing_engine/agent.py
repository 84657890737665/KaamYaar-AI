"""
agents/pricing_engine/agent.py

Agent 4 of 7 — Dynamic Pricing Engine.
Generates transparent, fair price quotes with full breakdown.
Suggests a budget option if the user is budget-sensitive.
"""

import logging
from typing import Any, Optional
from pydantic import BaseModel, Field

import google.genai as genai
from google.genai import types
from google.api_core.exceptions import ResourceExhausted

from agents.base import BaseAgent
from agents.provider_discovery.schemas import ProviderCandidate
from agents.language_parser.schemas import ParsedServiceRequest
from agents.pricing_engine.schemas import PricingEngineOutput, PriceBreakdown, BudgetAlternative
from core.llm_client import get_gemini_client

logger = logging.getLogger(__name__)

MODEL_ID = "gemini-2.0-flash"


class GeminiExplanation(BaseModel):
    """Schema to enforce structured output from Gemini for explanations."""
    price_explanation: str = Field(..., description="Warm, friendly price breakdown explanation in user's primary language")
    tradeoff: Optional[str] = Field(default=None, description="Clear, polite comparison and trade-off of the budget alternative in user's primary language")


class PricingEngineAgent(BaseAgent):
    """
    Calculates a transparent, fair price quote for the service booking.
    Formula: total = base_rate + distance_cost + urgency_premium + complexity_addon - loyalty_discount + surge
    """

    name = "pricing_engine"

    def __init__(self) -> None:
        self._client: genai.Client = get_gemini_client()

    def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """
        Execute the pricing engine agent.

        Args:
            input_data: A dictionary containing:
                - provider: ProviderCandidate or dict (top recommendation)
                - parsed_request: ParsedServiceRequest or dict (from Agent 1)
                - alternative_provider: ProviderCandidate or dict (optional, runner-up)

        Returns:
            A dictionary conforming to the PricingEngineOutput schema.
        """
        logger.info("[%s] Running pricing calculations...", self.name)

        # Extract and parse inputs with robust fallback keys
        raw_provider = input_data.get("provider") or input_data.get("selected_provider") or input_data.get("top_recommendation")
        raw_parsed_request = input_data.get("parsed_request") or input_data.get("request")
        raw_alt_provider = input_data.get("alternative_provider") or input_data.get("second_ranked") or input_data.get("runner_up")

        if not raw_provider:
            raise ValueError("Input data must contain a 'provider' or 'selected_provider' key.")
        if not raw_parsed_request:
            raise ValueError("Input data must contain a 'parsed_request' key.")

        # Cast to Pydantic models if they are raw dicts
        provider = ProviderCandidate(**raw_provider) if isinstance(raw_provider, dict) else raw_provider
        parsed_request = ParsedServiceRequest(**raw_parsed_request) if isinstance(raw_parsed_request, dict) else raw_parsed_request
        
        alt_provider = None
        if raw_alt_provider:
            alt_provider = ProviderCandidate(**raw_alt_provider) if isinstance(raw_alt_provider, dict) else raw_alt_provider

        logger.info(
            "[%s] Primary Provider: %s (Base Rate: Rs. %d, Distance: %.1f km), Service Type: %s",
            self.name, provider.name, provider.base_rate_pkr, provider.distance_km, parsed_request.service_type
        )

        # 1. Budget sensitivity check
        budget_str = str(parsed_request.budget or "").lower()
        budget_keywords = ["kam", "thoda", "low", "budget", "affordable", "zyada nahi", "sasta"]
        is_budget_sensitive = any(kw in budget_str for kw in budget_keywords)
        logger.info("[%s] Budget sensitivity detected: %s", self.name, is_budget_sensitive)

        # 2. Urgency premium calculation
        # UrgencyLevel options: LOW = "low", MEDIUM = "medium", HIGH = "high", EMERGENCY = "emergency"
        urgency_premium = 0
        if parsed_request.urgency:
            urgency = parsed_request.urgency
            if hasattr(urgency, "value"):
                urg_val = str(urgency.value).lower().strip()
            else:
                urg_val = str(urgency).lower().strip()
            
            # If the string contains UrgencyLevel.xxx, extract xxx
            if "." in urg_val:
                urg_val = urg_val.split(".")[-1]

            if urg_val in ("critical", "emergency"):
                urgency_premium = 500
            elif urg_val == "high":
                urgency_premium = 300
        logger.info("[%s] Calculated urgency premium: Rs. %d (Urgency: %s)", self.name, urgency_premium, parsed_request.urgency)

        # 3. Complexity add-on calculation
        complexity_addon = self._calculate_complexity_addon(parsed_request.service_type)
        logger.info("[%s] Calculated complexity addon: Rs. %d", self.name, complexity_addon)

        # 4. Primary Provider Calculations
        base_rate = provider.base_rate_pkr
        distance_cost = round(provider.distance_km * 15)  # Rs. 15 per km
        loyalty_discount = 0  # Placeholder for future loyalty history
        surge = 0  # Placeholder for future surge pricing

        total = base_rate + distance_cost + urgency_premium + complexity_addon - loyalty_discount + surge
        total = max(0, total)  # Ensure total is never negative

        price_breakdown = PriceBreakdown(
            base_rate=base_rate,
            distance_cost=distance_cost,
            urgency_premium=urgency_premium,
            complexity_addon=complexity_addon,
            loyalty_discount=loyalty_discount,
            surge=surge,
            total=total
        )

        logger.info(
            "[%s] Primary breakdown - Base: %d, Distance: %d, Urgency: %d, Complexity: %d, Total: %d",
            self.name, base_rate, distance_cost, urgency_premium, complexity_addon, total
        )

        # 5. Budget alternative calculations (if user is budget-sensitive)
        budget_alt_output = None
        if is_budget_sensitive and alt_provider:
            alt_base_rate = alt_provider.base_rate_pkr
            alt_distance_cost = round(alt_provider.distance_km * 15)
            alt_total = alt_base_rate + alt_distance_cost + urgency_premium + complexity_addon - loyalty_discount + surge
            alt_total = max(0, alt_total)

            # Tradeoff will be generated by LLM (or fallback)
            budget_alt_output = {
                "provider_id": alt_provider.provider_id,
                "provider_name": alt_provider.name,
                "total": alt_total,
                "tradeoff": ""  # Will be populated after Gemini explanation step
            }
            logger.info(
                "[%s] Budget alternative available: %s (Total: Rs. %d, Primary: Rs. %d)",
                self.name, alt_provider.name, alt_total, total
            )

        # 6. Generate Warm Multilingual Explanation and Tradeoffs
        price_explanation = ""
        tradeoff_text = ""

        primary_lang = parsed_request.primary_language or "English"
        service_type_name = parsed_request.service_type or "service"

        # Ask Gemini to generate explanation and tradeoff cleanly
        gemini_success = False
        try:
            prompt = (
                f"You are a warm, transparent customer care representative for KaamYaar AI, a premium Pakistani home-services platform.\n"
                f"Generate a warm, friendly, and clear explanation of the price quote for the user in their primary language ({primary_lang}).\n"
                f"Additionally, if a budget alternative provider is offered, write a brief comparison/trade-off explanation.\n\n"
                f"User Request Context:\n"
                f"- Requested Service: {service_type_name}\n"
                f"- Primary Language: {primary_lang}\n"
                f"- Selected Provider: {provider.name} (Rating: {provider.rating}/5.0, Distance: {provider.distance_km} km, Experience: {provider.years_experience} years)\n"
                f"- Total Price Quote: Rs. {total}\n"
                f"- Price Breakdown:\n"
                f"  - Base Rate: Rs. {base_rate}\n"
                f"  - Distance Charges: Rs. {distance_cost} (at Rs. 15 per km)\n"
                f"  - Urgency Fee: Rs. {urgency_premium}\n"
                f"  - Service Complexity Add-on: Rs. {complexity_addon}\n\n"
                f"Budget Alternative Context:\n"
                f"- Budget Alternative Offered: {'Yes' if budget_alt_output else 'No'}\n"
            )

            if budget_alt_output and alt_provider:
                savings = total - budget_alt_output["total"]
                prompt += (
                    f"- Budget Provider Name: {alt_provider.name} (Rating: {alt_provider.rating}/5.0, Distance: {alt_provider.distance_km} km, Experience: {alt_provider.years_experience} years)\n"
                    f"- Budget Provider Total Price: Rs. {budget_alt_output['total']} (Savings of Rs. {savings})\n"
                )

            prompt += (
                f"\nInstructions for `price_explanation`:\n"
                f"- Explain the total quote and how it is broken down.\n"
                f"- Write this in the user's primary language ({primary_lang}). If Roman Urdu, write in natural, friendly SMS-style Roman Urdu. If Urdu, write in Nastaliq. If Punjabi, Pashto, Balochi, or Sindhi, write in that language's native script/text.\n"
                f"- Keep the tone extremely warm, clear, and reassuring—like explaining to a close friend.\n"
                f"- Reassure the user that our pricing is fair and transparent.\n\n"
                f"Instructions for `tradeoff` (Only if budget alternative is offered):\n"
                f"- Write in the same primary language.\n"
                f"- Explain the trade-offs clearly but politely (e.g. they save money, but the provider is slightly further away or has slightly fewer reviews/ratings).\n"
                f"- Keep it friendly and let the user decide."
            )

            logger.info("[%s] Requesting Gemini explanation in %s...", self.name, primary_lang)
            response = self._client.models.generate_content(
                model=MODEL_ID,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=GeminiExplanation,
                    temperature=0.3,
                ),
            )
            # Parse the Gemini response
            gemini_data = GeminiExplanation.model_validate_json(response.text)
            price_explanation = gemini_data.price_explanation.strip()
            tradeoff_text = (gemini_data.tradeoff or "").strip()
            gemini_success = True
            logger.info("[%s] Gemini explanation successfully generated.", self.name)

        except Exception as exc:
            logger.warning("[%s] Gemini explanation failed: %s. Swerving to offline localized fallbacks.", self.name, exc)

        # If Gemini failed or is not available, trigger robust offline pre-translated fallback
        if not gemini_success:
            price_explanation, tradeoff_text = self._get_fallback_explanation(
                primary_lang=primary_lang,
                provider=provider,
                total=total,
                price_breakdown=price_breakdown,
                alt_provider=alt_provider,
                budget_alt_output=budget_alt_output
            )

        # Set tradeoff on budget_alternative if exists
        if budget_alt_output:
            budget_alt_output["tradeoff"] = tradeoff_text
            budget_alternative = BudgetAlternative(**budget_alt_output)
        else:
            budget_alternative = None

        estimated_duration = self._estimate_duration(parsed_request.service_type)

        output = PricingEngineOutput(
            provider_id=provider.provider_id,
            price_breakdown=price_breakdown,
            currency="PKR",
            is_budget_sensitive=is_budget_sensitive,
            budget_alternative=budget_alternative,
            price_explanation=price_explanation,
            estimated_duration_minutes=estimated_duration,
            validity_minutes=30
        )

        logger.info("[%s] Quote generation complete for Provider: %s. Total: Rs. %d", self.name, provider.name, total)
        return output.model_dump()

    # ------------------------------------------------------------------
    # Helper / Calculation details
    # ------------------------------------------------------------------

    def _calculate_complexity_addon(self, service_type: Optional[str]) -> int:
        """
        Calculates service complexity addon based on service description.
        AC gas=800, AC cleaning=0, pipe burst=600, wiring=400, painting=0 (default 0).
        """
        if not service_type:
            return 0
        service_lower = service_type.lower().strip()

        # Check exact matching first
        if service_lower == "ac gas":
            return 800
        elif service_lower == "ac cleaning":
            return 0
        elif service_lower == "pipe burst":
            return 600
        elif service_lower == "wiring":
            return 400
        elif service_lower == "painting":
            return 0

        # Substring robust matches
        if "gas" in service_lower and "ac" in service_lower:
            return 800
        elif "cleaning" in service_lower and "ac" in service_lower:
            return 0
        elif "burst" in service_lower or "pipe" in service_lower:
            return 600
        elif "wiring" in service_lower or "electric" in service_lower:
            return 400
        elif "painting" in service_lower or "paint" in service_lower:
            return 0

        return 0

    def _estimate_duration(self, service_type: Optional[str]) -> int:
        """Estimates duration of the service in minutes."""
        if not service_type:
            return 60
        service_lower = service_type.lower().strip()

        if "gas" in service_lower and "ac" in service_lower:
            return 60
        elif "cleaning" in service_lower and "ac" in service_lower:
            return 45
        elif "burst" in service_lower or "pipe" in service_lower:
            return 90
        elif "wiring" in service_lower or "electric" in service_lower:
            return 60
        elif "painting" in service_lower or "paint" in service_lower:
            return 180
        return 60

    def _get_fallback_explanation(
        self,
        primary_lang: str,
        provider: ProviderCandidate,
        total: int,
        price_breakdown: PriceBreakdown,
        alt_provider: Optional[ProviderCandidate] = None,
        budget_alt_output: Optional[dict] = None
    ) -> tuple[str, str]:
        """Provides localized, friendly pre-translated explanation strings in case LLM fails."""
        lang_lower = primary_lang.lower()
        savings = (total - budget_alt_output["total"]) if budget_alt_output else 0

        if "roman" in lang_lower or "urdu" in lang_lower and "roman" in lang_lower:
            # Roman Urdu Fallback
            explanation = (
                f"Aap ka total quote Rs. {total} hai. Isme base rate Rs. {price_breakdown.base_rate}, "
                f"distance cost Rs. {price_breakdown.distance_cost}, aur service complexity addon Rs. {price_breakdown.complexity_addon} "
                f"shamil hai. Hum ne transparent pricing rakhi hai taake aap ko koi fikar na ho!"
            )
            tradeoff = ""
            if alt_provider and budget_alt_output:
                tradeoff = (
                    f"{alt_provider.name} aap ke Rs. {savings} bacha sakte hain (Total Rs. {budget_alt_output['total']}), "
                    f"lekin un ki rating {alt_provider.rating}/5.0 hai aur wo {alt_provider.distance_km}km door hain "
                    f"compared to {provider.name} ({provider.distance_km}km)."
                )

        elif "urdu" in lang_lower:
            # Urdu Nastaliq Fallback
            explanation = (
                f"محترم کسٹمر، آپ کا کل تخمینہ Rs. {total} ہے۔ اس میں بنیادی فیس Rs. {price_breakdown.base_rate}، "
                f"فاصلے کے چارجز Rs. {price_breakdown.distance_cost}، اور سروس کی پیچیدگی کے چارجز Rs. {price_breakdown.complexity_addon} "
                f"شامل ہیں۔ ہماری قیمتیں مکمل طور پر شفاف ہیں تاکہ آپ مطمئن رہیں۔"
            )
            tradeoff = ""
            if alt_provider and budget_alt_output:
                tradeoff = (
                    f"{alt_provider.name} آپ کے Rs. {savings} بچا سکتے ہیں (کل قیمت Rs. {budget_alt_output['total']})، "
                    f"لیکن ان کی ریٹنگ {alt_provider.rating}/5.0 ہے اور وہ {alt_provider.distance_km} کلومیٹر دور ہیں "
                    f"جبکہ {provider.name} {provider.distance_km} کلومیٹر دور ہیں۔"
                )

        else:
            # English / Generic Fallback
            explanation = (
                f"Dear customer, your transparent quote is Rs. {total}. This includes a base rate of Rs. {price_breakdown.base_rate}, "
                f"distance charge of Rs. {price_breakdown.distance_cost} (Rs. 15/km), urgency premium of Rs. {price_breakdown.urgency_premium}, "
                f"and service complexity add-on of Rs. {price_breakdown.complexity_addon}."
            )
            tradeoff = ""
            if alt_provider and budget_alt_output:
                tradeoff = (
                    f"{alt_provider.name} is more affordable by Rs. {savings} (Total Rs. {budget_alt_output['total']}), "
                    f"but has a rating of {alt_provider.rating}/5.0 (compared to {provider.rating}/5.0) "
                    f"and is at a distance of {alt_provider.distance_km}km (compared to {provider.distance_km}km)."
                )

        return explanation, tradeoff
