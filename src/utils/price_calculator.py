def calculate_total_cost(flight_cost: float, hotel_cost: float, activity_cost: float) -> float:
    """
    Sums up the primary expenses of the trip.
    """
    return flight_cost + hotel_cost + activity_cost

def check_budget(total: float, budget: float) -> str:
    """
    Compares the total cost to the user's budget and provides feedback.
    """
    if total <= budget:
        remaining = budget - total
        return f"✅ You are within budget! You have ${remaining:,.2f} left over for souvenirs."
    else:
        overage = total - budget
        return f"❌ You are over budget by ${overage:,.2f}. Consider looking for cheaper activities or flights."

# --- TEST BLOCK ---
if __name__ == "__main__":
    # Mocking inputs (Hardcoded for testing)
    my_budget = 2000.00
    
    # Example 1: Under Budget
    flight = 600.00
    hotel = 800.00
    activities = 350.00
    
    trip_total = calculate_total_cost(flight, hotel, activities)
    
    print(f"--- Trip Financial Summary ---")
    print(f"Total Cost: ${trip_total:,.2f}")
    print(f"Budget:     ${my_budget:,.2f}")
    print(check_budget(trip_total, my_budget))
    
    print("\n" + "-"*30 + "\n")
    
    # Example 2: Over Budget
    expensive_flight = 1200.00
    new_total = calculate_total_cost(expensive_flight, hotel, activities)
    
    print(f"--- High Cost Scenario ---")
    print(f"Total Cost: ${new_total:,.2f}")
    print(f"Budget:     ${my_budget:,.2f}")
    print(check_budget(new_total, my_budget))