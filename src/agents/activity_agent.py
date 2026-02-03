from src.state import TravelState
from src.tools.activity_tool import search_activities

def activity_agent(state: TravelState):
    print("--- 🎡 AGENT: ACTIVITY SCOUT ---")
    
    all_activities = []
    
    for city in state["destinations"]:
        print(f"Finding things to do in {city}...")
        results = search_activities(city, state["request"])
        
        all_activities.append({
            "location": city,
            "total_cost": 50.0, # Mocked per-city activity budget
            "details": results
        })
        
    return {
        "activity_info": all_activities,
        "status": "activities_found"
    }