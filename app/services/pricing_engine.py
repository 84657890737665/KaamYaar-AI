import time
from typing import Dict, Any, Optional
from app.models.provider import Provider

class PriceCache:
    """Simple in-memory TTL cache for price estimates"""
    def __init__(self, ttl_seconds: int = 300):
        self.cache = {}
        self.ttl = ttl_seconds

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        if key in self.cache:
            entry, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl:
                return entry
            else:
                del self.cache[key]
        return None

    def set(self, key: str, value: Dict[str, Any]):
        self.cache[key] = (value, time.time())

# Global cache instance (5 minutes TTL)
price_cache = PriceCache(ttl_seconds=300)

class PricingEngine:
    @staticmethod
    def calculate_price(provider: Provider, user_request: Dict[str, Any], distance_km: float) -> Dict[str, float]:
        """
        Calculate price with transparent breakdown.
        Formula: final_price = base_rate + distance_fee + urgency_fee + complexity_fee - discount
        """
        base_rate = float(provider.base_rate)
        
        # Distance fee: ₹10 per km
        distance_fee = float(distance_km) * 10.0
        
        # Urgency tiers: normal (0%), urgent (+25%), emergency (+50%)
        urgency = user_request.get('urgency', 'normal').lower()
        if urgency == 'emergency':
            urgency_fee = base_rate * 0.50
        elif urgency == 'urgent':
            urgency_fee = base_rate * 0.25
        else:
            urgency_fee = 0.0
            
        # Complexity tiers: simple (0%), moderate (+15%), complex (+30%)
        complexity = user_request.get('complexity', 'simple').lower()
        if complexity == 'complex':
            complexity_fee = base_rate * 0.30
        elif complexity == 'moderate':
            complexity_fee = base_rate * 0.15
        else:
            complexity_fee = 0.0
            
        # Discount: first_booking (-10%), repeat_customer (-5%), none (0%)
        discount_type = user_request.get('discount', 'none').lower()
        if discount_type == 'first_booking':
            discount_amount = base_rate * 0.10
        elif discount_type == 'repeat_customer':
            discount_amount = base_rate * 0.05
        else:
            discount_amount = 0.0
            
        total = base_rate + distance_fee + urgency_fee + complexity_fee - discount_amount
        
        return {
            'base': round(base_rate, 2),
            'distance': round(distance_fee, 2),
            'urgency': round(urgency_fee, 2),
            'complexity': round(complexity_fee, 2),
            'discount': -round(discount_amount, 2),
            'total': round(total, 2)
        }
