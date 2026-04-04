import os
import sys
import asyncio
import threading
import logging
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Request, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field, EmailStr
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
import sqlite3
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

logger = logging.getLogger(__name__)

# Add src to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent / "src"))

from bot import MovieRecommendationBot
from cache import get_cache, set_cache, generate_query_hash

app = FastAPI(title="Movie Recommendation Chatbot")

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ---------------------------------------------------------------------------
# Bot singleton with thread safety (issue #5)
# NOTE: FAISS IndexFlatIP is read-only after build, so concurrent searches
# are safe.  The threading lock guards initialisation and conversation
# history mutations only.
# ---------------------------------------------------------------------------
bot = MovieRecommendationBot()
bot_lock = threading.Lock()

# ---------------------------------------------------------------------------
# Authentication Setup
# ---------------------------------------------------------------------------
SECRET_KEY = os.getenv("SECRET_KEY", "cineguide-super-secret-jwt-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

def init_db():
    with sqlite3.connect("users.db", check_same_thread=False) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

def get_db():
    conn = sqlite3.connect("users.db", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: sqlite3.Connection = Depends(get_db)):
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    if user is None:
        raise credentials_exception
    return dict(user)

DATA_PATH = os.getenv("DATA_PATH", "data/tmdb_top_movies_cleaned.csv")


@app.on_event("startup")
async def startup_init():
    """Initialise the bot at startup instead of at module-import time."""
    init_db()
    if not os.path.exists(DATA_PATH):
        logger.warning(f"Dataset not found at {DATA_PATH}. Run 'python download_data.py' first.")
        return
    # Run the blocking initialisation in a thread so it doesn't block the
    # event loop during startup.
    await asyncio.to_thread(_init_bot)


def _init_bot():
    with bot_lock:
        logger.info("Initializing Chatbot...")
        bot.initialize(DATA_PATH, force_rebuild=False)
        logger.info("Chatbot initialized.")


# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# ---------------------------------------------------------------------------
# Pydantic models (Auth and Chat)
# ---------------------------------------------------------------------------
class UserSignup(BaseModel):
    name: str
    email: EmailStr
    password: str = Field(..., min_length=6)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    created_at: str
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=500,
                         description="User message (1-500 characters)")
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


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@app.get("/")
async def read_root():
    return FileResponse("static/index.html")


@app.post("/api/v1/auth/signup", response_model=Token)
async def signup(user: UserSignup, db: sqlite3.Connection = Depends(get_db)):
    existing_user = db.execute("SELECT id FROM users WHERE email = ?", (user.email,)).fetchone()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(user.password)
    db.execute(
        "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
        (user.name, user.email, hashed_password)
    )
    db.commit()
    
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/api/v1/auth/login", response_model=Token)
async def login(user: UserLogin, db: sqlite3.Connection = Depends(get_db)):
    db_user = db.execute("SELECT * FROM users WHERE email = ?", (user.email,)).fetchone()
    if not db_user or not verify_password(user.password, db_user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": db_user["email"]})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/v1/auth/me", response_model=UserResponse)
async def read_users_me(current_user: dict = Depends(get_current_user)):
    return {
        "id": current_user["id"],
        "name": current_user["name"],
        "email": current_user["email"],
        "created_at": current_user["created_at"],
    }

@app.post("/api/v1/chat", response_model=ChatResponse)
@limiter.limit("10/minute")
async def chat(request: Request, body: ChatRequest, current_user: dict = Depends(get_current_user)):
    if not bot.initialized:
        raise HTTPException(status_code=503, detail="System not initialized")

    # sanitize — strip extra whitespace
    body.message = body.message.strip()

    try:
        # Check cache for generic queries
        is_generic_query = not body.use_history and len(body.message.split()) < 20
        cache_key = None

        if is_generic_query:
            query_hash = generate_query_hash(body.message)
            cache_key = f"llm:{query_hash}"
            cached_response = get_cache(cache_key)
            if cached_response:
                return ChatResponse(**cached_response)

        # Run blocking RAG call in a thread (issue #4 — async correctness)
        result = await asyncio.to_thread(
            _generate_recommendations,
            body.message,
            body.use_history,
        )

        response_data = ChatResponse(
            recommendations=[],
            message=result.get('message')
        )

        if result.get('recommendations'):
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
            try:
                cache_data = response_data.model_dump()
            except AttributeError:
                cache_data = response_data.dict()
            set_cache(cache_key, cache_data, expiry=3600)

        return response_data

    except Exception as e:
        logger.error(f"Error processing request: {e}")
        raise HTTPException(status_code=500, detail="An internal error occurred. Please try again later.")


def _generate_recommendations(message: str, use_history: bool) -> dict:
    """Wrapper that acquires the bot lock for history mutations."""
    with bot_lock:
        return bot.rag_pipeline.generate_recommendations(
            message,
            num_recommendations=5,
            use_history=use_history,
        )


@app.post("/api/v1/clear")
async def clear_history(current_user: dict = Depends(get_current_user)):
    with bot_lock:
        if bot.initialized and bot.rag_pipeline:
            bot.rag_pipeline.clear_history()
    return {"status": "success", "message": "History cleared"}


@app.get("/api/v1/health")
async def health_check():
    return {"status": "online", "initialized": bot.initialized}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("web_app:app", host="0.0.0.0", port=8000, reload=True)
