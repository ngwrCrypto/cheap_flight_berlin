import aiohttp
import logging
from typing import Dict, Any

class CurrencyApiClient:
    """Client for fetching currency exchange rates"""
    BASE_URL = "https://api.exchangerate-api.com/v4/latest/EUR"

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    async def get_exchange_rates(self) -> Dict[str, float]:
        """
        Get current exchange rates with EUR as the base currency

        Returns:
            Dictionary with currency codes as keys and exchange rates as values
        """
        self.logger.info("Fetching currency exchange rates")

        # This is a mock implementation
        # In a real implementation, we would make an HTTP request to the exchange rate API

        # Mock exchange rates (relative to EUR)
        mock_rates = {
            "EUR": 1.0,
            "USD": 1.09,
            "GBP": 0.85,
            "PLN": 4.32,
            "UAH": 42.5,
            "HUF": 386.25,
            "CZK": 25.1,
            "BGN": 1.96,
            "RON": 4.97,
            "HRK": 7.53,
            "DKK": 7.46,
            "SEK": 11.3,
            "NOK": 11.7
        }

        return mock_rates

    async def convert_currency(self, amount: float, from_currency: str, to_currency: str) -> float:
        """
        Convert amount from one currency to another

        Args:
            amount: Amount to convert
            from_currency: Source currency code
            to_currency: Target currency code

        Returns:
            Converted amount in target currency
        """
        if from_currency == to_currency:
            return amount

        rates = await self.get_exchange_rates()

        if from_currency not in rates or to_currency not in rates:
            self.logger.error(f"Currency not found: {from_currency} or {to_currency}")
            return amount

        # Convert to EUR first (if not already)
        eur_amount = amount
        if from_currency != "EUR":
            eur_amount = amount / rates[from_currency]

        # Convert from EUR to target currency
        if to_currency == "EUR":
            return eur_amount

        return eur_amount * rates[to_currency]
