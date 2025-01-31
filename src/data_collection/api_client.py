import os
import json
from typing import Dict, List, Optional
import requests
import tmdbsimple as tmdb
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class TVShowDataCollector:
    def __init__(self):
        """Initialize API clients with appropriate API keys."""
        self.tmdb_api_key = os.getenv('TMDB_API_KEY')
        if self.tmdb_api_key:
            tmdb.API_KEY = self.tmdb_api_key
        
        self.tvmaze_base_url = "http://api.tvmaze.com"
        
    def fetch_tvmaze_shows(self, page: int = 0) -> List[Dict]:
        """Fetch TV shows from TVMaze API.
        
        Args:
            page: Page number for pagination
            
        Returns:
            List of TV show data dictionaries
        """
        try:
            response = requests.get(f"{self.tvmaze_base_url}/shows?page={page}")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching TVMaze data: {e}")
            return []
            
    def fetch_tmdb_shows(self, page: int = 1) -> List[Dict]:
        """Fetch TV shows from TMDb API.
        
        Args:
            page: Page number for pagination
            
        Returns:
            List of TV show data dictionaries
        """
        if not self.tmdb_api_key:
            print("TMDb API key not found!")
            return []
            
        try:
            tv = tmdb.TV()
            response = tv.popular(page=page)
            return response.get('results', [])
        except Exception as e:
            print(f"Error fetching TMDb data: {e}")
            return []
            
    def fetch_show_details(self, show_id: int, source: str = 'tvmaze') -> Optional[Dict]:
        """Fetch detailed information for a specific show.
        
        Args:
            show_id: ID of the show
            source: API source ('tvmaze' or 'tmdb')
            
        Returns:
            Dictionary containing show details
        """
        try:
            if source == 'tvmaze':
                response = requests.get(f"{self.tvmaze_base_url}/shows/{show_id}")
                response.raise_for_status()
                return response.json()
            elif source == 'tmdb':
                tv = tmdb.TV(show_id)
                return tv.info()
        except Exception as e:
            print(f"Error fetching show details from {source}: {e}")
            return None
            
    def save_to_json(self, data: List[Dict], filename: str):
        """Save collected data to a JSON file.
        
        Args:
            data: List of TV show data to save
            filename: Name of the output file
        """
        filepath = os.path.join('data', 'raw', filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
            
    def collect_initial_dataset(self, num_pages: int = 5):
        """Collect initial dataset from both APIs.
        
        Args:
            num_pages: Number of pages to fetch from each API
        """
        tvmaze_shows = []
        tmdb_shows = []
        
        # Collect TVMaze shows
        for page in range(num_pages):
            shows = self.fetch_tvmaze_shows(page)
            if shows:
                tvmaze_shows.extend(shows)
                
        # Collect TMDb shows
        for page in range(1, num_pages + 1):
            shows = self.fetch_tmdb_shows(page)
            if shows:
                tmdb_shows.extend(shows)
                
        # Save collected data
        self.save_to_json(tvmaze_shows, 'tvmaze_shows.json')
        self.save_to_json(tmdb_shows, 'tmdb_shows.json')
        
if __name__ == "__main__":
    collector = TVShowDataCollector()
    collector.collect_initial_dataset() 