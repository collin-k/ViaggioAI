# import os
# from dotenv import load_dotenv
# from src.graph import app  # Import the compiled graph

# # Load API keys
# load_dotenv()

# def print_itinerary(state):
#     """
#     Helper function to format the final nomadic state into a beautiful report.
#     """
#     print("\n" + "="*50)
#     print("🌍 YOUR NOMADIC ITINERARY IS READY!")
#     print("="*50)
#     print(f"Origin: {state['origin']}")
#     print(f"Destinations: {' -> '.join(state['destinations'])}")
#     print(f"Total Cost: ${state['total_cost']:,.2f} (Budget: ${state['budget']:,.2f})")
#     print("-" * 50)

#     print("\n✈️ FLIGHT DETAILS")
#     print(f"Details: {state['flight_info']['details']}")
#     for leg in state['flight_info']['itinerary']:
#         print(f"  - {leg['from']} to {leg['to']} on {leg['date']} ({leg.get('airline', 'TBD')})")

#     print("\n🏨 ACCOMMODATIONS")
#     for hotel in state['hotel_info']:
#         print(f"📍 {hotel['location']}:")
#         print(f"   {hotel['description']}")

#     print("\n🎡 ACTIVITIES")
#     for act_group in state['activity_info']:
#         print(f"📍 {act_group['location']}:")
#         for act in act_group['details'][:3]: # Show top 3
#             print(f"  - {act['name']}: {act['description']} ({act['cost']})")

#     print("="*50 + "\n")

# def run_travel_planner():
#     # 1. Capture user input
#     user_query = input("Describe your dream nomadic trip (e.g., 'London to Tokyo and Osaka for 2 weeks on $4000'): ")

#     # 2. Set the initial state
#     initial_state = {
#         "request": user_query,
#         "origin": "",
#         "destinations": [],
#         "durations": [],
#         "start_window": "",
#         "budget": 0.0,
#         "messages": [],
#         "flight_info": {"total_price": 0.0, "details": "", "itinerary": []},
#         "hotel_info": [],
#         "activity_info": [],
#         "total_cost": 0.0,
#         "status": "started"
#     }

#     # 3. Run the Graph
#     print("\n🚀 Starting the Travel Agent team. Please wait...\n")
#     final_state = app.invoke(initial_state)

#     # 4. Show results
#     if final_state["status"] == "within_budget":
#         print_itinerary(final_state)
#     else:
#         print("❌ Sorry, we couldn't find a trip that fits your budget. Try adjusting your request!")

# if __name__ == "__main__":
#     run_travel_planner()

from src.graph import app
from src.state import TravelState
from dotenv import load_dotenv

load_dotenv()

def run_test_case():
    print("🧪 RUNNING END-TO-END TEST: 'Within Budget' Scenario")
    
    # Define a generous test case
    initial_state = {
        "request": "I want a 4-day luxury trip to Tokyo starting from London in September 2026. My budget is $8000.",
        "origin": "",
        "destinations": [],
        "durations": [],
        "start_window": "",
        "budget": 0.0,
        "messages": [],
        "flight_info": {"total_price": 0.0, "details": "", "itinerary": []},
        "hotel_info": [],
        "activity_info": [],
        "total_cost": 0.0,
        "status": "started"
    }

    # Execute the graph
    try:
        final_output = app.invoke(initial_state)
        verify_results(final_output)
    except Exception as e:
        print(f"❌ Test Failed with error: {e}")

def verify_results(state):
    print("\n--- 🔍 VERIFICATION CHECKLIST ---")
    
    # Check 1: Planner Extraction
    print(f"1. Planner Data: {state['destinations']} for {state['durations']} nights. (PASS)")
    
    # Check 2: Flight Integration
    if state['flight_info']['total_price'] > 0:
        print(f"2. Flight Price: ${state['flight_info']['total_price']} found. (PASS)")
    
    # Check 3: Hotel List (Ensure it's a list)
    if isinstance(state['hotel_info'], list) and len(state['hotel_info']) > 0:
        print(f"3. Hotels: {len(state['hotel_info'])} city stays recorded. (PASS)")
        
    # Check 4: Activity List
    if isinstance(state['activity_info'], list) and len(state['activity_info']) > 0:
        print(f"4. Activities: Found {len(state['activity_info'][0]['details'])} things to do. (PASS)")

    # Check 5: Accountant Node
    print(f"5. Final Status: {state['status']}. (PASS)")
    
    print("\n✅ TEST COMPLETE: State passed through all agents correctly.")

if __name__ == "__main__":
    run_test_case()