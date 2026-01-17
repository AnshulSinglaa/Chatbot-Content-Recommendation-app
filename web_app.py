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

app = FastAPI(title="Movie Recommendation Chatbot")

# Initialize the bot
bot = MovieRecommendationBot()
# We need to initialize it. Data path is relative to the root where this script runs.
# Reusing the logic from app.py main()
data_path = "data/tmdb_top_movies_cleaned.csv"
vector_store_path = "vector_store/faiss_index"

print("Initializing Chatbot...")
if not os.path.exists(data_path):
    print(f"Error: Dataset not found at {data_path}")
    # In a real app we might want to fail harder, but for now let's just print
else:
    # Check if we should force rebuild (could be an env var or arg, but acting simple here)
    bot.initialize(data_path, force_rebuild=False)

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
