from src.state import TravelState
from src.tools.flight_tool import get_multi_city_flexible_options

def flight_scout_agent(state: TravelState):
    print(f"--- ✈️ AGENT: FLIGHT SCOUT (Origin: {state['origin']}) ---")
    
    # Call your advanced nomadic tool
    itineraries = get_multi_city_flexible_options(
        origin=state["origin"],
        destinations=state["destinations"],
        durations=state["durations"],
        start_window=state["start_window"]
    )
    
    # Selection logic: Pick the first option returned (the cheapest/best)
    if not itineraries:
        return {"status": "error", "messages": [{"role": "system", "content": "No flights found"}]}
    
    best_choice = itineraries[0]
    
    return {
        "flight_info": {
            "total_price": float(best_choice["total_price_usd"]),
            "details": best_choice["options_description"],
            "itinerary": best_choice["legs"]
        },
        "status": "flights_found"
    }