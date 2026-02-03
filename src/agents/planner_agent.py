import os
import json
from typing import Dict
from openai import OpenAI
from src.state import TravelState

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def planner_agent(state: TravelState) -> Dict:
    """
    Parses the user's request into a structured nomadic itinerary.
    """
    print("--- 📋 AGENT: NOMADIC PLANNER ---")
    
    # We provide a detailed prompt to ensure the LLM handles multiple cities
    system_prompt = """
    You are a travel coordinator. Your goal is to parse a user's request into a structured JSON itinerary.
    
    Guidelines:
    1. 'origin': Where the trip starts.
    2. 'destinations': A list of all cities the user wants to visit in order.
    3. 'durations': A list of integers representing nights in each city. If unspecified, default to 3.
    4. 'start_window': The timeframe (e.g., 'June 2026').
    5. 'budget': Total budget for the whole trip. Default to 2500.0 if not mentioned.

    Return ONLY a JSON object.
    """

    user_content = f"User Request: {state['request']}"

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            response_format={"type": "json_object"}
        )
        
        data = json.loads(response.choices[0].message.content)
        
        # 1. Update the state with the new list-based fields
        return {
            "origin": data.get("origin", "Unknown"),
            "destinations": data.get("destinations", []),
            "durations": data.get("durations", []),
            "start_window": data.get("start_window", "Flexible"),
            "budget": float(data.get("budget", 2500.0)),
            "status": "planning_complete"
        }
    
    except Exception as e:
        print(f"Error in Planner Agent: {e}")
        # Fallback to prevent the graph from breaking
        return {"status": "error", "messages": [{"role": "system", "content": str(e)}]}