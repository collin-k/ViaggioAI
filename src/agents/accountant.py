# src/agents/accountant.py
from src.state import TravelState

def route_after_budget_check(state: TravelState) -> str:
    # It just READS the state and returns a string signal
    if state["total_cost"] <= state["budget"]:
        return "success"
    else:
        return "recalculate"