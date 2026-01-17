# Quick Start Guide

## 🚀 Run in 3 Steps

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Groq API Key

**Windows PowerShell:**
```powershell
$env:GROQ_API_KEY="your-api-key-here"
```

**Windows CMD:**
```cmd
set GROQ_API_KEY=your-api-key-here
```

**Linux/Mac:**
```bash
export GROQ_API_KEY=your-api-key-here
```

**Or create a `.env` file in the project root:**
```
GROQ_API_KEY=your-api-key-here
```

### 3. Run the App
```bash
python app.py
```

---

## 📝 First Run

- First run takes **5-10 minutes** (builds vector store)
- Subsequent runs are **fast** (< 10 seconds)

## 💬 Example Queries

- "Suggest me a light movie for tonight, I'm tired"
- "Recommend a feel-good movie"
- "I want a comedy to relax"

## ⚙️ Troubleshooting

**Missing API Key?**
- Get one from: https://console.groq.com/keys
- Set it as shown in Step 2

**Dependencies not installed?**
- Run: `pip install -r requirements.txt`

**Verify setup:**
- Run: `python verify_setup.py`
