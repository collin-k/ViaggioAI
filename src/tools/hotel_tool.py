import chromadb
from chromadb.utils import embedding_functions
import os
from dotenv import load_dotenv

load_dotenv()

openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key=os.getenv("OPENAI_API_KEY"),
    model_name="text-embedding-3-small"
)

def get_hotel_info(location_query: str, max_price: float):
    """
    Search ChromaDB for hotels matching a description and budget.
    """
    client = chromadb.PersistentClient(path="chroma_db")
    collection = client.get_collection(name="tokyo_listings", embedding_function=openai_ef)

    # Query the database
    results = collection.query(
        query_texts=[location_query],
        n_results=3,
        where={"price": {"$lte": max_price}} # The 'Accountant' logic is built-in!
    )

    if not results['documents'][0]:
        return "No stays found matching that criteria and budget."

    # Format the output for the LLM
    output = "Here are the top matches within your budget:\n\n"
    for i in range(len(results['documents'][0])):
        meta = results['metadatas'][0][i]
        doc = results['documents'][0][i]
        output += f"🏨 {meta['id']}: ${meta['price']}/night\n"
        output += f"Summary: {doc[:200]}...\n"
        output += f"Link: {meta['url']}\n\n"

    return output

# --- TEST IT ---
if __name__ == "__main__":
    # Test for a cheap place in a specific vibe
    print(get_hotel_info("Modern studio with fast wifi near Shibuya", 150))