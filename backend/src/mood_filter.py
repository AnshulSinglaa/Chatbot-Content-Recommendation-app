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
    
    # Words that negate the following mood keyword
    NEGATION_WORDS = {'not', "don't", "dont", 'no', 'never', 'without', 'hardly', "doesn't", "isn't", "wasn't"}

    def detect_mood(self, query: str) -> List[str]:
        """
        Detect mood(s) from user query, accounting for negation.
        
        "I want a happy movie"         → ['funny']
        "I don't want a happy movie"   → [] (funny excluded)
        
        Args:
            query: User query string
            
        Returns:
            List of detected moods
        """
        query_lower = query.lower()
        words = query_lower.split()
        detected_moods = []
        negated_moods = []
        
        for mood, keywords in self.MOOD_KEYWORDS.items():
            for keyword in keywords:
                if keyword in query_lower:
                    # Check if a negation word appears within 3 words before the keyword
                    try:
                        # Find keyword position in word list
                        kw_indices = [i for i, w in enumerate(words) if keyword in w]
                        is_negated = False
                        for ki in kw_indices:
                            lookback = words[max(0, ki - 3):ki]
                            if any(neg in lookback for neg in self.NEGATION_WORDS):
                                is_negated = True
                                break
                        
                        if is_negated:
                            negated_moods.append(mood)
                        else:
                            detected_moods.append(mood)
                    except (ValueError, IndexError):
                        detected_moods.append(mood)
                    break  # One keyword match per mood is enough
        
        # Remove negated moods from detected moods
        final_moods = [m for m in detected_moods if m not in negated_moods]
        
        return final_moods if final_moods else ['relaxed']  # Default
    
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
