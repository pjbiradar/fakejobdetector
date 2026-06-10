# 🔍 Fake Job Detector

An AI-powered multi-agent system that analyzes job postings and detects scams, ghost jobs, and misleading listings using GenAI techniques.

## 🎯 What it does

Paste any job posting and get back:
- **Verdict** — SCAM / GHOST JOB / MISLEADING / LEGITIMATE
- **Confidence score** — how certain the system is
- **Reasons** — exactly why it flagged the posting
- **Recommendation** — what the user should do

## 🏗️ Architecture
Job Posting Text
↓
Agent 1 — Language Analyzer    (HuggingFace Transformers + Sentiment)
Agent 2 — Company Verifier     (Groq Llama 3.3 70B + Prompt Engineering)
Agent 3 — Pattern Matcher      (Embeddings + ChromaDB + RAG)
Agent 4 — Verdict Generator    (Groq Llama 3.3 70B + Multi-agent reasoning)
↓
Guardrails (output validation)
↓
LLM Evaluator (verdict quality scoring)
↓
Streamlit UI
## 🧠 GenAI Concepts Used

| Concept | Where Used |
|---------|-----------|
| Transformers | Agent 1 — RoBERTa sentiment model |
| Transfer Learning | Agent 1 — Cardiff pretrained model |
| HuggingFace Pipelines | Agent 1 — text classification |
| Text Embeddings | Agent 3 — SentenceTransformer |
| Vector Database | Agent 3 — ChromaDB |
| RAG | Agent 3 — scam pattern retrieval |
| Prompt Engineering | Agents 2 and 4 — structured JSON output |
| LLM API | Agents 2 and 4 — Groq Llama 3.3 70B |
| Multi-agent System | CrewAI pipeline orchestration |
| Guardrails | Output validation layer |
| LLM Evaluation | Verdict quality scoring |

## 🛠️ Tech Stack

- **Python 3.9**
- **Streamlit** — frontend UI
- **FastAPI** — backend API
- **CrewAI** — multi-agent orchestration
- **Groq** — Llama 3.3 70B LLM API
- **HuggingFace Transformers** — sentiment analysis
- **Sentence Transformers** — text embeddings
- **ChromaDB** — vector database
- **Docker** — containerization

## 🚀 How to Run

### Local Setup

```bash
# Clone the repo
git clone https://github.com/YOURUSERNAME/fake-job-detector.git
cd fake-job-detector

# Create virtual environment
python3.9 -m venv venv
source venv/bin/activate

# Install packages
pip install -r requirements.txt

# Add your API keys
cp .env.example .env
# Edit .env and add your GROQ_API_KEY and HUGGINGFACE_TOKEN

# Run the app
streamlit run app.py
```

### Using Docker

```bash
docker-compose up
```

Open `http://localhost:8501` in your browser.

## 🔑 API Keys Required

- **Groq API** — free at console.groq.com
- **HuggingFace Token** — free at huggingface.co

## 📁 Project Structure
fake-job-detector/
├── agents/
│   ├── language_analyzer.py   # Agent 1 — HuggingFace sentiment
│   ├── pattern_matcher.py     # Agent 3 — ChromaDB RAG
│   ├── company_verifier.py    # Agent 2 — Groq LLM
│   └── verdict_generator.py   # Agent 4 — Groq LLM
├── data/
│   └── scam_patterns.json     # RAG knowledge base
├── app.py                     # Streamlit UI
├── crew.py                    # Multi-agent pipeline
├── guardrails.py              # Output validation
├── evaluator.py               # LLM evaluation
├── Dockerfile
└── docker-compose.yml
## 👩‍💻 Author

Pooja — GenAI Developer