import os
import sys
import psycopg2
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

# Add parent directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.search import SearchRequest, SearchResponse, CaseDetailResponse
from services.search_service import execute_legal_search
from services.case_service import get_case_by_id

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASSWORD", "postgrespassword")
DB_NAME = os.getenv("DB_NAME", "ai_legal_research")

app = FastAPI(
    title="NyayaLens API - AI Legal Research Engine",
    description="Natural-language legal query search engine over indexed Indian Supreme Court commercial judgments.",
    version="1.0.0"
)

# Enable CORS for React/Vite frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
def health_check():
    try:
        conn = psycopg2.connect(host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASS, dbname=DB_NAME)
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM cases;")
            ncases = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM document_chunks;")
            nchunks = cur.fetchone()[0]
        conn.close()
        return {
            "status": "healthy",
            "database": "connected",
            "indexed_cases": ncases,
            "indexed_chunks": nchunks
        }
    except Exception as e:
        return {
            "status": "degraded",
            "database_error": str(e)
        }

@app.post("/api/search", response_model=SearchResponse)
def search_legal_corpus(request: SearchRequest):
    try:
        res = execute_legal_search(
            query=request.query,
            court=request.court,
            year=request.year,
            document_type=request.document_type,
            top_k=request.top_k
        )
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search execution error: {str(e)}")

@app.get("/api/cases/{case_id}", response_model=CaseDetailResponse)
def get_case_details(case_id: int):
    case_data = get_case_by_id(case_id)
    if not case_data:
        raise HTTPException(status_code=404, detail=f"Case with ID {case_id} not found.")
    return case_data

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
