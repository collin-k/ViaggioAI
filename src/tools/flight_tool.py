import os
import json
from typing import List, Dict, Optional, Union
from tavily import TavilyClient
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_multi_city_flexible_options(
    origin: str,
    destinations: List[str],      # e.g., ["Tokyo", "Osaka"]
    durations: List[int],         # e.g., [4, 2] (4 nights in Tokyo, 2 in Osaka)
    start_window: str,            # e.g., "Early June 2026"
    seat_class: str = "economy"
) -> List[Dict]:
    """
    Finds complete multi-city itineraries with flexible dates based on stay durations.
    """
    
    # 1. Build a prompt that describes the 'flow' of the trip
    itinerary_desc = f"Start at {origin}, then "
    for city, stay in zip(destinations, durations):
        itinerary_desc += f"spend approximately {stay} nights in {city}, then "
    itinerary_desc += f"return to {origin}."

    query = (
        f"Find flight itineraries for: {itinerary_desc}. "
        f"Departure window: {start_window}. Class: {seat_class}. "
        f"Search for 'multi-city fare calendars' and 'flexible round trip multi-stop'. "
        f"Identify the cheapest sequence of dates that respects the stay durations."
    )

    print(f"✈️ Searching for nomadic itinerary: {destinations}...")
    
    search_result = tavily.search(query=query, search_depth="advanced", max_results=5)
    context = "\n".join([res['content'] for res in search_result['results']])

    # 2. Extract a 'Full Journey' JSON
    extract_prompt = f"""
    You are a world-class travel agent. Find the 3 best 'Full Itinerary' options.
    Each option must include ALL legs of the trip.
    
    Return ONLY a JSON object with a key "itineraries" containing a list:
    - total_price_usd (float)
    - options_description (str: e.g., 'Cheapest route using budget airlines')
    - legs (list of objects):
        - from (str)
        - to (str)
        - date (str: YYYY-MM-DD)
        - airline (str)
        - duration_of_stay (int: nights spent in the 'to' city)

    Context: {context}
    """

    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": extract_prompt}],
            response_format={ "type": "json_object" },
            temperature=0
        )
        data = json.loads(response.choices[0].message.content)
        return data.get("itineraries", [])
    
    except Exception as e:
        print(f"Error parsing nomadic itinerary: {e}")
        return []

# --- TEST BLOCK ---
if __name__ == "__main__":
    # Example: 4 nights in Tokyo, 2 nights in Osaka, starting early June
    nomadic_trips = get_multi_city_flexible_options(
        origin="London",
        destinations=["Tokyo", "Osaka"],
        durations=[4, 2],
        start_window="First week of June 2026"
    )
    
    for i, trip in enumerate(nomadic_trips):
        print(f"\n🌟 Option {i+1}: Total ${trip['total_price_usd']}")
        for leg in trip['legs']:
            print(f"   Fly {leg['from']} -> {leg['to']} on {leg['date']} ({leg['airline']})")
            if leg['duration_of_stay'] > 0:
                print(f"   -- Stay in {leg['to']} for {leg['duration_of_stay']} nights --")