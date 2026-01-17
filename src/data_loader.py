"""
Data loading and preprocessing module for TMDB movies dataset.
"""
import pandas as pd
import os
from typing import List, Dict, Any


class DataLoader:
    """Handles loading and preprocessing of movie data."""
    
    def __init__(self, data_path: str):
        """
        Initialize the data loader.
        
        Args:
            data_path: Path to the CSV file containing movie data
        """
        self.data_path = data_path
        self.df = None
    
    def load_data(self) -> pd.DataFrame:
        """
        Load the movie dataset from CSV.
        
        Returns:
            DataFrame containing movie data
        """
        if not os.path.exists(self.data_path):
            raise FileNotFoundError(f"Dataset not found at {self.data_path}")
        
        self.df = pd.read_csv(self.data_path)
        print(f"Loaded {len(self.df)} movies from dataset")
        return self.df
    
    def preprocess_data(self) -> pd.DataFrame:
        """
        Preprocess the data: handle missing values and create combined text fields.
        
        Returns:
            Preprocessed DataFrame
        """
        if self.df is None:
            self.load_data()
        
        # Create a combined text field for better retrieval
        # Combine title, genres, and overview
        self.df['combined_text'] = (
            self.df['Title'].fillna('') + ' ' +
            self.df['Genres'].fillna('') + ' ' +
            self.df['Overview'].fillna('')
        )
        
        # Fill missing values
        self.df['Vote Average'] = self.df['Vote Average'].fillna(0.0)
        self.df['Popularity'] = self.df['Popularity'].fillna(0.0)
        self.df['Genres'] = self.df['Genres'].fillna('Unknown')
        self.df['Overview'] = self.df['Overview'].fillna('No description available')
        
        # Remove rows with missing titles
        self.df = self.df.dropna(subset=['Title'])
        
        print(f"Preprocessed {len(self.df)} movies")
        return self.df
    
    def get_movie_documents(self) -> List[Dict[str, Any]]:
        """
        Convert DataFrame to list of document dictionaries for vector store.
        
        Returns:
            List of movie documents with metadata
        """
        if self.df is None:
            self.preprocess_data()
        
        documents = []
        for idx, row in self.df.iterrows():
            doc = {
                'id': str(idx),
                'title': row['Title'],
                'text': row['combined_text'],
                'genres': row['Genres'],
                'overview': row['Overview'],
                'rating': float(row['Vote Average']),
                'popularity': float(row['Popularity']),
                'release_date': row.get('Release Date', 'Unknown'),
                'metadata': {
                    'title': row['Title'],
                    'genres': row['Genres'],
                    'rating': float(row['Vote Average']),
                    'popularity': float(row['Popularity']),
                    'release_date': row.get('Release Date', 'Unknown'),
                    'vote_count': int(row.get('Vote Count', 0))
                }
            }
            documents.append(doc)
        
        return documents
