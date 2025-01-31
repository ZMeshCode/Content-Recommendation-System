import os
import json
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from sklearn.preprocessing import MultiLabelBinarizer, MinMaxScaler

class TVShowDataProcessor:
    def __init__(self):
        """Initialize the data processor with necessary preprocessing tools."""
        self.genre_encoder = MultiLabelBinarizer()
        self.rating_scaler = MinMaxScaler()
        
    def load_raw_data(self, source: str) -> List[Dict]:
        """Load raw data from JSON files.
        
        Args:
            source: Source of the data ('tvmaze' or 'tmdb')
            
        Returns:
            List of TV show dictionaries
        """
        filename = f"{source}_shows.json"
        filepath = os.path.join('data', 'raw', filename)
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"No data file found for {source}")
            return []
            
    def extract_features(self, shows: List[Dict], source: str) -> pd.DataFrame:
        """Extract relevant features from raw show data.
        
        Args:
            shows: List of show dictionaries
            source: Source of the data ('tvmaze' or 'tmdb')
            
        Returns:
            DataFrame with extracted features
        """
        if source == 'tvmaze':
            return pd.DataFrame([{
                'id': show.get('id'),
                'title': show.get('name'),
                'genres': show.get('genres', []),
                'rating': show.get('rating', {}).get('average'),
                'runtime': show.get('runtime'),
                'premiered': show.get('premiered'),
                'status': show.get('status'),
                'summary': show.get('summary')
            } for show in shows])
        else:  # tmdb
            return pd.DataFrame([{
                'id': show.get('id'),
                'title': show.get('name'),
                'genres': [g['name'] for g in show.get('genre_ids', [])],
                'rating': show.get('vote_average'),
                'popularity': show.get('popularity'),
                'first_air_date': show.get('first_air_date'),
                'overview': show.get('overview')
            } for show in shows])
            
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean the extracted data.
        
        Args:
            df: DataFrame with extracted features
            
        Returns:
            Cleaned DataFrame
        """
        # Remove rows with missing crucial information
        df = df.dropna(subset=['title', 'rating'])
        
        # Fill missing values
        df['genres'] = df['genres'].fillna('').apply(lambda x: x if isinstance(x, list) else [])
        
        # Convert dates to datetime
        date_columns = [col for col in df.columns if 'date' in col.lower() or 'premiered' in col.lower()]
        for col in date_columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
            
        return df
        
    def encode_genres(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
        """Encode genres using one-hot encoding.
        
        Args:
            df: DataFrame with genre lists
            
        Returns:
            Tuple of (DataFrame with encoded genres, list of genre names)
        """
        genre_matrix = self.genre_encoder.fit_transform(df['genres'])
        genre_df = pd.DataFrame(
            genre_matrix,
            columns=self.genre_encoder.classes_,
            index=df.index
        )
        return pd.concat([df.drop('genres', axis=1), genre_df], axis=1), self.genre_encoder.classes_
        
    def normalize_ratings(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize ratings to 0-1 scale.
        
        Args:
            df: DataFrame with raw ratings
            
        Returns:
            DataFrame with normalized ratings
        """
        df['normalized_rating'] = self.rating_scaler.fit_transform(
            df['rating'].values.reshape(-1, 1)
        )
        return df
        
    def process_data(self, source: str) -> pd.DataFrame:
        """Process raw data into a clean, encoded DataFrame.
        
        Args:
            source: Source of the data ('tvmaze' or 'tmdb')
            
        Returns:
            Processed DataFrame
        """
        # Load and extract features
        raw_data = self.load_raw_data(source)
        if not raw_data:
            return pd.DataFrame()
            
        df = self.extract_features(raw_data, source)
        
        # Clean and process
        df = self.clean_data(df)
        df, genre_names = self.encode_genres(df)
        df = self.normalize_ratings(df)
        
        # Save processed data
        output_path = os.path.join('data', 'processed', f"{source}_processed.csv")
        df.to_csv(output_path, index=False)
        
        return df
        
    def merge_sources(self) -> pd.DataFrame:
        """Merge processed data from all sources.
        
        Returns:
            Combined DataFrame from all sources
        """
        tvmaze_df = self.process_data('tvmaze')
        tmdb_df = self.process_data('tmdb')
        
        # Add source column to each DataFrame
        if not tvmaze_df.empty:
            tvmaze_df['source'] = 'tvmaze'
        if not tmdb_df.empty:
            tmdb_df['source'] = 'tmdb'
            
        # Combine DataFrames
        combined_df = pd.concat([tvmaze_df, tmdb_df], ignore_index=True)
        
        # Save combined data
        output_path = os.path.join('data', 'processed', 'combined_shows.csv')
        combined_df.to_csv(output_path, index=False)
        
        return combined_df
        
if __name__ == "__main__":
    processor = TVShowDataProcessor()
    combined_data = processor.merge_sources() 