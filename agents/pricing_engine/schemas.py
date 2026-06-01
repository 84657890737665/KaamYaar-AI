from typing import Optional
from pydantic import BaseModel, Field

class PriceBreakdown(BaseModel):
    base_rate: int = Field(..., description="Base rate of the selected provider in PKR")
    distance_cost: int = Field(..., description="Distance cost in PKR (Rs. 15 per km)")
    urgency_premium: int = Field(..., description="Premium charge based on urgency level in PKR")
    complexity_addon: int = Field(..., description="Additional fee for service complexity in PKR")
    loyalty_discount: int = Field(default=0, description="Loyalty discount for repeat users in PKR")
    surge: int = Field(default=0, description="Surge pricing addon in PKR")
    total: int = Field(..., description="Total price = base_rate + distance_cost + urgency_premium + complexity_addon - loyalty_discount + surge")

class BudgetAlternative(BaseModel):
    provider_id: str = Field(..., description="ID of the budget provider candidate")
    provider_name: str = Field(..., description="Name of the budget provider")
    total: int = Field(..., description="Total calculated quote for this budget alternative in PKR")
    tradeoff: str = Field(..., description="Explanation of tradeoffs (e.g. lower rating or further distance vs price savings)")

class PricingEngineOutput(BaseModel):
    provider_id: str = Field(..., description="Selected provider ID")
    price_breakdown: PriceBreakdown = Field(..., description="Full breakdown of the quote")
    currency: str = Field(default="PKR", description="Currency of the quote (default PKR)")
    is_budget_sensitive: bool = Field(..., description="True if the user's request indicates budget sensitivity")
    budget_alternative: Optional[BudgetAlternative] = Field(default=None, description="Cheaper alternative details if user is budget sensitive")
    price_explanation: str = Field(..., description="Warm, friendly explanation in the user's primary language")
    estimated_duration_minutes: int = Field(..., description="Estimated service duration in minutes")
    validity_minutes: int = Field(default=30, description="Quote validity duration in minutes")
