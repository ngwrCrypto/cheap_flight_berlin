import requests
from datetime import datetime, timedelta
from icecream import ic
import random
import time
import aiohttp
import asyncio
from typing import List, Dict, Any, Optional


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
    return random.choice(USER_AGENTS)

def get_flight_link(origin, destination, date):
    """Generates a direct link to a Ryanair flight

    Args:
        origin: IATA code of the departure airport (e.g. "BER")
        destination: IATA code of the destination airport (e.g. "BCN")
        date: departure date, can be in 'YYYY-MM-DD' format or with time 'YYYY-MM-DDThh:mm:ss'
    """
    # Make sure we have the correct date format
    if 'T' in date:
        formatted_date = date.split('T')[0]
    else:
        formatted_date = date

    return f"https://www.ryanair.com/ua/uk/trip/flights/select?adults=1&teens=0&children=0&infants=0&dateOut={formatted_date}&dateIn=&isConnectedFlight=false&isReturn=false&discount=0&promoCode=&originIata={origin}&destinationIata={destination}&tpAdults=1&tpTeens=0&tpChildren=0&tpInfants=0&tpStartDate={formatted_date}&tpEndDate=&tpDiscount=0&tpPromoCode=&tpOriginIata={origin}&tpDestinationIata={destination}"

def get_cheap_flights(origin, destination, date_from, date_to):
    """Get information about cheap flights

    Args:
        origin: IATA code of the departure airport (e.g. "BER")
        destination: IATA code of the destination airport (e.g. "BCN")
        date_from: start date in YYYY-MM-DD format
        date_to: end date in YYYY-MM-DD format
    """
    print(f"Searching for flights: {origin} -> {destination}, from {date_from} to {date_to}")

    # Use a simplified URL for better stability
    url = "https://www.ryanair.com/api/booking/v4/en-gb/availability"
    headers = {
        "User-Agent": get_random_user_agent(),
        "Content-Type": "application/json",
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://www.ryanair.com/ua/uk/trip/flights/select",
        "Origin": "https://www.ryanair.com",
        "Accept-Language": "uk-UA,uk;q=0.9,en-US;q=0.8,en;q=0.7"
    }
    params = {
        "ADT": 1,  # 1 adult
        "CHD": 0,  # 0 children
        "DateIn": "",  # no return flight
        "DateOut": date_from,  # departure date
        "Destination": destination,
        "Disc": 0,
        "INF": 0,  # 0 infants
        "Origin": origin,
        "TEEN": 0,  # 0 teenagers
        "promoCode": "",
        "IncludeConnectingFlights": "false",
        "FlexDaysBeforeOut": 2,  # search 2 days before
        "FlexDaysOut": 2,  # search 2 days after
        "ToUs": "AGREED",
        "RoundTrip": "false"  # one-way only
    }

    try:
        # Add a delay to avoid being blocked
        time.sleep(random.uniform(0.5, 2))

        print(f"Sending request to API: {url}")
        # Add a small timeout for requests
        response = requests.get(url, headers=headers, params=params, timeout=15)

        print(f"Received response: status {response.status_code}")
        if response.status_code == 200:
            try:
                data = response.json()
                flights = []

                # Check the response structure
                if "trips" in data and len(data["trips"]) > 0:
                    for trip in data["trips"]:
                        if "dates" in trip and len(trip["dates"]) > 0:
                            for date_item in trip["dates"]:
                                if "flights" in date_item and len(date_item["flights"]) > 0:
                                    for flight in date_item["flights"]:
                                        if "regularFare" in flight and "fares" in flight["regularFare"]:
                                            price = float(flight["regularFare"]["fares"][0]["amount"])

                                            # Get departure date
                                            departure_date = flight["time"][0]
                                            flight_link = get_flight_link(origin, destination, departure_date)

                                            flights.append({
                                                "destination": destination,
                                                "price": price,
                                                "date": departure_date,
                                                "link": flight_link
                                            })

                print(f"Found flights: {len(flights)}")
                return flights
            except Exception as json_error:
                print(f"JSON parsing error: {json_error}")
                print(f"API response: {response.text[:500]}")
                return []
        else:
            print(f"Ryanair API error: {response.status_code}")
            print(f"Response: {response.text[:500]}")
            return []
    except Exception as e:
        print(f"API request error: {e}")
        return []

def get_popular_destinations_from_berlin():
    return [
        {"code": "BCN", "city": "Барселона"},
        {"code": "ALC", "city": "Аліканте"},
        {"code": "AGP", "city": "Малага"},
        {"code": "ATH", "city": "Афіни"},
        {"code": "VLC", "city": "Валенсія"},
        {"code": "NAP", "city": "Неаполь"},
        {"code": "CIA", "city": "Рим"},
        {"code": "PMI", "city": "Пальма-де-Майорка"},
        {"code": "LIS", "city": "Лісабон"},
        {"code": "PRG", "city": "Прага"},
        {"code": "MXP", "city": "Мілан"},
        {"code": "BUD", "city": "Будапешт"},
        {"code": "BRU", "city": "Брюссель"},
        {"code": "DUB", "city": "Дублін"},
        {"code": "EDI", "city": "Единбург"},
        {"code": "FAO", "city": "Фару"},
        {"code": "OPO", "city": "Порту"},
        {"code": "PSA", "city": "Піза"},
        {"code": "VIE", "city": "Відень"},
        {"code": "ZAG", "city": "Загреб"}
    ]

def find_cheapest_flights_from_berlin(date_from=None, date_to=None):
    """Finds the cheapest flights from Berlin to each city for a specified period

    Args:
        date_from: start date in YYYY-MM-DD format
        date_to: end date in YYYY-MM-DD format

    Returns:
        List of cheapest flights for each city
    """
    today = datetime.now()
    three_months = today + timedelta(days=90)  # 3 months instead of 1

    # If dates not provided, use 3 months by default
    if not date_from:
        date_from = today.strftime("%Y-%m-%d")
    if not date_to:
        date_to = three_months.strftime("%Y-%m-%d")

    print(f"Searching for cheapest flights from Berlin from {date_from} to {date_to}")

    cheapest_per_city = {}  # Dictionary to store the cheapest flight for each city
    destinations = get_popular_destinations_from_berlin()

    # Define dates for search (1 search per month for each destination)
    search_dates = []
    current_date = datetime.strptime(date_from, "%Y-%m-%d")
    end_date = datetime.strptime(date_to, "%Y-%m-%d")

    # Add the first date
    search_dates.append(current_date.strftime("%Y-%m-%d"))

    # Add dates every ~30 days
    while current_date < end_date:
        current_date += timedelta(days=30)
        if current_date <= end_date:
            search_dates.append(current_date.strftime("%Y-%m-%d"))

    print(f"Searching on these dates: {search_dates}")

    for dest in destinations:
        print(f"Searching for flights to {dest['city']} ({dest['code']})")
        all_flights = []

        # Search for each date
        for search_date in search_dates:
            flights = get_cheap_flights("BER", dest["code"], search_date, "")

            if flights:
                # Add city name to each flight
                for flight in flights:
                    flight["city"] = dest["city"]
                all_flights.extend(flights)
                print(f"Found {len(flights)} flights to {dest['city']} on {search_date}")

        if all_flights:
            # Find the cheapest flight among all dates
            cheapest_flight = min(all_flights, key=lambda x: x["price"])
            cheapest_per_city[dest["city"]] = cheapest_flight
            print(f"Cheapest flight to {dest['city']}: {cheapest_flight['price']}€ on {cheapest_flight['date']}")

    # Convert dictionary to list and sort by price
    cheapest_flights = list(cheapest_per_city.values())
    sorted_flights = sorted(cheapest_flights, key=lambda x: x["price"])

    print(f"Found cheapest flights for {len(sorted_flights)} cities")
    return sorted_flights

# Example usage for testing
if __name__ == "__main__":
    # Get cheapest flights for 3 months
    today = datetime.now()
    three_months = today + timedelta(days=90)
    date_from = today.strftime("%Y-%m-%d")
    date_to = three_months.strftime("%Y-%m-%d")

    cheapest_flights = find_cheapest_flights_from_berlin(date_from, date_to)
    ic(cheapest_flights[:5])

# Async version of get_cheap_flights
async def get_cheap_flights_async(origin, destination, date_from, date_to=""):
    """Async version: Get information about cheap flights

    Args:
        origin: IATA code of the departure airport (e.g. "BER")
        destination: IATA code of the destination airport (e.g. "BCN")
        date_from: start date in YYYY-MM-DD format
        date_to: end date in YYYY-MM-DD format
    """
    print(f"Starting async search: {origin} -> {destination}, from {date_from}")

    # Use a simplified URL for better stability
    url = "https://www.ryanair.com/api/booking/v4/en-gb/availability"
    headers = {
        "User-Agent": get_random_user_agent(),
        "Content-Type": "application/json",
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://www.ryanair.com/ua/uk/trip/flights/select",
        "Origin": "https://www.ryanair.com",
        "Accept-Language": "uk-UA,uk;q=0.9,en-US;q=0.8,en;q=0.7"
    }
    params = {
        "ADT": 1,  # 1 adult
        "CHD": 0,  # 0 children
        "DateIn": "",  # no return flight
        "DateOut": date_from,  # departure date
        "Destination": destination,
        "Disc": 0,
        "INF": 0,  # 0 infants
        "Origin": origin,
        "TEEN": 0,  # 0 teenagers
        "promoCode": "",
        "IncludeConnectingFlights": "false",
        "FlexDaysBeforeOut": 2,  # search 2 days before
        "FlexDaysOut": 2,  # search 2 days after
        "ToUs": "AGREED",
        "RoundTrip": "false"  # one-way only
    }

    try:
        # Add a small random delay to prevent API rate limiting
        # More randomization to avoid pattern detection
        delay = random.uniform(0.05, 0.3)
        await asyncio.sleep(delay)

        async with aiohttp.ClientSession() as session:
            # Add timeout to prevent hanging requests
            try:
                async with session.get(url, headers=headers, params=params, timeout=10) as response:
                    print(f"Response for {destination}: status {response.status}")

                    if response.status == 200:
                        try:
                            data = await response.json()
                            flights = []

                            # Check the response structure
                            if "trips" in data and len(data["trips"]) > 0:
                                for trip in data["trips"]:
                                    if "dates" in trip and len(trip["dates"]) > 0:
                                        for date_item in trip["dates"]:
                                            if "flights" in date_item and len(date_item["flights"]) > 0:
                                                for flight in date_item["flights"]:
                                                    if "regularFare" in flight and "fares" in flight["regularFare"]:
                                                        price = float(flight["regularFare"]["fares"][0]["amount"])

                                                        # Get departure date
                                                        departure_date = flight["time"][0]
                                                        flight_link = get_flight_link(origin, destination, departure_date)

                                                        flights.append({
                                                            "destination": destination,
                                                            "price": price,
                                                            "date": departure_date,
                                                            "link": flight_link
                                                        })

                            print(f"Found {len(flights)} flights for {destination}")
                            return flights
                        except Exception as json_error:
                            print(f"JSON parsing error for {destination}: {json_error}")
                            return []
                    else:
                        print(f"API error for {destination}: HTTP {response.status}")
                        return []
            except asyncio.TimeoutError:
                print(f"Request timeout for {destination}")
                return []
    except Exception as e:
        print(f"General error for {destination}: {e}")
        return []

# Async version of find_cheapest_flights_from_berlin
async def find_cheapest_flights_from_berlin_async(date_from=None, date_to=None):
    """Async version: Finds the cheapest flights from Berlin to each city for a specified period

    Args:
        date_from: start date in YYYY-MM-DD format
        date_to: end date in YYYY-MM-DD format

    Returns:
        List of cheapest flights for each city
    """
    today = datetime.now()
    three_months = today + timedelta(days=90)  # 3 months instead of 1

    # If dates not provided, use 3 months by default
    if not date_from:
        date_from = today.strftime("%Y-%m-%d")
    if not date_to:
        date_to = three_months.strftime("%Y-%m-%d")

    print(f"Searching for cheapest flights from Berlin from {date_from} to {date_to}")

    cheapest_per_city = {}  # Dictionary to store the cheapest flight for each city
    destinations = get_popular_destinations_from_berlin()

    # Define dates for search (1 search per month for each destination)
    search_dates = []
    current_date = datetime.strptime(date_from, "%Y-%m-%d")
    end_date = datetime.strptime(date_to, "%Y-%m-%d")

    # Add the first date
    search_dates.append(current_date.strftime("%Y-%m-%d"))

    # Add dates every ~30 days
    while current_date < end_date:
        current_date += timedelta(days=30)
        if current_date <= end_date:
            search_dates.append(current_date.strftime("%Y-%m-%d"))

    print(f"Searching on these dates: {search_dates}")

    # Create tasks for parallel search
    tasks = []
    task_info = []  # To store (dest, date) for each task

    for dest in destinations:
        for search_date in search_dates:
            task = get_cheap_flights_async("BER", dest["code"], search_date)
            tasks.append(task)
            task_info.append((dest, search_date))

    # Execute all search tasks in parallel using gather
    print(f"Starting parallel search for {len(tasks)} destination-date combinations")
    results = await asyncio.gather(*tasks)
    print(f"Parallel search completed, processing results")

    # Process results
    city_flights = {}
    for i, flights in enumerate(results):
        dest, search_date = task_info[i]
        if flights:
            if dest["city"] not in city_flights:
                city_flights[dest["city"]] = []

            # Add city name to each flight
            for flight in flights:
                flight["city"] = dest["city"]

            city_flights[dest["city"]].extend(flights)
            print(f"Found {len(flights)} flights to {dest['city']} on {search_date}")

    # Find the cheapest flight for each city
    for city, flights in city_flights.items():
        if flights:
            cheapest_flight = min(flights, key=lambda x: x["price"])
            cheapest_per_city[city] = cheapest_flight
            print(f"Cheapest flight to {city}: {cheapest_flight['price']}€ on {cheapest_flight['date']}")

    # Convert dictionary to list and sort by price
    cheapest_flights = list(cheapest_per_city.values())
    sorted_flights = sorted(cheapest_flights, key=lambda x: x["price"])

    print(f"Found cheapest flights for {len(sorted_flights)} cities")
    return sorted_flights

# Async version to search all cities for specific date
async def search_all_cities_for_date_async(date_str):
    """Async search for the cheapest flights to all cities on a specific date

    Args:
        date_str: The date to search in YYYY-MM-DD format

    Returns:
        List of cheapest flights for each city on that date
    """
    destinations = get_popular_destinations_from_berlin()

    # Create tasks for all destinations
    tasks = []
    for dest in destinations:
        task = get_cheap_flights_async("BER", dest["code"], date_str)
        tasks.append(task)

    # Execute all search tasks in parallel
    print(f"Starting parallel search for {len(tasks)} destinations on {date_str}")
    results = await asyncio.gather(*tasks)
    print(f"Parallel search completed, processing results")

    # Process the results
    cheapest_per_city = {}
    for i, flights in enumerate(results):
        dest = destinations[i]
        if flights:
            # Add city name to each flight
            for flight in flights:
                flight["city"] = dest["city"]

            # Find the cheapest flight for this city
            cheapest_flight = min(flights, key=lambda x: x["price"])
            cheapest_per_city[dest["city"]] = cheapest_flight
            print(f"Found {len(flights)} flights to {dest['city']}, cheapest: {cheapest_flight['price']}€")

    # Convert to sorted list
    cheapest_flights = list(cheapest_per_city.values())
    sorted_flights = sorted(cheapest_flights, key=lambda x: x["price"])

    return sorted_flights
