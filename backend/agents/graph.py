from .nodes import (
    router,
    hotel_node,
    flight_node,
    unknown_node,
    generate_response,
    route_after_extraction,
)


class TravelGraph:
    def invoke(self, state: dict) -> dict:
        state.update(router(state))
        route = route_after_extraction(state)

        if route == "hotel":
            state.update(hotel_node(state))
        elif route == "flight":
            state.update(flight_node(state))
        else:
            state.update(unknown_node(state))

        state.update(generate_response(state))
        return state


graph = TravelGraph()