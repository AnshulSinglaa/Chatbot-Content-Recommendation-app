"""
Main application entry point for the Movie Recommendation Chatbot.
Provides a CLI interface for interacting with the RAG-based recommendation system.
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from bot import MovieRecommendationBot


def main():
    """Main entry point."""
    bot = MovieRecommendationBot()
    
    # Check if vector store exists
    vector_store_path = "vector_store/faiss_index"
    force_rebuild = False
    
    if len(sys.argv) > 1 and sys.argv[1] == "--rebuild":
        force_rebuild = True
        print("Rebuilding vector store...")
    
    # Initialize
    data_path = "data/tmdb_top_movies_cleaned.csv"
    if not os.path.exists(data_path):
        print(f"Error: Dataset not found at {data_path}")
        print("Please ensure the CSV file is in the data/ directory.")
        sys.exit(1)
    
    bot.initialize(data_path, force_rebuild=force_rebuild)
    
    # Start chat
    bot.chat()


if __name__ == "__main__":
    main()
