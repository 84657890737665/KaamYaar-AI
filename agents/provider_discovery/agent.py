import json
import logging
import random
import os
from typing import Any

from agents.base import BaseAgent
from agents.provider_discovery.schemas import ProviderCandidate, ProviderDiscoveryOutput

logger = logging.getLogger(__name__)

class ProviderDiscoveryAgent(BaseAgent):
    """
    Agent 2: Provider Discovery Agent.
    Given a service_type and location, finds matching providers from a local JSON dataset.
    """
    name = "provider_discovery"

    def __init__(self, data_path: str = None) -> None:
        if data_path is None:
            # Resolve absolutely relative to project root
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
            self.data_path = os.path.join(base_dir, "data", "providers.json")
        else:
            self.data_path = data_path
        self._providers = self._load_providers()

    def _load_providers(self) -> list[dict]:
        """Load the mock provider dataset from a JSON file."""
        if not os.path.exists(self.data_path):
            logger.warning("[%s] Data file %s not found. Returning empty list.", self.name, self.data_path)
            return []
        try:
            with open(self.data_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error("[%s] Failed to load providers: %s", self.name, e)
            return []

    def _calculate_simulated_distance(self, provider_location: str, user_location: str) -> float:
        """
        Simulate distance based on location string matching.
        Same city = 2-8km random
        Different city = 20-50km random
        """
        if not user_location:
            return round(random.uniform(20.0, 50.0), 1)
        
        user_loc_lower = user_location.lower()
        prov_loc_lower = provider_location.lower()
        
        # Simple check if city name matches the user's location string
        if prov_loc_lower in user_loc_lower or user_loc_lower in prov_loc_lower:
            return round(random.uniform(2.0, 8.0), 1)
        return round(random.uniform(20.0, 50.0), 1)

    def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """
        Execute the agent logic.
        
        Args:
            input_data: Must contain at least `service_type` and `location`.
                        Can be the direct ParsedServiceRequest dict or wrapped under `parsed_request`.
        
        Returns:
            ProviderDiscoveryOutput as a dict.
        """
        # Allow input to be nested under parsed_request or flat
        parsed_data = input_data.get("parsed_request", input_data)
        
        service_type = parsed_data.get("service_type")
        location = parsed_data.get("location")
        
        # Log the request
        logger.info("[%s] Searching for '%s' near '%s'...", self.name, service_type, location)

        if not service_type:
            logger.warning("[%s] No service_type provided. Returning empty candidates.", self.name)
            return ProviderDiscoveryOutput(
                candidates=[],
                total_found=0,
                search_radius_km=10.0,
                fallback_triggered=True
            ).model_dump()

        service_type_lower = service_type.lower()
        
        # 1. Filter by service type match
        matched_providers = []
        for p in self._providers:
            # Check if any of the provider's service types match the requested service
            if any(service_type_lower in st.lower() or st.lower() in service_type_lower for st in p.get("service_types", [])):
                matched_providers.append(p)

        # 2. Calculate distance for all matched providers
        candidates = []
        for p in matched_providers:
            dist = self._calculate_simulated_distance(p.get("location_name", ""), location)
            p_copy = p.copy()
            p_copy["distance_km"] = dist
            candidates.append(p_copy)

        search_radius = 10.0
        fallback_triggered = False

        # First pass: within 10km
        nearby = [c for c in candidates if c["distance_km"] <= search_radius]

        # Fallback 1: expand to 20km
        if not nearby:
            logger.info("[%s] No providers within 10km. Expanding to 20km.", self.name)
            search_radius = 20.0
            nearby = [c for c in candidates if c["distance_km"] <= search_radius]

        # Fallback 2: set fallback_triggered=True and return all city providers (matched candidates)
        if not nearby:
            logger.info("[%s] No providers within 20km. Triggering fallback to all matched providers.", self.name)
            fallback_triggered = True
            nearby = candidates

        # 3. Sort candidates by distance
        nearby.sort(key=lambda x: x["distance_km"])

        # Validate with Pydantic schema
        candidate_models = [ProviderCandidate(**c) for c in nearby]

        output = ProviderDiscoveryOutput(
            candidates=candidate_models,
            total_found=len(candidate_models),
            search_radius_km=search_radius,
            fallback_triggered=fallback_triggered
        )

        logger.info("[%s] Found %d candidates. Fallback: %s", self.name, output.total_found, output.fallback_triggered)
        return output.model_dump()
