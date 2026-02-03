from src.state import TravelState
from src.tools.hotel_tool import get_hotel_info

def hotel_expert_agent(state: TravelState):
    print("--- 🏨 AGENT: NOMADIC HOTEL EXPERT ---")
    
    all_hotels = []
    # Simple budget split: give 60% of total budget to hotels
    per_city_limit = (state["budget"] * 0.6) / len(state["destinations"])

    for city in state["destinations"]:
        print(f"Searching hotels in {city}...")
        # Your RAG tool returns a formatted string
        rag_output = get_hotel_info(f"Best stay in {city} for {state['request']}", per_city_limit)
        
        # We assume the tool provides a price; if not, we mock one for the math tool
        all_hotels.append({
            "location": city,
            "price": per_city_limit, # Or extract from rag_output if possible
            "description": rag_output
        })
    
    return {
        "hotel_info": all_hotels,
        "status": "hotels_found"
    }