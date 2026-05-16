import logging
from typing import Dict, Optional, Tuple
import googlemaps
from app.config import settings

logger = logging.getLogger(__name__)

class MapsService:
    def __init__(self):
        self.api_key = settings.google_maps_api_key
        self.client = None
        if self.api_key:
            try:
                self.client = googlemaps.Client(key=self.api_key)
                logger.info("Google Maps client initialized successfully.")
            except Exception as e:
                logger.error(f"Failed to initialize Google Maps client: {e}")
        else:
            logger.warning("Google Maps API key not found. Using mock responses.")

    def calculate_distance(self, origin: str, destination: str) -> Optional[Dict[str, str]]:
        """
        Calculates distance and duration between two locations.
        Returns a dictionary with 'distance' and 'duration', or None if calculation fails.
        """
        if not self.client:
            # Return mock response
            return {
                "distance": "15.5 km",
                "duration": "45 mins"
            }
        
        try:
            result = self.client.distance_matrix(origins=[origin], destinations=[destination])
            if result['status'] == 'OK':
                element = result['rows'][0]['elements'][0]
                if element['status'] == 'OK':
                    return {
                        "distance": element['distance']['text'], # e.g. "15.5 km"
                        "duration": element['duration']['text']  # e.g. "45 mins"
                    }
                else:
                    logger.error(f"Distance calculation failed for element: {element['status']}")
            else:
                logger.error(f"Distance calculation failed with status: {result['status']}")
        except Exception as e:
            logger.error(f"Exception during calculate_distance: {e}")
            
        return None

    def geocode_location(self, location_name: str) -> Optional[Tuple[float, float]]:
        """
        Returns latitude and longitude coordinates for a given location name.
        """
        if not self.client:
            # Return mock response (Coordinates for a central location, e.g., Karachi, Pakistan)
            return (24.8607, 67.0011)

        try:
            geocode_result = self.client.geocode(location_name)
            if geocode_result:
                location = geocode_result[0]['geometry']['location']
                return (location['lat'], location['lng'])
            else:
                logger.warning(f"No geocode results found for {location_name}")
        except Exception as e:
            logger.error(f"Exception during geocode_location: {e}")
            
        return None

maps_service = MapsService()
