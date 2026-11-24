import re

from .tools import get_hotels, get_flights, search_hotel, search_flights, book_hotel,book_flight
from .entity import GraphState
def router(state: GraphState) -> dict:
    user_message = state["messages"][-1]
    message = user_message.lower()
    dates = re.findall(r"\b\d{4}-\d{2}-\d{2}\b", user_message)

    if re.search(r"\b(hotel|hotels|room|rooms|stay|accommodation)\b", message):
        intent = "hotel"
    elif re.search(r"\b(flight|flights|ticket|tickets|fly|airline|airfare)\b", message):
        intent = "flight"
    else:
        intent = "unknown"

    sub_action = "book" if re.search(r"\bbook|booking\b", message) else "search"
    if re.search(r"\b(all|list|show)\b", message):
        sub_action = "list_all"

    city_match = re.search(r"\b(?:in|at)\s+([a-zA-Z]+)\b", message)
    city = city_match.group(1).title() if city_match else None

    route_match = re.search(
        r"\b(?:from|origin)\s+([A-Za-z]{3})\s+(?:to|destination)\s+([A-Za-z]{3})",
        message,
    )
    origin = route_match.group(1).upper() if route_match else None
    destination = route_match.group(2).upper() if route_match else None

    data = {
        "intent": intent,
        "sub_action": sub_action,
        "city": city,
        "check_in": dates[0] if dates else None,
        "check_out": dates[1] if len(dates) > 1 else None,
        "origin": origin,
        "destination": destination,
        "flight_date": dates[0] if dates else None,
        "hotel_id": None,
        "guest_name": None,
        "guest_email": None,
        "room_type": None,
        "flight_id": None,
        "passenger_name": None,
        "passenger_email": None,
    }

    return {
        "intent": data.get("intent", "unknown"),
        "sub_action": data.get("sub_action", "general"),

        "city": data.get("city"),
        "check_in": data.get("check_in"),
        "check_out": data.get("check_out"),

        "origin": data.get("origin"),
        "destination": data.get("destination"),
        "flight_date": data.get("flight_date"),

        "hotel_id": data.get("hotel_id"),
        "guest_name": data.get("guest_name"),
        "guest_email": data.get("guest_email"),
        "room_type": data.get("room_type"),

        "flight_id": data.get("flight_id"),
        "passenger_name": data.get("passenger_name"),
        "passenger_email": data.get("passenger_email"),

        "hotel_results": [],
        "flight_results": [],
        "response_text": "",
    }



def _format_hotel(hotel: dict) -> str:
    name = hotel.get("name", "Unknown hotel")

    city_data = hotel.get("city", "unknown city")
    if isinstance(city_data, dict):
        city = city_data.get("name", "unknown city")
    else:
        city = city_data

    stars = hotel.get("stars", hotel.get("rating", "N/A"))
    price = hotel.get("price", hotel.get("pricePerNight", "N/A"))
    currency = hotel.get("currency", "USD")

    available = hotel.get(
        "available_rooms",
        hotel.get("availableRooms", hotel.get("available", "N/A"))
    )

    return (
        f"{name} in {city}, "
        f"{stars} stars - {currency} {price}/night - "
        f"{available} rooms"
    )


def _format_flight(flight: dict) -> str:
    airline = flight.get("airline", "Unknown airline")

    number = flight.get(
        "flightNumber",
        flight.get("flight_number", flight.get("flightNo", "N/A"))
    )

    origin_data = flight.get("origin", "unknown")
    destination_data = flight.get("destination", "unknown")

    if isinstance(origin_data, dict):
        origin = origin_data.get("airport", origin_data.get("city", "unknown"))
    else:
        origin = origin_data

    if isinstance(destination_data, dict):
        destination = destination_data.get("airport", destination_data.get("city", "unknown"))
    else:
        destination = destination_data

    flight_date = flight.get(
        "flightDate",
        flight.get("date", flight.get("departure_date", "unknown"))
    )

    departure_time = flight.get(
        "departureTime",
        flight.get("departure_time", "N/A")
    )

    arrival_time = flight.get(
        "arrivalTime",
        flight.get("arrival_time", "N/A")
    )

    price = flight.get("price", "N/A")
    currency = flight.get("currency", "USD")

    seats = flight.get(
        "availableSeats",
        flight.get("available_seats", flight.get("seats", "N/A"))
    )

    return (
        f"{airline} {number} from {origin} to {destination} "
        f"on {flight_date}, {departure_time} - {arrival_time} "
        f"- {currency} {price} - {seats} seats"
    )



def hotel_node(state: GraphState) -> dict:
    city = state.get("city")
    check_in = state.get("check_in")
    check_out = state.get("check_out")

    if state.get("sub_action") == "book":
        hotel_id = state.get("hotel_id")
        guest_name = state.get("guest_name")
        guest_email = state.get("guest_email")
        room_type = state.get("room_type")
        check_in_date = state.get("check_in")
        check_out_date = state.get("check_out")

        missing = [
            field
            for field, value in [
                ("hotel_id", hotel_id),
                ("guest_name", guest_name),
                ("guest_email", guest_email),
                ("check_in", check_in_date),
                ("check_out", check_out_date),
                ("room_type", room_type),
            ]
            if not value
        ]

        if missing:
            return {
                "hotel_results": [],
                "flight_results": [],
                "response_text": (
                    "I need more details to book the hotel. "
                    "Please provide hotel_id, guest_name, guest_email, room_type, "
                    "check_in, and check_out."
                ),
            }

        result = book_hotel(
            hotel_id=hotel_id,
            guest_name=guest_name,
            guest_email=guest_email,
            check_in_date=check_in_date,
            check_out_date=check_out_date,
            room_type=room_type,
        )

    elif city:
        params = {
            "city": city,
        }

        if check_in:
            params["checkIn"] = check_in

        if check_out:
            params["checkOut"] = check_out

        result = search_hotel(
            city=params["city"],
            checkIn=params.get("checkIn"),
            checkOut=params.get("checkOut"),
        )

    else:
        result = get_hotels()

    if state.get("sub_action") == "book":
        if isinstance(result, dict):
            confirmation = result.get("message") or result.get("status") or "Hotel booking completed."
            return {
                "hotel_results": [],
                "flight_results": [],
                "response_text": confirmation,
            }

        return {
            "hotel_results": [],
            "flight_results": [],
            "response_text": "Hotel booking completed.",
        }

    if isinstance(result, dict):
        hotel_results = result.get("hotels", [])
    elif isinstance(result, list):
        hotel_results = result
    else:
        hotel_results = []

    if not hotel_results:
        return {
            "hotel_results": [],
            "flight_results": [],
            "response_text": (
                "I couldn't find any hotels. "
                "Try searching by city, for example: 'available hotels in Mumbai'."
            ),
        }

    return {
        "hotel_results": hotel_results,
        "flight_results": [],
        "response_text": "",
    }


def flight_node(state: GraphState) -> dict:
    origin = state.get("origin")
    destination = state.get("destination")
    flight_date = state.get("flight_date")

    if state.get("sub_action") == "book":
        flight_id = state.get("flight_id")
        passenger_name = state.get("passenger_name")
        passenger_email = state.get("passenger_email")

        missing = [
            field
            for field, value in [
                ("flight_id", flight_id),
                ("passenger_name", passenger_name),
                ("passenger_email", passenger_email),
            ]
            if not value
        ]

        if missing:
            return {
                "hotel_results": [],
                "flight_results": [],
                "response_text": (
                    "I need more details to book the flight. "
                    "Please provide flight_id, passenger_name, and passenger_email."
                ),
            }

        result = book_flight(
            flight_id=flight_id,
            passenger_name=passenger_name,
            passenger_email=passenger_email,
        )

    elif origin and destination:
        params = {
            "origin": origin,
            "destination": destination,
        }

        if flight_date:
            params["date"] = flight_date

        result = search_flights(
            origin=params["origin"],
            destination=params["destination"],
            date=params.get("date"),
        )

    elif origin or destination:
        return {
            "hotel_results": [],
            "flight_results": [],
            "response_text": (
                "I need both departure and destination information. "
                "For example: 'flight from BOM to DEL'."
            ),
        }

    else:
        result = get_flights()

    if state.get("sub_action") == "book":
        if isinstance(result, dict):
            confirmation = result.get("message") or result.get("status") or "Flight booking completed."
            return {
                "hotel_results": [],
                "flight_results": [],
                "response_text": confirmation,
            }

        return {
            "hotel_results": [],
            "flight_results": [],
            "response_text": "Flight booking completed.",
        }

    if isinstance(result, dict):
        flight_results = result.get("flights", [])
    elif isinstance(result, list):
        flight_results = result
    else:
        flight_results = []

    if not flight_results:
        return {
            "hotel_results": [],
            "flight_results": [],
            "response_text": (
                "I couldn't find flights matching your request. "
                "Try another route or ask for all flights."
            ),
        }

    return {
        "hotel_results": [],
        "flight_results": flight_results,
        "response_text": "",
    }


def unknown_node(state: GraphState) -> dict:
    return {
        "hotel_results": [],
        "flight_results": [],
        "response_text": (
            "I can help you search for flights or hotels. "
            "Try 'Find flights from BOM to DEL' or 'Hotels in Bangkok'."
        ),
    }



def generate_response(state: GraphState) -> dict:
    if state.get("response_text"):
        return {
            "response_text": state["response_text"]
        }

    hotel_results = state.get("hotel_results", [])
    flight_results = state.get("flight_results", [])

    if hotel_results:
        count = len(hotel_results)
        lines = [_format_hotel(hotel) for hotel in hotel_results[:5]]

        return {
            "response_text": (
                f"I found {count} hotel option{'s' if count != 1 else ''}:\n"
                + "\n".join(lines)
            )
        }

    if flight_results:
        count = len(flight_results)
        lines = [_format_flight(flight) for flight in flight_results[:5]]

        return {
            "response_text": (
                f"I found {count} flight option{'s' if count != 1 else ''}:\n"
                + "\n".join(lines)
            )
        }

    return {
        "response_text": "I couldn't find matching travel options."
    }


def route_after_extraction(state: GraphState) -> str:
    intent = state.get("intent", "unknown")

    if intent == "hotel":
        return "hotel"

    if intent == "flight":
        return "flight"

    return "unknown"