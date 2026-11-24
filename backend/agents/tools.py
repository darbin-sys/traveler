from typing import Any, List, Optional

import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen


HOTEL_API_BASE = "https://standing-fish-574.convex.site/hotels"
FLIGHT_API_BASE = "https://standing-fish-574.convex.site/flights"


def _fetch_json(url: str, params: Optional[dict] = None) -> Any:
    if params:
        url = f"{url}?{urlencode(params)}"

    try:
        with urlopen(url, timeout=15) as response:
            return json.loads(response.read().decode("utf-8"))
    except Exception as e:
        return None
def get_hotels() -> List[dict]:
    """
    Get a list of all available hotels.
    Use this when the user asks to show/list all hotels.
    """
    data = _fetch_json(HOTEL_API_BASE)

    if isinstance(data, dict):
        return data.get("hotels", [])

    return []


def search_hotel(
    city: str,
    checkIn: Optional[str] = None,
    checkOut: Optional[str] = None,
) -> List[dict]:
    """
    Search for hotels by city and optional check-in/check-out dates.

    Args:
        city: Hotel city name. Example: Bangkok, Colombo, Singapore.
        checkIn: Optional check-in date in YYYY-MM-DD format.
        checkOut: Optional check-out date in YYYY-MM-DD format.
    """
    params = {"city": city}

    if checkIn:
        params["checkIn"] = checkIn

    if checkOut:
        params["checkOut"] = checkOut

    data = _fetch_json(f"{HOTEL_API_BASE}/search", params=params)

    if isinstance(data, dict):
        return data.get("hotels", [])

    return []


def book_hotel(
    hotel_id: str,
    guest_name: str,
    guest_email: str,
    check_in_date: str,
    check_out_date: str,
    room_type: str,
) -> dict:
    """Book a hotel room.

    Args:
        hotel_id: ID of the hotel to book
        guest_name: Full name of the guest
        guest_email: Email of the guest
        check_in_date: Check-in date (YYYY-MM-DD)
        check_out_date: Check-out date (YYYY-MM-DD)
        room_type: Type of room (single, double, suite)
    """
    payload = {
        "hotelId": hotel_id,
        "guestName": guest_name,
        "guestEmail": guest_email,
        "checkInDate": check_in_date,
        "checkOutDate": check_out_date,
        "roomType": room_type,
    }
    request = Request(
        f"{HOTEL_API_BASE}/book",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(request, timeout=15) as response:
        return json.loads(response.read().decode("utf-8"))

def get_flights() -> List[dict]:
    """
    Get a list of all available flights.
    Use this when the user asks to show/list all flights.
    """
    data = _fetch_json(FLIGHT_API_BASE)

    if isinstance(data, dict):
        return data.get("flights", [])

    return []


def search_flights(
    origin: str,
    destination: str,
    date: Optional[str] = None,
) -> List[dict]:
    """
    Search for flights by origin, destination, and optional travel date.

    Args:
        origin: Flight origin city or airport code. Example: CMB, Bangkok.
        destination: Flight destination city or airport code. Example: BKK, Singapore.
        date: Optional flight date in YYYY-MM-DD format.
    """

    if origin and len(origin) == 3 and origin.isalpha():
        normalized_origin = origin.upper()
    else:
        normalized_origin = origin

    if destination and len(destination) == 3 and destination.isalpha():
        normalized_destination = destination.upper()
    else:
        normalized_destination = destination

    params = {
        "origin": normalized_origin,
        "destination": normalized_destination,
    }

    if date:
        params["date"] = date

    data = _fetch_json(f"{FLIGHT_API_BASE}/search", params=params)

    if isinstance(data, dict):
        return data.get("flights", [])

    return []

def book_flight(flight_id: str, passenger_name: str, passenger_email: str) -> dict:
    """Book a flight ticket.

    Args:
        flight_id: ID of the flight to book
        passenger_name: Full name of the passenger
        passenger_email: Email of the passenger
    """
    payload = {
        "flightId": flight_id,
        "passengerName": passenger_name,
        "passengerEmail": passenger_email,
    }
    request = Request(
        f"{FLIGHT_API_BASE}/book",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(request, timeout=15) as response:
        return json.loads(response.read().decode("utf-8"))