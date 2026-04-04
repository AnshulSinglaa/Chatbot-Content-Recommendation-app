# 🎬 CineGuide AI — Movie Recommendation Chatbot

A conversational movie recommendation system powered by 
RAG (Retrieval-Augmented Generation). Ask in plain English 
— get personalized movie recommendations with explanations.

> **Live Demo:** [https://cineguide-ai.onrender.com](https://cineguide-ai.onrender.com)  
> ⚠️ Backend may take 30 seconds to wake on first request (free tier)

---

## ✨ Features

- 🔍 **Semantic Search** — Understands meaning, not just keywords 
  (FAISS + SentenceTransformers)
- 🤖 **LLM-Powered Responses** — Groq Llama 3.1 generates natural 
  explanations
- 🎭 **Mood Detection** — Detects mood from query and filters movies
- 💬 **Conversation History** — Maintains context with sliding window
- ⚡ **Fast Retrieval** — FAISS index persisted to disk
- 🔐 **JWT Authentication** — Secure signup/login with bcrypt passwords
- 🛡️ **Rate Limiting** — 10 requests/minute per IP via slowapi
- 🌐 **Web UI + REST API** — FastAPI backend with React frontend

---

## 🏗️ Architecture
User Query
│
▼
JWT Auth Middleware
│
▼
Input Validation (Pydantic — max 500 chars)
│
▼
Rate Limiter (10 req/min per IP)
│
▼
Mood Detection (MoodFilter)
│
▼
Semantic Search (FAISS + SentenceTransformers)
│  → retrieves top-15 relevant movies
▼
RAG Pipeline (LangChain + Groq Llama 3.1)
│  → query + movie context → LLM → recommendations
▼
Structured Response (title, genre, rating, explanation)

---

## 🗂️ Project Structure
├── backend/
│   ├── web_app.py          # FastAPI app — main web entry point
│   ├── app.py              # CLI entry point
│   ├── cache.py            # In-memory cache (get/set/hash)
│   ├── download_data.py    # Dataset verification script
│   ├── requirements.txt    # Pinned dependencies
│   ├── render.yaml         # Render deployment blueprint
│   └── src/
│       ├── bot.py          # MovieRecommendationBot class
│       ├── data_loader.py  # TMDB CSV loading & preprocessing
│       ├── vector_store.py # FAISS index: build, save, load, search
│       ├── rag_pipeline.py # RAG: retrieve → augment → generate
│       └── mood_filter.py  # Mood detection & genre filtering
│
└── frontend/
├── src/
│   ├── components/     # React components
│   ├── context/        # Auth context
│   └── utils/          # API client
├── index.html
└── package.json

---

## ⚙️ Setup & Installation

### Prerequisites
- Python 3.11+
- Node.js 18+
- A free [Groq API key](https://console.groq.com)

### 1. Clone the repo
```bash
git clone https://github.com/AnshulSinglaa/Chatbot-Content-Recommendation-app.git
cd Chatbot-Content-Recommendation-app
```

### 2. Backend setup
```bash
cd backend
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate

pip install -r requirements.txt
```

### 3. Environment variables
```bash
cp .env.example .env
```

Open `.env` and fill in:
GROQ_API_KEY=your_groq_key_here
GROQ_MODEL=llama-3.1-8b-instant
SECRET_KEY=your_random_secret_here

Generate a secure SECRET_KEY:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 4. Get the dataset
Place `tmdb_top_movies_cleaned.csv` inside `backend/data/`  
Then verify:
```bash
python download_data.py
```

### 5. Run backend
```bash
uvicorn web_app:app --host 0.0.0.0 --port 8000 --reload
```

### 6. Frontend setup
```bash
cd ../frontend
npm install
npm run dev
```

Frontend: [http://localhost:3000](http://localhost:3000)  
Backend: [http://localhost:8000](http://localhost:8000)

---

## 🖥️ CLI Mode
```bash
cd backend
python app.py
python app.py --rebuild   # force rebuild vector store
```

---

## 🔌 API Reference

All endpoints are prefixed with `/api/v1/`

### Auth

| Method | Endpoint | Auth Required | Description |
|---|---|---|---|
| POST | `/api/v1/auth/signup` | No | Register new user |
| POST | `/api/v1/auth/login` | No | Login, returns JWT |
| GET | `/api/v1/auth/me` | Yes | Get current user |

### Chat

| Method | Endpoint | Auth Required | Description |
|---|---|---|---|
| POST | `/api/v1/chat` | Yes | Get recommendations |
| POST | `/api/v1/clear` | Yes | Clear conversation history |
| GET | `/api/v1/health` | No | System health check |

### Example — Chat Request
```json
POST /api/v1/chat
Authorization: Bearer <your_jwt_token>

{
  "message": "Suggest a feel-good movie for tonight",
  "use_history": true
}
```

### Example — Chat Response
```json
{
  "recommendations": [
    {
      "title": "The Intouchables",
      "genres": "Drama, Comedy",
      "rating": 8.5,
      "explanation": "A heartwarming story perfect for when you 
                      need something uplifting..."
    }
  ]
}
```

---

## 🌍 Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `GROQ_API_KEY` | Yes | — | From console.groq.com |
| `GROQ_MODEL` | No | `llama-3.1-8b-instant` | Groq model name |
| `SECRET_KEY` | Yes | — | JWT signing secret |
| `DATA_PATH` | No | `data/tmdb_top_movies_cleaned.csv` | Dataset path |
| `VECTOR_STORE_PATH` | No | `vector_store/faiss_index` | FAISS index path |

---

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| Embeddings | `all-MiniLM-L6-v2` (SentenceTransformers) |
| Vector DB | FAISS (cosine similarity via IndexFlatIP) |
| LLM | Groq — Llama 3.1 8B Instant |
| LLM Framework | LangChain |
| Backend | FastAPI + Uvicorn |
| Auth | JWT + bcrypt (passlib + python-jose) |
| Rate Limiting | slowapi |
| Frontend | React + Vite + Tailwind CSS |
| Dataset | TMDB Top Movies (~9,800 movies) |

---

## 🚀 Deployment

### Backend — Render
1. Push to GitHub
2. New Web Service on [render.com](https://render.com) → connect repo
3. Root directory: `backend`
4. Build command: `pip install -r requirements.txt`
5. Start command:
```bash
python download_data.py && uvicorn web_app:app --host 0.0.0.0 --port $PORT
```
6. Add environment variables in Render dashboard:

| Variable | Value |
|---|---|
| `GROQ_API_KEY` | your key |
| `SECRET_KEY` | generated random string |
| `GROQ_MODEL` | `llama-3.1-8b-instant` |
| `VECTOR_STORE_PATH` | `/opt/render/project/src/vector_store` |

### Frontend — Vercel
1. New Project on [vercel.com](https://vercel.com) → connect repo
2. Root directory: `frontend`
3. Build command: `npm run build`
4. Add environment variable:
`VITE_API_URL=https://your-backend.onrender.com`

---

## 🔮 Planned Improvements

- [ ] Agentic RAG with LangGraph + Tavily web search
- [ ] PostgreSQL + Redis for production scaling
- [ ] Pinecone for cloud-hosted vector search
- [ ] User feedback — like/dislike to improve recommendations
- [ ] Test coverage with pytest

---

## 📄 License

MIT — free to use and modify.
