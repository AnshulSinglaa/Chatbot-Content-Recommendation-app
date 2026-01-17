"""
RAG (Retrieval-Augmented Generation) pipeline for movie recommendations.
Uses LangChain for LLM integration and context management.
"""
import os
from typing import List, Dict, Any
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage
from vector_store import VectorStore
from mood_filter import MoodFilter

# Load environment variables from .env file
load_dotenv()


class RAGPipeline:
    """RAG pipeline for generating movie recommendations with explanations."""
    
    def __init__(self, vector_store: VectorStore, llm_model: str = "llama-3.1-8b-instant", temperature: float = 0.7):
        """
        Initialize the RAG pipeline.
        
        Args:
            vector_store: Initialized VectorStore instance
            llm_model: Groq model name (default: llama-3.1-70b-versatile)
            temperature: LLM temperature for response generation
        """
        self.vector_store = vector_store
        self.llm_model = llm_model
        self.temperature = temperature
        self.llm = None
        self.conversation_history = []
        self.mood_filter = MoodFilter()
        
        # Initialize LLM with Groq
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError(
                "GROQ_API_KEY not found in environment variables. "
                "Please set it using:\n"
                "  Windows: set GROQ_API_KEY=your-key-here\n"
                "  Linux/Mac: export GROQ_API_KEY=your-key-here\n"
                "Or create a .env file with: GROQ_API_KEY=your-key-here"
            )
        
        # Initialize Groq LLM
        self.llm = ChatGroq(
            model=llm_model,
            temperature=temperature,
            groq_api_key=api_key
        )
    
    def retrieve_movies(self, query: str, k: int = 10) -> List[Dict[str, Any]]:
        """
        Retrieve relevant movies from vector store.
        
        Args:
            query: User query
            k: Number of movies to retrieve
            
        Returns:
            List of retrieved movie documents
        """
        results = self.vector_store.search(query, k=k)
        return [doc for doc, score in results]
    
    def format_movie_context(self, movies: List[Dict[str, Any]]) -> str:
        """
        Format retrieved movies into context string for LLM.
        
        Args:
            movies: List of movie documents
            
        Returns:
            Formatted context string
        """
        context_parts = []
        for i, movie in enumerate(movies, 1):
            context_parts.append(
                f"{i}. Title: {movie['title']}\n"
                f"   Genres: {movie['genres']}\n"
                f"   Rating: {movie['rating']:.1f}/10\n"
                f"   Overview: {movie['overview']}\n"
            )
        return "\n".join(context_parts)
    
    def generate_recommendations(
        self, 
        query: str, 
        num_recommendations: int = 5,
        use_history: bool = True
    ) -> Dict[str, Any]:
        """
        Generate movie recommendations using RAG.
        
        Args:
            query: User query
            num_recommendations: Number of movies to recommend
            use_history: Whether to use conversation history
            
        Returns:
            Dictionary with recommendations and explanations
        """
        # Detect mood from query
        detected_moods = self.mood_filter.detect_mood(query)
        
        # Retrieve relevant movies
        retrieved_movies = self.retrieve_movies(query, k=15)  # Retrieve more, then filter
        
        # Apply mood-based filtering if moods detected
        if detected_moods and len(detected_moods) > 0:
            retrieved_movies = self.mood_filter.filter_by_mood(retrieved_movies, detected_moods)
            # If filtering removed too many, fall back to original results
            if len(retrieved_movies) < 3:
                retrieved_movies = self.retrieve_movies(query, k=15)
        
        if not retrieved_movies:
            return {
                'recommendations': [],
                'message': "I couldn't find any movies matching your query. Please try a different search."
            }
        
        # Format context
        movie_context = self.format_movie_context(retrieved_movies)
        
        # Build prompt with conversation history
        system_prompt = """You are a friendly and knowledgeable movie recommendation assistant. 
Your task is to recommend movies based on user queries and provide thoughtful explanations.

Given a user's query and a list of relevant movies, you should:
1. Select 3-5 most appropriate movies from the list
2. Provide a brief, friendly explanation for each recommendation
3. Consider the user's mood, preferences, and query context
4. Maintain a conversational and helpful tone

Format your response as:
- Movie Title (Genre) - Rating: X.X/10
  Explanation: [Why this movie fits the user's request]

If the user's query is vague or unclear, ask for clarification while still providing some recommendations."""
        
        # Include conversation history if enabled
        if use_history and self.conversation_history:
            history_context = "\n\nPrevious conversation:\n"
            for msg in self.conversation_history[-4:]:  # Last 4 messages
                history_context += f"{msg}\n"
        else:
            history_context = ""
        
        user_prompt = f"""User Query: {query}
{history_context}

Relevant Movies:
{movie_context}

Please recommend {num_recommendations} movies that best match the user's query. 
Provide a brief explanation for each recommendation explaining why it fits their request."""
        
        # Generate response
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        response = self.llm.invoke(messages)
        recommendation_text = response.content
        
        # Update conversation history
        self.conversation_history.append(f"User: {query}")
        self.conversation_history.append(f"Assistant: {recommendation_text}")
        
        # Parse recommendations (simple extraction)
        recommendations = self._parse_recommendations(recommendation_text, retrieved_movies)
        
        return {
            'recommendations': recommendations,
            'raw_response': recommendation_text,
            'retrieved_count': len(retrieved_movies)
        }
    
    def _parse_recommendations(
        self, 
        response_text: str, 
        retrieved_movies: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Parse LLM response to extract structured recommendations.
        
        Args:
            response_text: LLM response text
            retrieved_movies: List of retrieved movies
            
        Returns:
            List of recommendation dictionaries
        """
        recommendations = []
        movie_titles = {movie['title'].lower(): movie for movie in retrieved_movies}
        
        # Try to extract movie titles from response
        lines = response_text.split('\n')
        current_movie = None
        current_explanation = []
        
        for line in lines:
            line_lower = line.lower().strip()
            
            # Check if line contains a movie title
            for title_lower, movie_data in movie_titles.items():
                if title_lower in line_lower and len(title_lower) > 3:  # Avoid short matches
                    # Save previous movie if exists
                    if current_movie:
                        recommendations.append({
                            'title': current_movie['title'],
                            'genres': current_movie['genres'],
                            'rating': current_movie['rating'],
                            'popularity': current_movie['popularity'],
                            'overview': current_movie['overview'],
                            'explanation': ' '.join(current_explanation) if current_explanation else "Recommended based on your preferences."
                        })
                    
                    current_movie = movie_data
                    current_explanation = []
                    break
            
            # Collect explanation text
            if current_movie and ('explanation' in line_lower or ':' in line):
                explanation = line.split(':', 1)[-1].strip()
                if explanation:
                    current_explanation.append(explanation)
        
        # Add last movie
        if current_movie:
            recommendations.append({
                'title': current_movie['title'],
                'genres': current_movie['genres'],
                'rating': current_movie['rating'],
                'popularity': current_movie['popularity'],
                'overview': current_movie['overview'],
                'explanation': ' '.join(current_explanation) if current_explanation else "Recommended based on your preferences."
            })
        
        # If parsing failed, use top retrieved movies with raw response
        if not recommendations:
            for movie in retrieved_movies[:5]:
                recommendations.append({
                    'title': movie['title'],
                    'genres': movie['genres'],
                    'rating': movie['rating'],
                    'popularity': movie['popularity'],
                    'overview': movie['overview'],
                    'explanation': response_text[:200] + "..." if len(response_text) > 200 else response_text
                })
        
        return recommendations[:5]  # Limit to 5
    
    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []
