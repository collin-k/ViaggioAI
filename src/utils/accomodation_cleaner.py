"""This module cleans and standardizes Airbnb listings data."""

import argparse
import numpy as np
import os
import pandas as pd
import re

from argparse import Namespace
from pathlib import Path

# --- HELPER FUNCTIONS ---
def validate_columns(df, required_cols):
    """
    Validates that all required columns are present in the DataFrame.

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
    missing = [col for col in required_cols if col not in df.columns]

    if missing:
        raise ValueError(f"Missing critical columns: {missing}")
    
def parse_bathrooms(text):
    """
    Extracts bathroom count from bathroom text.

    Parameters
    ----------
    text: str or pandas.NA
        Bathroom description from a pandas Series (e.g., "1.5 baths", "Half-bath").

    Returns
    -------
    float
        Parsed number of bathrooms, or np.nan if unavailable or unparseable.
    """
    if pd.isna(text):
        return np.nan
    text = text.lower()
    if 'half-bath' in text and not re.search(r'\d', text):
        return 0.5
    match = re.search(r'(\d+(\.\d+)?)', text)
    if match:
        return float(match.group(1))
    return np.nan

def process_bathroom_counts(df):
    """
    Cleans and standardizes bathroom-related fields.

    - Fills missing numeric bathroom counts using `bathrooms_text`
    - Identifies whether a bathroom is shared using multiple text fields

    Parameters
    ----------
    df : pandas.DataFrame
        Airbnb listings data.

    Returns
    -------
    pandas.DataFrame
        DataFrame with cleaned bathroom counts and a `bathroom_shared` flag.
    """
    # Fill bathroom counts
    df = df.copy()
    mask = df['bathrooms'].isna()
    df.loc[mask, 'bathrooms'] = df.loc[mask, 'bathrooms_text'].apply(parse_bathrooms)

    # Define the shared pattern
    bathroom_pattern = r'shared\s+(?:half[-\s]?bath|bathroom|bath)'

    # Identify shared status from various columns (Your Fallback Logic)
    shared_from_text = df['bathrooms_text'].str.contains(
        bathroom_pattern, 
        case=False, 
        na=False
    )
    fallback_mask = df['bathrooms_text'].isna()
    
    shared_fallback = (
        df['description'].str.contains(
            bathroom_pattern, 
            case=False, 
            na=False, 
            regex=True
        )
        | df['name'].str.contains(
            bathroom_pattern,
            case=False,
            na=False,
            regex=True
        )
        | df['property_type'].str.contains(
            bathroom_pattern, 
            case=False, 
            na=False, 
            regex=True
        )
    )

    # Apply shared status
    df['bathroom_shared'] = pd.Series(pd.NA, dtype='boolean')
    df.loc[shared_from_text, 'bathroom_shared'] = True
    df.loc[fallback_mask & shared_fallback, 'bathroom_shared'] = True
    df.loc[
        df['bathrooms_text'].notna() & ~shared_from_text, 
        'bathroom_shared'
    ] = False
    
    return df

def process_rooms_beds_counts(df):
    """
    Cleans and imputes bedroom and bed counts using room type and listing text.

    - Ensures private rooms have at least one bedroom and one bed
    - Detects studio apartments and sets bedroom count to zero when appropriate

    Parameters
    ----------
    df : pandas.DataFrame
        Airbnb listings data.

    Returns
    -------
    pandas.DataFrame
        DataFrame with cleaned bedroom and bed counts.
    """
    df = df.copy()

    # Fill bedroom count for Private Rooms
    private_room_mask = df['room_type'].str.contains('private room', case=False, na=False)

    bed_mask = private_room_mask & (df['bedrooms'].isna() | (df['bedrooms'] == 0))
    df.loc[bed_mask, 'bedrooms'] = 1

    # Fill bed count for Private Rooms
    beds_mask = private_room_mask & (df['beds'].isna() | (df['beds'] == 0))
    df.loc[beds_mask, 'beds'] = 1

    # Identify Studios in 'Entire home/apt' and set bedrooms to 0
    studio_pattern = r'\bstudio\b|\bstudio\s+apartment\b'
    is_studio_text = df['description'].str.contains(studio_pattern, case=False, na=False, regex=True)

    studio_mask = (
        (df['room_type'] == 'Entire home/apt') & 
        is_studio_text & 
        (df['bedrooms'].isna() | (df['bedrooms'] > 1))
    )
    df.loc[studio_mask, 'bedrooms'] = 0
    
    return df

def clean_currency(value):
    """
    Converts a currency-formatted string into a float.

    Examples
    --------
    "$1,300" -> 1300.0

    Parameters
    ----------
    value : str or numeric
        Price value to clean.

    Returns
    -------
    float or original type
        Cleaned numeric price, or original value if not a string.
    """
    if isinstance(value, str):
        return float(re.sub(r'[^\d.]', '', value))
    return value



# --- MAIN PIPELINE ---
def process_listings(input_path, output_path):
    """
    Runs the full cleaning pipeline for Airbnb listings data.

    Parameters
    ----------
    input_path : str
        Path to raw listings CSV file.
    output_path : str
        Path where cleaned listings CSV will be saved.

    Returns
    -------
    None
    """
    raw_listings = pd.read_csv(input_path)

    target_cols = [
        'id', 'listing_url', 'name', 'description', 'picture_url', 'host_name',
        'host_identity_verified', 'neighbourhood_cleansed', 'latitude', 
        'longitude', 'property_type', 'room_type', 'accommodates', 'bathrooms',
        'bathrooms_text', 'bedrooms', 'beds', 'amenities', 'price',
        'minimum_nights', 'maximum_nights', 'number_of_reviews',
        'review_scores_rating', 'review_scores_accuracy',
        'review_scores_cleanliness', 'review_scores_checkin',
        'review_scores_communication', 'review_scores_location',
        'review_scores_value', 'instant_bookable'
    ]

    # Validate schema
    validate_columns(raw_listings, target_cols)

    # Subset to required columns
    listings = raw_listings[target_cols].copy()

    # Clean price column
    listings['price'] = listings['price'].apply(clean_currency)

    # Process bathrooms
    listings = process_bathroom_counts(listings)

    # Process bedrooms and beds
    listings = process_rooms_beds_counts(listings)

    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Save cleaned data
    listings.to_csv(output_path, index=False)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Process and clean raw listings data"
    )

    parser.add_argument(
        "--input", 
        type=str, 
        help="Path to the raw listing file"
    )

    parser.add_argument(
        "--output", 
        type=str, 
        help="Path to processed listing file"
    )

    args = parser.parse_args()


    RAW_DATA = "../../data/raw/linstings/listings_robust.csv"
    PROCESSED_DATA = "data/processed/listings/listings_cleaned.csv"
    
    process_listings(RAW_DATA, PROCESSED_DATA)