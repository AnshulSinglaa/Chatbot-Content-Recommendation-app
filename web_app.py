import os
import sys
from pathlib import Path
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

# Add src to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent / "src"))

from app import MovieRecommendationBot
from cache import get_cache, set_cache, generate_query_hash
app = FastAPI(title="Movie Recommendation Chatbot")

# Initialize the bot
bot = MovieRecommendationBot()
# We need to initialize it. Data path is relative to the root where this script runs.
# Reusing the logic from app.py main()
DATA_PATH = os.getenv("DATA_PATH", "data/tmdb_top_movies_cleaned.csv")

print("Initializing Chatbot...")
if not os.path.exists(DATA_PATH):
    print(f"Warning: Dataset not found at {DATA_PATH}. Run 'python download_data.py' first.")
else:
    bot.initialize(DATA_PATH, force_rebuild=False)

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

class ChatRequest(BaseModel):
    message: str
    use_history: bool = True

class Recommendation(BaseModel):
    title: str
    genres: str
    rating: float
    explanation: str
    overview: Optional[str] = None

class ChatResponse(BaseModel):
    recommendations: List[Recommendation]
    message: Optional[str] = None

@app.get("/")
async def read_root():
    return FileResponse("static/index.html")

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    if not bot.initialized:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    try:
        # Check cache for generic queries if history is not used
        # We assume queries under 20 words are generic enough for caching
        # Skip caching for very specific or follow up queries (handled by use_history and length check)
        is_generic_query = not request.use_history and len(request.message.split()) < 20
        cache_key = None
        
        if is_generic_query:
            query_hash = generate_query_hash(request.message)
            cache_key = f"llm:{query_hash}"
            cached_response = get_cache(cache_key)
            
            if cached_response:
                # Return cached response directly
                return ChatResponse(**cached_response)

        # The bot's rag_pipeline.generate_recommendations returns a dict
        result = bot.rag_pipeline.generate_recommendations(
            request.message, 
            num_recommendations=5,
            use_history=request.use_history
        )
        
        response_data = ChatResponse(
            recommendations=[],
            message=result.get('message')
        )
        
        if result.get('recommendations'):
            # Transform to our pydantic model
            for rec in result['recommendations']:
                response_data.recommendations.append(Recommendation(
                    title=rec['title'],
                    genres=rec.get('genres', ''),
                    rating=rec.get('rating', 0.0),
                    explanation=rec.get('explanation', ''),
                    overview=rec.get('overview', '')
                ))
                
        # Save to cache if applicable
        if is_generic_query and cache_key:
            # Cache the response for 1 hour (3600 seconds)
            # Use model_dump() or dict() depending on pydantic version. We'll use dict() as it's safe for older versions.
            try:
                cache_data = response_data.model_dump()
            except AttributeError:
                cache_data = response_data.dict()
            set_cache(cache_key, cache_data, expiry=3600)
            
        return response_data
        
    except Exception as e:
        print(f"Error processing request: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/clear")
async def clear_history():
    if bot.initialized and bot.rag_pipeline:
        bot.rag_pipeline.clear_history()
    return {"status": "success", "message": "History cleared"}

@app.get("/health")
async def health_check():
    return {"status": "online", "initialized": bot.initialized}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("web_app:app", host="0.0.0.0", port=8000, reload=True)
