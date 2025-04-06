import aiohttp
import logging
from datetime import datetime
import json
from typing import List, Dict, Any, Optional

class RyanAirApiClient:
    """Client for interacting with the RyanAir API to fetch flight data"""
    BASE_URL = "https://services-api.ryanair.com/farfnd/v4"

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    async def get_cheap_flights(
        self,
        origin: str,
        date_from: str,
        date_to: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get cheap flights from RyanAir API

        Args:
            origin: Origin airport IATA code
            date_from: Start date in YYYY-MM-DD format
            date_to: End date in YYYY-MM-DD format (optional)

        Returns:
            List of flight dictionaries with price and details
        """
        self.logger.info(f"Searching RyanAir flights from {origin} between {date_from} and {date_to}")

        if date_to is None:
            date_to = date_from

        # This is a mock implementation since we don't have actual RyanAir API credentials
        # In a real implementation, we would make an HTTP request to the RyanAir API

        # Mock data for demonstration
        mock_destinations = {
            "BER": ["DUB", "STN", "BCN", "MAD", "OPO"],
            "HAM": ["STN", "DUB", "MAD", "LIS"],
            "FRA": ["STN", "DUB", "BCN", "LIS", "OPO"],
            "MUC": ["DUB", "STN", "LIS", "MAD"],
            "CGN": ["STN", "DUB", "OPO"],
            "DUS": ["DUB", "STN", "BCN"]
        }

        # City name mapping
        city_map = {
            "DUB": "Dublin",
            "STN": "London Stansted",
            "BCN": "Barcelona",
            "MAD": "Madrid",
            "LIS": "Lisbon",
            "OPO": "Porto"
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
                            "airline": "RyanAir",
                            "origin": origin,
                            "origin_city": self._get_city_name(origin),
                            "destination": dest,
                            "destination_city": city_map.get(dest, dest),
                            "departure_date": flight_date.strftime("%Y-%m-%d"),
                            "price": 19.99 + (i * 15),  # Random price
                            "currency": "EUR",
                            "link": f"https://www.ryanair.com/gb/en/trip/flights/select?adults=1&teens=0&children=0&infants=0&dateOut={flight_date.strftime('%Y-%m-%d')}&dateIn=&isConnectedFlight=false&isReturn=false&discount=0&promoCode=&originIata={origin}&destinationIata={dest}&tpAdults=1&tpTeens=0&tpChildren=0&tpInfants=0&tpStartDate={flight_date.strftime('%Y-%m-%d')}&tpEndDate=&tpDiscount=0&tpPromoCode=&tpOriginIata={origin}&tpDestinationIata={dest}"
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
