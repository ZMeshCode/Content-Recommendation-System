#!/usr/bin/env python3

import os
from dotenv import load_dotenv
from src.data_collection.api_client import TVShowDataCollector
from src.preprocessing.data_processor import TVShowDataProcessor

def main():
    """Initialize the dataset by collecting and processing TV show data."""
    print("Initializing TV Show Recommendation System...")
    
    # Load environment variables
    load_dotenv()
    
    # Check for API keys
    tmdb_key = os.getenv('TMDB_API_KEY')
    if tmdb_key == 'your_tmdb_api_key_here':
        print("Warning: TMDB API key not set. Please update the .env file.")
        return
        
    # Collect data
    print("\nCollecting TV show data...")
    collector = TVShowDataCollector()
    collector.collect_initial_dataset(num_pages=5)
    print("Data collection completed.")
    
    # Process data
    print("\nProcessing collected data...")
    processor = TVShowDataProcessor()
    combined_data = processor.merge_sources()
    print(f"Data processing completed. Total shows: {len(combined_data)}")
    
if __name__ == "__main__":
    main() 