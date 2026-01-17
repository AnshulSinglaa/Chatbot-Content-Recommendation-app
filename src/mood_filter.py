"""
Mood-based filtering for movie recommendations.
Maps user queries to mood categories and filters movies accordingly.
"""
from typing import List, Dict, Any


class MoodFilter:
    """Filters movies based on mood categories."""
    
    # Mood keywords mapping
    MOOD_KEYWORDS = {
        'relaxed': ['relax', 'chill', 'calm', 'peaceful', 'easy', 'light', 'gentle', 'soothing'],
        'inspiring': ['inspire', 'motivational', 'uplifting', 'empowering', 'encouraging', 'hopeful'],
        'emotional': ['emotional', 'touching', 'heartfelt', 'moving', 'sentimental', 'tear'],
        'energetic': ['energetic', 'exciting', 'thrilling', 'action', 'adrenaline', 'intense'],
        'funny': ['funny', 'comedy', 'humor', 'laugh', 'hilarious', 'comic'],
        'thoughtful': ['thoughtful', 'deep', 'philosophical', 'meaningful', 'profound', 'contemplative'],
        'romantic': ['romantic', 'love', 'romance', 'sweet', 'heartwarming', 'charming'],
        'dark': ['dark', 'gritty', 'serious', 'intense', 'dramatic', 'heavy']
    }
    
    # Genre to mood mapping
    GENRE_MOOD_MAP = {
        'Comedy': ['funny', 'relaxed'],
        'Drama': ['emotional', 'thoughtful'],
        'Action': ['energetic'],
        'Romance': ['romantic', 'emotional'],
        'Thriller': ['energetic', 'dark'],
        'Horror': ['dark', 'energetic'],
        'Family': ['relaxed', 'inspiring'],
        'Animation': ['relaxed', 'funny'],
        'Documentary': ['thoughtful', 'inspiring']
    }
    
    def detect_mood(self, query: str) -> List[str]:
        """
        Detect mood(s) from user query.
        
        Args:
            query: User query string
            
        Returns:
            List of detected moods
        """
        query_lower = query.lower()
        detected_moods = []
        
        for mood, keywords in self.MOOD_KEYWORDS.items():
            if any(keyword in query_lower for keyword in keywords):
                detected_moods.append(mood)
        
        return detected_moods if detected_moods else ['relaxed']  # Default
    
    def filter_by_mood(self, movies: List[Dict[str, Any]], moods: List[str]) -> List[Dict[str, Any]]:
        """
        Filter movies based on detected moods.
        
        Args:
            movies: List of movie documents
            moods: List of mood categories
            
        Returns:
            Filtered list of movies
        """
        if not moods:
            return movies
        
        scored_movies = []
        for movie in movies:
            score = 0
            genres = movie.get('genres', '').lower()
            
            # Check genre-mood alignment
            for mood in moods:
                # Check if any genre in the movie matches this mood
                for genre_name, mood_list in self.GENRE_MOOD_MAP.items():
                    if genre_name.lower() in genres and mood in mood_list:
                        score += 1
            
            # Boost score if movie description contains mood keywords
            overview = movie.get('overview', '').lower()
            for mood in moods:
                if mood in self.MOOD_KEYWORDS:
                    for keyword in self.MOOD_KEYWORDS[mood]:
                        if keyword in overview:
                            score += 0.5
            
            scored_movies.append((movie, score))
        
        # Sort by score and return top matches
        scored_movies.sort(key=lambda x: x[1], reverse=True)
        return [movie for movie, score in scored_movies if score > 0]
