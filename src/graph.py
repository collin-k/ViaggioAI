from langgraph.graph import StateGraph, END
from src.state import TravelState

# Import your agents
from src.agents.planner_agent import planner_agent
from src.agents.flight_scout import flight_scout_agent
from src.agents.hotel_expert import hotel_expert_agent
from src.agents.activity_agent import activity_agent
from src.agents.budget_agent import budget_agent
from src.agents.accountant import route_after_budget_check

# 1. Initialize the Graph with our State schema
workflow = StateGraph(TravelState)

# 2. Add Nodes (The Workers)
workflow.add_node("planner", planner_agent)
workflow.add_node("flights", flight_scout_agent)
workflow.add_node("hotels", hotel_expert_agent)
workflow.add_node("activities", activity_agent)
workflow.add_node("budget", budget_agent)

# 3. Define the Edges (The Connections)
# We start at the planner
workflow.set_entry_point("planner")

# Standard linear flow for data gathering
workflow.add_edge("planner", "flights")
workflow.add_edge("flights", "hotels")
workflow.add_edge("hotels", "activities")
workflow.add_edge("activities", "budget")

# 4. Define the Conditional Edge (The Accountant's Decision)
workflow.add_conditional_edges(
    "budget",                 # After the budget node finishes...
    route_after_budget_check,  # ...consult the Accountant logic
    {
        "success": END,               # If okay, exit the graph
        "recalculate": "planner"      # If over budget, go back to the start
    }
)

# 5. Compile the Graph
app = workflow.compile()

print("✅ Graph structure defined and compiled successfully.")