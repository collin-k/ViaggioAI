from src.state import TravelState

def budget_agent(state: TravelState):
    print("--- 💰 AGENT: BUDGET CHECK ---")
    
    # 1. Get Flight Cost
    f_cost = state["flight_info"].get("total_price", 0)
    
    # 2. Sum Hotel Costs (List)
    h_cost = sum(hotel["price"] for hotel in state["hotel_info"])
    
    # 3. Sum Activity Costs (List)
    a_cost = sum(act["total_cost"] for act in state["activity_info"])
    
    grand_total = f_cost + h_cost + a_cost
    
    status = "within_budget" if grand_total <= state["budget"] else "over_budget"
    
    return {
        "total_cost": grand_total,
        "status": status
    }