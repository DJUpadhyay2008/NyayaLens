import os
import psycopg2
from typing import List, Dict, Any
from ingestion.generate_embeddings import generate_embedding

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASSWORD", "postgrespassword")
DB_NAME = os.getenv("DB_NAME", "ai_legal_research")

def search_vectors(query: str, court_filter: str = None, year_filter: str = None, limit: int = 30) -> List[Dict[str, Any]]:
    query_vector = generate_embedding(query)
    
    conn = psycopg2.connect(host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASS, dbname=DB_NAME)
    results = []

    sql = """
    SELECT 
        c.id as chunk_id,
        c.case_id,
        c.document_id,
        c.chunk_index,
        c.page_number,
        c.paragraph_reference,
        c.text,
        cs.title as case_title,
        cs.citation,
        cs.court,
        cs.decision_date,
        cs.year,
        cs.judges,
        cs.parties,
        cs.source_url,
        cs.metadata as case_meta,
        cosine_similarity(c.embedding, %s::float8[]) as similarity_score
    FROM document_chunks c
    JOIN cases cs ON c.case_id = cs.id
    WHERE c.embedding IS NOT NULL
    """

    params = [query_vector]

    if court_filter and court_filter.strip() and court_filter != "All":
        sql += " AND cs.court ILIKE %s"
        params.append(f"%{court_filter.strip()}%")

    if year_filter and year_filter.strip() and year_filter != "All":
        try:
            sql += " AND cs.year = %s"
            params.append(int(year_filter.strip()))
        except ValueError:
            pass

    sql += " ORDER BY similarity_score DESC LIMIT %s;"
    params.append(limit)

    with conn.cursor() as cur:
        cur.execute(sql, params)
        rows = cur.fetchall()
        for r in rows:
            dec_date = str(r[10]) if r[10] else ""
            results.append({
                "chunk_id": r[0],
                "case_id": r[1],
                "document_id": r[2],
                "chunk_index": r[3],
                "page_number": r[4],
                "paragraph_reference": r[5],
                "text": r[6],
                "case_title": r[7],
                "citation": r[8],
                "court": r[9],
                "decision_date": dec_date,
                "year": r[11],
                "judges": r[12],
                "parties": r[13],
                "source_url": r[14],
                "case_meta": r[15] or {},
                "vector_score": float(r[16]) if r[16] is not None else 0.0
            })

    conn.close()
    return results
