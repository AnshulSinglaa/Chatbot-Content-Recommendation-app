# 🎬 Movie Recommendation Chatbot

A conversational movie recommendation system powered by **RAG (Retrieval-Augmented Generation)**. Ask in plain English — get personalized movie recommendations with explanations.

> **Live Demo:** [🔗 Coming Soon — link will be added after deployment]

---

## ✨ Features

- 🔍 **Semantic Search** — Understands meaning, not just keywords (FAISS + SentenceTransformers)
- 🤖 **LLM-Powered Responses** — Uses Groq (Llama 3.1) to generate natural explanations
- 🎭 **Mood Detection** — Automatically detects your mood and filters movies accordingly
- 💬 **Conversation History** — Maintains context across multiple queries
- ⚡ **Fast Retrieval** — FAISS index persisted to disk, loads in seconds after first build
- 🌐 **Web UI + REST API** — FastAPI backend with a clean chat interface

---

## 🏗️ Architecture
User Query
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
├── web_app.py              # FastAPI app (main entry for web/API)
├── app.py                  # CLI entry point
├── requirements.txt        # Dependencies
├── .env.example            # Environment variable template
├── download_data.py        # Script to download the dataset
└── src/
├── data_loader.py      # TMDB CSV loading & preprocessing
├── vector_store.py     # FAISS index: build, save, load, search
├── rag_pipeline.py     # RAG chain: retrieve → augment → generate
└── mood_filter.py      # Mood detection & genre-mood filtering

---

## ⚙️ Setup & Installation

### Prerequisites
- Python 3.8+
- A free [Groq API key](https://console.groq.com)

### 1. Clone the repo
```bash
git clone https://github.com/AnshulSinglaa/Chatbot-Content-Recommendation-app.git
cd Chatbot-Content-Recommendation-app
```

### 2. Create a virtual environment
```bash
python -m venv venv
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up environment variables
```bash
cp .env.example .env
# Open .env and add your GROQ_API_KEY
```

### 5. Download the dataset
```bash
python download_data.py
```

### 6. Run the web app
```bash
python web_app.py
```
Open [http://localhost:8000](http://localhost:8000) in your browser.

---

## 🖥️ CLI Mode
```bash
python app.py
python app.py --rebuild   # force rebuild vector store
```

---

## 🔌 API Reference

### `POST /chat`
```json
{ "message": "Suggest a feel-good movie", "use_history": true }
```
**Response:**
```json
{
  "recommendations": [
    {
      "title": "The Intouchables",
      "genres": "Drama, Comedy",
      "rating": 8.5,
      "explanation": "A heartwarming story perfect for when you need something uplifting..."
    }
  ]
}
```

### `GET /health`  →  `{ "status": "online", "initialized": true }`
### `POST /clear`  →  Clears conversation history

---

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| Embeddings | `all-MiniLM-L6-v2` (SentenceTransformers) |
| Vector DB | FAISS (cosine similarity via IndexFlatIP) |
| LLM | Groq — Llama 3.1 8B Instant |
| LLM Framework | LangChain |
| Backend | FastAPI + Uvicorn |
| Dataset | TMDB Top Movies (~9,800 movies) |

---

## 🚀 Deployment

Deployed on **Render** — Live URL: [add after deploy]

To deploy your own:
1. Push to GitHub
2. New Web Service on [render.com](https://render.com) → connect repo
3. Build command: `pip install -r requirements.txt`
4. Start command: `python download_data.py && python web_app.py`
5. Add `GROQ_API_KEY` in Render environment variables

---

## 🔮 Planned Improvements

- [ ] Agentic RAG with LangGraph + Tavily web search
- [ ] User feedback (like/dislike) to improve recommendations
- [ ] Structured JSON output mode to fix LLM response parsing
- [ ] Recommendation history per session

---

## 📄 License

MIT — free to use and modify.
