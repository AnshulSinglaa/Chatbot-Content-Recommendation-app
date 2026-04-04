"""
RAG (Retrieval-Augmented Generation) pipeline for movie recommendations.
Uses LangChain for LLM integration and context management.
"""
import os
import time
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage
from vector_store import VectorStore
from mood_filter import MoodFilter
from cache import get_cache, set_cache

# Load environment variables from .env file
load_dotenv()


class RAGPipeline:
    """RAG pipeline for generating movie recommendations with explanations."""
    
    def __init__(self, vector_store: VectorStore, llm_model: str = None, temperature: float = 0.7):
        """
        Initialize the RAG pipeline.
        
        Args:
            vector_store: Initialized VectorStore instance
            llm_model: Groq model name (default: from GROQ_MODEL env var or llama-3.1-8b-instant)
            temperature: LLM temperature for response generation
        """
        self.vector_store = vector_store
        self.llm_model = llm_model or os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
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
            model=self.llm_model,
            temperature=temperature,
            groq_api_key=api_key
        )
    
    def _invoke_llm_with_retry(self, messages, max_retries: int = 3) -> str:
        """
        Invoke the LLM with retry logic and exponential backoff.
        
        Args:
            messages: Chat messages to send
            max_retries: Maximum number of retry attempts
            
        Returns:
            LLM response text, or None if all retries fail
        """
        for attempt in range(max_retries):
            try:
                response = self.llm.invoke(messages)
                return response.content
            except Exception as e:
                wait_time = 2 ** attempt  # 1s, 2s, 4s
                logger.warning(f"LLM call failed (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(wait_time)
        
        logger.error("All LLM retry attempts failed.")
        return None
    
    # Minimum cosine similarity score to include a FAISS result
    MIN_RELEVANCE_SCORE = 0.3
    
    def retrieve_movies(self, query: str, k: int = 10) -> List[Dict[str, Any]]:
        """
        Retrieve relevant movies from vector store.
        
        Args:
            query: User query
            k: Number of movies to retrieve
            
        Returns:
            List of retrieved movie documents
        """
        try:
            results = self.vector_store.search(query, k=k)
            # Filter by minimum relevance score to avoid low-quality results
            filtered = [doc for doc, score in results if score >= self.MIN_RELEVANCE_SCORE]
            # If filtering removed everything, return top results regardless
            return filtered if filtered else [doc for doc, score in results[:k]]
        except Exception as e:
            logger.error(f"FAISS search failed: {e}")
            return []
    
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
        # Check cache for mood detection results
        mood_cache_key = f"mood:{query.lower().strip()}"
        cached_mood = get_cache(mood_cache_key)
        
        if cached_mood and "moods" in cached_mood:
            detected_moods = cached_mood["moods"]
        else:
            # Detect mood from query
            detected_moods = self.mood_filter.detect_mood(query)
            # Cache mood detection results for 24 hours (86400 seconds)
            set_cache(mood_cache_key, {"moods": detected_moods}, expiry=86400)
        
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
        
        # Generate response with retry logic
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        recommendation_text = self._invoke_llm_with_retry(messages)
        
        # Graceful fallback: if LLM fails, return retrieved movies without LLM explanation
        if recommendation_text is None:
            logger.warning("LLM unavailable — returning raw retrieval results as fallback.")
            fallback_recs = []
            for movie in retrieved_movies[:5]:
                fallback_recs.append({
                    'title': movie['title'],
                    'genres': movie['genres'],
                    'rating': movie['rating'],
                    'popularity': movie.get('popularity', 0),
                    'overview': movie['overview'],
                    'explanation': 'Recommended based on semantic similarity to your query.'
                })
            return {
                'recommendations': fallback_recs,
                'raw_response': '(LLM unavailable — showing top matches)',
                'retrieved_count': len(retrieved_movies)
            }
        
        # Update conversation history and enforce a sliding window
        self.conversation_history.append(f"User: {query}")
        self.conversation_history.append(f"Assistant: {recommendation_text}")
        
        # Keep maximum of 10 messages (5 user-assistant turns)
        max_history_length = 10
        if len(self.conversation_history) > max_history_length:
            self.conversation_history = self.conversation_history[-max_history_length:]
        
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
