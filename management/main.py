import requests
from datetime import datetime, timedelta
from icecream import ic
import random


# List of User-Agents for randomization
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"
]

def get_random_user_agent():
    """Returns a random User-Agent from the list"""
    return random.choice(USER_AGENTS)

def get_flight_link(origin, destination, date):
    """Generates a direct link to a Ryanair flight"""
    formatted_date = date.split('T')[0]
    return f"https://www.ryanair.com/ua/uk/trip/flights/select?adults=1&teens=0&children=0&infants=0&dateOut={formatted_date}&dateIn=&isConnectedFlight=false&isReturn=false&discount=0&promoCode=&originIata={origin}&destinationIata={destination}&tpAdults=1&tpTeens=0&tpChildren=0&tpInfants=0&tpStartDate={formatted_date}&tpEndDate=&tpDiscount=0&tpPromoCode=&tpOriginIata={origin}&tpDestinationIata={destination}"

def get_cheap_flights(origin, destination, date_from, date_to):
    """Gets cheap flights from the Ryanair API"""
    url = "https://www.ryanair.com/api/farfnd/v4/oneWayFares"
    headers = {
        "User-Agent": get_random_user_agent(),
        "Content-Type": "application/json",
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://www.ryanair.com/ua/uk/trip/flights/select",
        "Origin": "https://www.ryanair.com",
        "Accept-Language": "uk-UA,uk;q=0.9,en-US;q=0.8,en;q=0.7"
    }
    params = {
        "departureAirportIataCode": origin,
        "outboundDepartureDateFrom": date_from,
        "outboundDepartureDateTo": date_to,
        "destinationAirportIataCode": destination,
        "currency": "EUR",
        "limit": 16
    }

    try:
        # Add a small timeout for requests
        response = requests.get(url, headers=headers, params=params, timeout=10)

        if response.status_code == 200:
            data = response.json()
            flights = []
            for fare in data.get("fares", []):
                price = fare["summary"]["price"]["value"]
                departure_date = fare["outbound"]["departureDate"]
                flight_link = get_flight_link(origin, destination, departure_date)
                flights.append({
                    "destination": destination,
                    "price": price,
                    "date": departure_date,
                    "link": flight_link
                })
            return flights
        else:
            print(f"Ryanair API Error: {response.status_code}")
            if response.text:
                print(f"Response: {response.text[:200]}")
            return []
    except Exception as e:
        print(f"API request error: {e}")
        return []

def get_popular_destinations_from_berlin():
    """Returns a list of popular destinations from Berlin"""
    return [
        {"code": "BCN", "city": "Barcelona"},
        {"code": "ALC", "city": "Alicante"},
        {"code": "AGP", "city": "Malaga"},
        {"code": "ATH", "city": "Athens"},
        {"code": "VLC", "city": "Valencia"},
        {"code": "NAP", "city": "Naples"},
        {"code": "CIA", "city": "Rome"},
        {"code": "PMI", "city": "Palma de Mallorca"},
        {"code": "LIS", "city": "Lisbon"},
        {"code": "PRG", "city": "Prague"},
        {"code": "MXP", "city": "Milan"},
        {"code": "BUD", "city": "Budapest"},
        {"code": "BRU", "city": "Brussels"},
        {"code": "DUB", "city": "Dublin"},
        {"code": "EDI", "city": "Edinburgh"},
        {"code": "FAO", "city": "Faro"},
        {"code": "OPO", "city": "Porto"},
        {"code": "PSA", "city": "Pisa"},
        {"code": "VIE", "city": "Vienna"},
        {"code": "ZAG", "city": "Zagreb"}
    ]

def find_cheapest_flights_from_berlin():
    """Finds the cheapest flights from Berlin for the next month"""
    today = datetime.now()
    next_month = today + timedelta(days=30)

    date_from = today.strftime("%Y-%m-%d")
    date_to = next_month.strftime("%Y-%m-%d")

    all_flights = []
    destinations = get_popular_destinations_from_berlin()

    for dest in destinations:
        flights = get_cheap_flights("BER", dest["code"], date_from, date_to)
        if flights:
            for flight in flights:
                flight["city"] = dest["city"]
            all_flights.extend(flights)

    return sorted(all_flights, key=lambda x: x["price"])

cheapest_flights = find_cheapest_flights_from_berlin()
ic(cheapest_flights[:5])
