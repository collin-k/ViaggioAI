import pandas as pd
import chromadb
from chromadb.utils import embedding_functions
import os
from dotenv import load_dotenv
from tqdm import tqdm # Useful for progress bars

load_dotenv()

# 1. Setup OpenAI Embedding Function
openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key=os.getenv("OPENAI_API_KEY"),
    model_name="text-embedding-3-small" # Efficient and cheap
)

def build_hotel_index():
    # Load your gold data
    df = pd.read_csv("data/processed/listings_with_reviews.csv")
    
    # Initialize Chroma Persistent Client
    client = chromadb.PersistentClient(path="chroma_db")
    
    # Create (or get) the collection
    collection = client.get_or_create_collection(
        name="tokyo_listings",
        embedding_function=openai_ef
    )

    print("🛠️ Preparing documents and metadata...")
    documents = []
    metadatas = []
    ids = []

    for _, row in tqdm(df.iterrows(), total=len(df)):
        # THE DOCUMENT: This is what the AI 'reads' to find a match.
        # We combine the name, description, and review summary.
        doc_text = f"Name: {row['name']}. Location: {row['neighbourhood_cleansed']}. " \
                   f"Description: {row['description']}. Amenities: {row['amenities']}. " \
                   f"Guest Vibe: {row['review_summary']}"
        
        documents.append(doc_text)
        
        # THE METADATA: This is used for hard filtering (Price, Bedrooms).
        metadatas.append({
            "price": float(row['price']),
            "url": row['listing_url'],
            "id": str(row['id']),
            "bedrooms": int(row['bedrooms']),
            "neighbourhood": row['neighbourhood_cleansed']
        })
        
        ids.append(str(row['id']))

    # 3. Add to ChromaDB in batches (Chroma handles large data better in chunks)
    batch_size = 500
    for i in range(0, len(documents), batch_size):
        collection.add(
            documents=documents[i:i+batch_size],
            metadatas=metadatas[i:i+batch_size],
            ids=ids[i:i+batch_size]
        )

    print(f"✅ Successfully indexed {len(documents)} listings into ChromaDB!")

if __name__ == "__main__":
    build_hotel_index()