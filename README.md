# Movie Recommendation Chatbot

A complete LLM-powered conversational movie recommendation system using Retrieval-Augmented Generation (RAG). This chatbot understands natural language queries and recommends movies with personalized explanations.

## Features

- 🎬 **Natural Language Understanding**: Ask for movies in plain English
- 🔍 **Semantic Search**: Uses embeddings to find relevant movies based on meaning, not just keywords
- 💬 **Conversational AI**: Maintains context across multiple queries
- 📊 **Smart Recommendations**: Provides 3-5 movie recommendations with explanations
- 🎯 **Context-Aware**: Understands mood, preferences, and follow-up questions
- 🎭 **Mood-Based Filtering**: Automatically detects and filters by mood (relaxed, inspiring, emotional, etc.)

## Example Queries

- "Suggest me a light movie for tonight, I'm tired"
- "Recommend a feel-good or inspirational movie"
- "I want a comedy movie to relax"
- "Find me a thriller with a twist ending"
- "What are some good family movies?"

## Project Structure

```
.
├── app.py                          # Main application entry point
├── requirements.txt                # Python dependencies
├── README.md                       # This file
├── data/
│   └── tmdb_top_movies_cleaned.csv # Movie dataset
├── vector_store/                   # FAISS index storage
│   ├── faiss_index.index
│   └── faiss_index.pkl
└── src/
    ├── data_loader.py              # Data loading and preprocessing
    ├── vector_store.py             # Embedding generation and FAISS index
    ├── rag_pipeline.py             # RAG pipeline with LangChain
    └── mood_filter.py              # Mood-based filtering (bonus feature)
```

## Installation

### Prerequisites

- Python 3.8 or higher
- OpenAI API key (for LLM generation)

### Step 1: Clone or Navigate to Project Directory

```bash
cd "C:\Users\singl\Downloads\Chatbot Content Recommendation app"
```

### Step 2: Create Virtual Environment (Recommended)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Verify Setup (Optional)

Run the verification script to check if everything is configured correctly:

```bash
python verify_setup.py
```

### Step 5: Set OpenAI API Key

**Windows (PowerShell):**
```powershell
$env:OPENAI_API_KEY="your-api-key-here"
```

**Windows (Command Prompt):**
```cmd
set OPENAI_API_KEY=your-api-key-here
```

**Linux/Mac:**
```bash
export OPENAI_API_KEY=your-api-key-here
```

**Or create a `.env` file:**
```
OPENAI_API_KEY=your-api-key-here
```

## Usage

### First Run (Build Vector Store)

On the first run, the system will:
1. Load the movie dataset
2. Generate embeddings for all movies
3. Build and save the FAISS index

This process may take 5-10 minutes depending on your system.

```bash
python app.py
```

### Subsequent Runs

After the first run, the vector store is saved and will load automatically:

```bash
python app.py
```

### Rebuild Vector Store

To rebuild the vector store from scratch:

```bash
python app.py --rebuild
```

### Interactive Chat

Once the system is initialized, you can start chatting:

```
You: Suggest me a light movie for tonight, I'm tired

🤔 Thinking...

============================================================
Recommendations:
============================================================

1. 
🎬 The Grand Budapest Hotel
   Genre: Comedy, Drama
   Rating: 8.1/10
   This whimsical comedy is perfect for when you're tired - it's visually delightful and not too demanding...

2. 
🎬 Paddington
   Genre: Family, Comedy
   Rating: 7.5/10
   A heartwarming family film that's gentle and uplifting...
```

### Commands

- Type your query naturally
- `quit`, `exit`, or `bye` - Exit the chatbot
- `clear` - Clear conversation history

## How It Works

### 1. Data Preprocessing
- Loads TMDB movie dataset
- Combines title, genres, and overview into searchable text
- Handles missing values

### 2. Embedding Generation
- Uses SentenceTransformers (`all-MiniLM-L6-v2`) to create embeddings
- Each movie is converted to a 384-dimensional vector
- Embeddings capture semantic meaning of movie descriptions

### 3. Vector Store (FAISS)
- Stores all movie embeddings in a FAISS index
- Enables fast similarity search (cosine similarity)
- Index is saved to disk for quick loading

### 4. RAG Pipeline
- **Retrieval**: User query is embedded and matched against movie database
- **Augmentation**: Top relevant movies are retrieved as context
- **Generation**: LLM (GPT-3.5-turbo) generates recommendations with explanations

### 5. Response Generation
- LLM receives user query + retrieved movie context
- Generates personalized recommendations with explanations
- Maintains conversation history for context

## Technical Details

### Technologies Used

- **Python 3.8+**: Core language
- **Pandas**: Data manipulation
- **SentenceTransformers**: Embedding generation
- **FAISS**: Vector similarity search
- **LangChain**: LLM orchestration and RAG pipeline
- **OpenAI API**: Language model (GPT-3.5-turbo)

### Model Information

- **Embedding Model**: `all-MiniLM-L6-v2` (384 dimensions)
  - Fast and efficient
  - Good semantic understanding
  - Runs locally (no API calls needed)

- **LLM**: OpenAI GPT-3.5-turbo
  - Generates natural, conversational responses
  - Understands context and user intent
  - Requires API key

## Dataset

The system uses a cleaned TMDB (The Movie Database) dataset with the following fields:
- **Title**: Movie title
- **Genres**: Comma-separated genres
- **Overview**: Movie description/plot
- **Vote Average**: Rating (0-10)
- **Popularity**: Popularity score
- **Release Date**: Movie release date

## Customization

### Change Embedding Model

Edit `src/vector_store.py`:

```python
self.embedding_model = SentenceTransformer("your-model-name")
```

Popular alternatives:
- `all-mpnet-base-v2` (768 dim, better quality, slower)
- `paraphrase-MiniLM-L6-v2` (384 dim, good for paraphrasing)

### Change LLM Model

Edit `src/rag_pipeline.py`:

```python
self.llm = ChatOpenAI(
    model_name="gpt-4",  # or "gpt-4-turbo"
    temperature=0.7
)
```

### Adjust Number of Recommendations

In `app.py`, modify:

```python
result = self.rag_pipeline.generate_recommendations(query, num_recommendations=5)
```

## Troubleshooting

### "OPENAI_API_KEY not found"
- Make sure you've set the environment variable correctly
- Restart your terminal after setting the variable
- Or create a `.env` file in the project root

### "Dataset not found"
- Ensure `tmdb_top_movies_cleaned.csv` is in the `data/` directory
- Check the file path in `app.py`

### Slow First Run
- First run builds the vector store (5-10 minutes)
- Subsequent runs are much faster (< 10 seconds)
- This is normal behavior

### Memory Issues
- If you have a large dataset, consider using `faiss-gpu` instead of `faiss-cpu`
- Reduce the number of retrieved movies in `rag_pipeline.py`

## Performance

- **Vector Store Build**: ~5-10 minutes (first run only)
- **Vector Store Load**: ~5-10 seconds
- **Query Processing**: ~2-5 seconds per query
- **Memory Usage**: ~500MB-1GB (depending on dataset size)

## Future Enhancements

Potential improvements:
- [x] Mood-based filtering (relaxed, inspiring, emotional) ✅
- [ ] User feedback system (like/dislike)
- [ ] Web UI interface
- [ ] Support for local LLMs (Ollama, LlamaCpp)
- [ ] Multi-turn conversation improvements
- [ ] Recommendation history

## License

This project is provided as-is for educational and demonstration purposes.

## Acknowledgments

- TMDB (The Movie Database) for the movie dataset
- SentenceTransformers for embedding models
- LangChain for RAG framework
- OpenAI for language models

## Support

For issues or questions:
1. Check the Troubleshooting section
2. Verify all dependencies are installed
3. Ensure your OpenAI API key is valid
4. Check that the dataset file exists and is readable

---

**Enjoy finding your next favorite movie! 🎬🍿**
