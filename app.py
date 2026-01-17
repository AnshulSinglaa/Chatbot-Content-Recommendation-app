"""
Main application entry point for the Movie Recommendation Chatbot.
Provides a CLI interface for interacting with the RAG-based recommendation system.
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from data_loader import DataLoader
from vector_store import VectorStore
from rag_pipeline import RAGPipeline


class MovieRecommendationBot:
    """Main chatbot application."""
    
    def __init__(self):
        """Initialize the chatbot."""
        self.data_loader = None
        self.vector_store = None
        self.rag_pipeline = None
        self.initialized = False
    
    def initialize(self, data_path: str = "data/tmdb_top_movies_cleaned.csv", 
                   force_rebuild: bool = False):
        """
        Initialize the system: load data, build/load vector store, initialize RAG.
        
        Args:
            data_path: Path to the movie dataset
            force_rebuild: If True, rebuild vector store even if it exists
        """
        print("=" * 60)
        print("Movie Recommendation Chatbot - Initializing...")
        print("=" * 60)
        
        # Load data
        print("\n[1/4] Loading movie data...")
        self.data_loader = DataLoader(data_path)
        df = self.data_loader.preprocess_data()
        documents = self.data_loader.get_movie_documents()
        
        # Initialize vector store
        print("\n[2/4] Setting up vector store...")
        self.vector_store = VectorStore()
        
        # Try to load existing index, or build new one
        if not force_rebuild and self.vector_store.load_index():
            print("✓ Loaded existing vector store")
        else:
            print("Building new vector store (this may take a few minutes)...")
            self.vector_store.initialize_model()
            embeddings = self.vector_store.create_embeddings(documents)
            self.vector_store.build_index(documents, embeddings)
            self.vector_store.save_index()
            print("✓ Vector store built and saved")
        
        # Initialize RAG pipeline
        print("\n[3/4] Initializing RAG pipeline...")
        try:
            self.rag_pipeline = RAGPipeline(self.vector_store)
            print("✓ RAG pipeline initialized")
        except ValueError as e:
            print(f"\n❌ Error: {e}")
            print("\nPlease set your Groq API key:")
            print("  Windows: set GROQ_API_KEY=your-key-here")
            print("  Linux/Mac: export GROQ_API_KEY=your-key-here")
            sys.exit(1)
        
        print("\n[4/4] System ready!")
        print("=" * 60)
        self.initialized = True
    
    def format_recommendation(self, rec: dict) -> str:
        """
        Format a single recommendation for display.
        
        Args:
            rec: Recommendation dictionary
            
        Returns:
            Formatted string
        """
        return f"""
🎬 {rec['title']}
   Genre: {rec['genres']}
   Rating: {rec['rating']:.1f}/10
   {rec['explanation']}
"""
    
    def chat(self):
        """Main chat loop."""
        if not self.initialized:
            print("Error: System not initialized. Call initialize() first.")
            return
        
        print("\n" + "=" * 60)
        print("Movie Recommendation Chatbot")
        print("=" * 60)
        print("\nI'm here to help you find the perfect movie!")
        print("You can ask me things like:")
        print("  - 'Suggest me a light movie for tonight, I'm tired'")
        print("  - 'Recommend a feel-good or inspirational movie'")
        print("  - 'I want a comedy movie to relax'")
        print("\nType 'quit', 'exit', or 'bye' to end the conversation.")
        print("Type 'clear' to clear conversation history.")
        print("-" * 60)
        
        while True:
            try:
                query = input("\nYou: ").strip()
                
                if not query:
                    continue
                
                if query.lower() in ['quit', 'exit', 'bye']:
                    print("\nThanks for using the Movie Recommendation Chatbot! Goodbye! 👋")
                    break
                
                if query.lower() == 'clear':
                    self.rag_pipeline.clear_history()
                    print("Conversation history cleared.")
                    continue
                
                # Generate recommendations
                print("\n🤔 Thinking...")
                result = self.rag_pipeline.generate_recommendations(query, num_recommendations=5)
                
                # Display results
                print("\n" + "=" * 60)
                print("Recommendations:")
                print("=" * 60)
                
                if result['recommendations']:
                    for i, rec in enumerate(result['recommendations'], 1):
                        print(f"\n{i}. {self.format_recommendation(rec)}")
                else:
                    print(result.get('message', 'No recommendations found.'))
                
                print("-" * 60)
                
            except KeyboardInterrupt:
                print("\n\nThanks for using the Movie Recommendation Chatbot! Goodbye! 👋")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                print("Please try again or type 'quit' to exit.")


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
