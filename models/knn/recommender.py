import os
import pandas as pd
import numpy as np
from typing import List, Tuple, Dict
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler

class KNNRecommender:
    def __init__(self, n_neighbors: int = 5):
        """Initialize the KNN recommender system.
        
        Args:
            n_neighbors: Number of neighbors to use for recommendations
        """
        self.n_neighbors = n_neighbors
        self.model = NearestNeighbors(
            n_neighbors=n_neighbors + 1,  # +1 because the item itself is included
            metric='cosine'
        )
        self.scaler = StandardScaler()
        self.shows_df = None
        self.feature_matrix = None
        
    def load_data(self) -> None:
        """Load and prepare the processed show data."""
        data_path = os.path.join('data', 'processed', 'combined_shows.csv')
        self.shows_df = pd.read_csv(data_path)
        
        # Select features for similarity computation
        feature_cols = [col for col in self.shows_df.columns 
                       if col not in ['id', 'title', 'summary', 'overview', 'source']]
        
        # Prepare feature matrix
        self.feature_matrix = self.shows_df[feature_cols].fillna(0)
        self.feature_matrix = self.scaler.fit_transform(self.feature_matrix)
        
    def fit(self) -> None:
        """Fit the KNN model on the feature matrix."""
        if self.feature_matrix is None:
            raise ValueError("Data not loaded. Call load_data() first.")
            
        self.model.fit(self.feature_matrix)
        
    def get_similar_shows(self, show_id: int, n_recommendations: int = 5) -> List[Dict]:
        """Get similar shows based on a given show ID.
        
        Args:
            show_id: ID of the show to find similar shows for
            n_recommendations: Number of recommendations to return
            
        Returns:
            List of dictionaries containing similar show information
        """
        if self.shows_df is None:
            raise ValueError("Model not fitted. Call fit() first.")
            
        # Find the index of the show
        show_idx = self.shows_df[self.shows_df['id'] == show_id].index
        if len(show_idx) == 0:
            raise ValueError(f"Show ID {show_id} not found in the dataset")
            
        # Get nearest neighbors
        distances, indices = self.model.kneighbors(
            self.feature_matrix[show_idx[0]].reshape(1, -1)
        )
        
        # Remove the show itself (first result)
        similar_shows = []
        for idx, distance in zip(indices[0][1:], distances[0][1:]):
            show = self.shows_df.iloc[idx]
            similar_shows.append({
                'id': int(show['id']),
                'title': show['title'],
                'similarity_score': 1 - distance,  # Convert distance to similarity
                'genres': show.get('genres', []),
                'rating': float(show.get('rating', 0))
            })
            
        return similar_shows[:n_recommendations]
        
    def get_recommendations(self, user_ratings: Dict[int, float], n_recommendations: int = 5) -> List[Dict]:
        """Get personalized recommendations based on user ratings.
        
        Args:
            user_ratings: Dictionary mapping show IDs to user ratings (1-5)
            n_recommendations: Number of recommendations to return
            
        Returns:
            List of dictionaries containing recommended show information
        """
        if self.shows_df is None:
            raise ValueError("Model not fitted. Call fit() first.")
            
        # Calculate weighted average of similar shows for each rated show
        weighted_sims = np.zeros(len(self.shows_df))
        weights_sum = 0
        
        for show_id, rating in user_ratings.items():
            # Normalize rating to 0-1 scale
            normalized_rating = (rating - 1) / 4
            
            # Get similar shows
            try:
                similar_shows = self.get_similar_shows(
                    show_id,
                    n_recommendations=len(self.shows_df)
                )
                
                # Add weighted similarities
                for show in similar_shows:
                    idx = self.shows_df[self.shows_df['id'] == show['id']].index[0]
                    weighted_sims[idx] += show['similarity_score'] * normalized_rating
                    weights_sum += show['similarity_score']
                    
            except ValueError:
                continue
                
        if weights_sum > 0:
            weighted_sims /= weights_sum
            
        # Get top N recommendations
        top_indices = np.argsort(weighted_sims)[::-1]
        
        # Filter out already rated shows
        recommendations = []
        for idx in top_indices:
            show = self.shows_df.iloc[idx]
            if show['id'] not in user_ratings:
                recommendations.append({
                    'id': int(show['id']),
                    'title': show['title'],
                    'predicted_rating': float(weighted_sims[idx] * 5),  # Scale back to 1-5
                    'genres': show.get('genres', []),
                    'rating': float(show.get('rating', 0))
                })
                
            if len(recommendations) >= n_recommendations:
                break
                
        return recommendations
        
if __name__ == "__main__":
    # Example usage
    recommender = KNNRecommender()
    recommender.load_data()
    recommender.fit()
    
    # Example: Get similar shows
    show_id = 1  # Replace with actual show ID
    similar_shows = recommender.get_similar_shows(show_id)
    print("Similar shows:", similar_shows)
    
    # Example: Get personalized recommendations
    user_ratings = {1: 5, 2: 3, 3: 4}  # Replace with actual user ratings
    recommendations = recommender.get_recommendations(user_ratings)
    print("Recommendations:", recommendations) 