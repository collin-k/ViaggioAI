"""This module cleans and standardizes Airbnb listings data."""

import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv
import os
import time

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_summary_from_llm(reviews_text):
    """
    Sends a bundle of reviews to OpenAI for a 2-sentence summary.

    Parameters
    ----------
    df : pandas.DataFrame
        Raw Airbnb listings data.
    required_cols : list of str
        Column names required for downstream processing.

    Raises
    ------
    ValueError
        If one or more required columns are missing.

    Returns
    -------
    None
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system", 
                    "content": "You are a travel expert. "
                    "Summarize the following guest reviews into two concise "
                    "sentences. Focus on: Cleanliness, Location, and Noise "
                    "levels. Mention one specific Pro and one specific Con "
                    "if they exist."},
                {
                    "role": "user", 
                    "content": f"Reviews: {reviews_text}"}
            ],
            temperature=0,
            max_tokens=150
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error during API call: {e}")
        return "Review summary unavailable."

def run_summarization(): 
    # //input_file, output_path):
    # print("📂 Loading reviews and listings...")
    reviews = pd.read_csv("data/raw/reviews/florence_reviews.csv")
    listings = pd.read_csv("data/processed/listings/listings_cleaned.csv")

    # 2. Sort by date and take the Top 10 per listing
    reviews['date'] = pd.to_datetime(reviews['date'])
    top_reviews = (
        reviews.sort_values('date', ascending=False)
        .groupby('listing_id')
        .head(10)
    )

    # 3. Concatenate reviews for each listing
    grouped_reviews = top_reviews.groupby('listing_id')['comments'].apply(
        lambda x: " | ".join(str(i) for i in x)
    ).reset_index()

    # 4. Loop and Summarize (Costs API credits. Test with head(5) first)
    summaries = []
    
    # We only summarize listings that actually have reviews
    for index, row in grouped_reviews.head(5).iterrows():
    # for index, row in grouped_reviews.iterrows():
        summary = get_summary_from_llm(row['comments'])
        summaries.append({"id": row['listing_id'], "review_summary": summary})
        
        # Simple progress bar
        if index % 10 == 0:
            print(f"Processed {index}/{len(grouped_reviews)} listings...")

    # 5. Merge and Save
    summary_df = pd.DataFrame(summaries)
    final_df = pd.merge(listings, summary_df, on='id', how='left')
    final_df['review_summary'] = final_df['review_summary'].fillna("No reviews yet.")
    
    final_df.to_csv("data/processed/listings_with_reviews.csv", index=False)

if __name__ == "__main__":
    run_summarization()