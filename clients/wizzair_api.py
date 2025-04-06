import aiohttp
import logging
from datetime import datetime
import json
from typing import List, Dict, Any, Optional

class WizzAirApiClient:
    """Client for interacting with the WizzAir API to fetch flight data"""
    BASE_URL = "https://wizzair.com/api/v1"

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    async def get_cheap_flights(
        self,
        origin: str,
        date_from: str,
        date_to: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get cheap flights from WizzAir API

        Args:
            origin: Origin airport IATA code
            date_from: Start date in YYYY-MM-DD format
            date_to: End date in YYYY-MM-DD format (optional)

        Returns:
            List of flight dictionaries with price and details
        """
        self.logger.info(f"Searching WizzAir flights from {origin} between {date_from} and {date_to}")

        if date_to is None:
            date_to = date_from

        # This is a mock implementation since we don't have actual WizzAir API credentials
        # In a real implementation, we would make an HTTP request to the WizzAir API

        # Mock data for demonstration
        mock_destinations = {
            "BER": ["VNO", "KBP", "WAW", "BUD", "SOF"],
            "HAM": ["VIE", "BUD", "CPH", "SOF"],
            "FRA": ["BUD", "SOF", "KBP", "WAW"],
            "MUC": ["BUD", "SOF", "WAW", "VIE"],
            "CGN": ["VIE", "BUD", "SOF"],
            "DUS": ["BUD", "VIE", "SOF"]
        }

        # City name mapping
        city_map = {
            "VNO": "Vilnius",
            "KBP": "Kyiv",
            "WAW": "Warsaw",
            "BUD": "Budapest",
            "SOF": "Sofia",
            "VIE": "Vienna",
            "CPH": "Copenhagen"
        }

        results = []

        # Generate some fake flights based on the origin
        if origin in mock_destinations:
            for dest in mock_destinations[origin]:
                # Create a few flight options
                for i in range(1, 4):
                    # Parse date string to datetime
                    start_date = datetime.strptime(date_from, "%Y-%m-%d")
                    # Add some days to create different dates
                    flight_date = start_date.replace(day=start_date.day + i % 28)

                    # Only include if within the date range
                    if date_from <= flight_date.strftime("%Y-%m-%d") <= date_to:
                        results.append({
                            "airline": "WizzAir",
                            "origin": origin,
                            "origin_city": self._get_city_name(origin),
                            "destination": dest,
                            "destination_city": city_map.get(dest, dest),
                            "departure_date": flight_date.strftime("%Y-%m-%d"),
                            "price": 29.99 + (i * 10),  # Random price
                            "currency": "EUR",
                            "link": f"https://wizzair.com/en-gb/flights/{origin}-{dest}/{flight_date.strftime('%Y-%m-%d')}"
                        })

        return results

    def _get_city_name(self, code: str) -> str:
        """Get city name from airport code"""
        city_map = {
            "BER": "Berlin",
            "HAM": "Hamburg",
            "FRA": "Frankfurt",
            "MUC": "Munich",
            "CGN": "Cologne",
            "DUS": "Düsseldorf"
        }
        return city_map.get(code, code)
