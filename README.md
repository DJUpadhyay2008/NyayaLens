# NyayaLens ⚖️ — AI Legal Research Engine

> **Precision Hybrid Semantic & Full-Text Retrieval for Indian Commercial Courts**

**NyayaLens** is an AI-powered legal research platform tailored for judicial officers, researchers, and legal practitioners operating in Indian Commercial Courts. It provides fast, citation-backed, zero-hallucination legal passage retrieval over an indexed corpus of official **Supreme Court of India commercial judgments**.

---

## 🌟 Key Features

- **Hybrid Semantic + Keyword Retrieval:** Combines dense vector embedding similarity (`sentence-transformers/all-MiniLM-L6-v2`) with PostgreSQL Full-Text Keyword search (`tsvector` + GIN indexing) via **Reciprocal Rank Fusion (RRF)**.
- **Precision Paragraph & Page Tagging:** Every result features exact Supreme Court Reporter (S.C.R.) citations, paragraph reference markers (e.g. `Paragraph 22`), and page numbers (`Page 26`).
- **Zero-Hallucination Guarantee:** Only returns verified, verbatim extracts directly from indexed judgment texts. Displays an *Insufficient Evidence* warning when legal corpus coverage is absent.
- **Interactive Case Viewer:** Complete document text reader with passage filtering, bench details, decision dates, and direct links to AWS Open Data source PDFs.
- **Judicial Theme & UX:** Tailored dark slate aesthetic with relevance percentage badges, key search term highlights, and instant suggested queries for commercial legal disputes.

---

## 📐 Architecture & Tech Stack

```
Natural Language Query -> NyayaLens Frontend (React + Vite + Tailwind)
                                |
                        FastAPI Backend (/api/search)
                                |
             Hybrid Retrieval (SentenceTransformers + PostgreSQL tsvector)
                                |
                  PostgreSQL + pgvector Database (750 Judgments / 24.6k Chunks)
```

- **Frontend:** React 19, Vite, Tailwind CSS, Lucide Icons, Axios.
- **Backend:** FastAPI, Python 3.10+, PyPDF, Sentence-Transformers, NumPy, Psycopg2.
- **Database:** PostgreSQL 16 with Full-Text Search TSVector & Cosine Similarity (`cosine_similarity`).
- **Corpus Source:** [AWS Open Data Indian Supreme Court Judgments](https://registry.opendata.aws/indian-supreme-court-judgments/).

---

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.10+
- Node.js 18+ & npm
- PostgreSQL 14+ running locally on port `5432` with user `postgres` and password `postgrespassword`

### 1. Database Setup
Create the database in PostgreSQL:
```sql
CREATE DATABASE ai_legal_research;
```

### 2. Backend Setup & Ingestion
```bash
# Navigate to project root
cd NyayaLens

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install backend dependencies
pip install -r backend/requirements.txt

# Run ingestion pipeline (downloads metadata, filters commercial cases, extracts text & stores embeddings)
python backend/ingestion/ingest.py
```

### 3. Start Backend Server
```bash
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
```
Backend API docs available at: `http://localhost:8000/docs`

### 4. Frontend Setup & Startup
```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start Vite dev server
npm run dev
```
Open `http://localhost:5173/` in your browser.

---

## 📜 License

Derived from official public domain records of the Supreme Court of India via the AWS Open Data project.

Developed for Indian Commercial Courts Research & Judicial Verification.
