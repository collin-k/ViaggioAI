import os
import json
from typing import List, Dict
from tavily import TavilyClient
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def search_activities(location: str, user_input: str) -> List[Dict]:
    """
    Finds activities based on natural language input (phrases, sentences, or keywords).
    """
    
    # 1. Generate an optimized search query based on the user's natural language
    # This turns "cheap eats and cool views" -> "best affordable restaurants with scenic views in [Location]"
    query_gen_prompt = f"Transform this user request into a highly effective search engine query for finding local activities in {location}. Request: {user_input}"
    
    query_refinement = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": query_gen_prompt}],
        temperature=0
    )
    optimized_query = query_refinement.choices[0].message.content
    
    print(f"🔍 Optimized Query: {optimized_query}")

    # 2. Search Tavily with the refined query
    search_result = tavily.search(query=optimized_query, search_depth="advanced", max_results=6)
    context = "\n".join([res['content'] for res in search_result['results']])

    # 3. Use LLM to structure the 'clean list'
    extract_prompt = f"""
    You are a local tour guide. Based on the context provided, find 5 activities that best match the user's interest: "{user_input}".
    
    Return ONLY a JSON object with a key "activities" containing a list of objects:
    - name (str)
    - description (str: 1 sentence summary)
    - cost (str: e.g., 'Free', '$15', or 'Pricey')
    - vibe (str: e.g., 'Adventurous', 'Relaxing', 'Cultural')
    - url (str: Use the source URL if provided, else 'N/A')

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
        return data.get("activities", [])
    
    except Exception as e:
        print(f"Error parsing activities: {e}")
        return []

# --- TEST BLOCK ---
if __name__ == "__main__":
    # Now you can use full sentences or multiple keywords
    location_input = "New York City"
    interest_input = "quiet bookstores with cafes where I can write, plus some cheap street food nearby"
    
    results = search_activities(location_input, interest_input)
    
    print(f"\n✅ Found {len(results)} activities for your request:")
    for i, act in enumerate(results):
        print(f"{i+1}. {act['name']} ({act['cost']})")
        print(f"   Vibe: {act['vibe']}")
        print(f"   Note: {act['description']}\n")