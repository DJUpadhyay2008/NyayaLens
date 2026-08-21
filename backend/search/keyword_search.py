import os
import re
import psycopg2
from typing import List, Dict, Any

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASSWORD", "postgrespassword")
DB_NAME = os.getenv("DB_NAME", "ai_legal_research")

def search_keywords(query: str, court_filter: str = None, year_filter: str = None, limit: int = 30) -> List[Dict[str, Any]]:
    cleaned_query = re.sub(r'[^\w\s]', ' ', query)
    words = [w for w in cleaned_query.split() if len(w) > 2]
    
    if not words:
        return []
        
    ilike_pattern = f"%{query.strip()}%"
    
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
        ts_rank_cd(c.tsv, plainto_tsquery('english', %s)) as rank_score,
        CASE WHEN c.text ILIKE %s THEN 0.5 ELSE 0.0 END as exact_bonus
    FROM document_chunks c
    JOIN cases cs ON c.case_id = cs.id
    WHERE (c.tsv @@ plainto_tsquery('english', %s) OR c.text ILIKE %s OR cs.title ILIKE %s OR cs.citation ILIKE %s)
    """

    params = [query, ilike_pattern, query, ilike_pattern, ilike_pattern, ilike_pattern]

    if court_filter and court_filter.strip() and court_filter != "All":
        sql += " AND cs.court ILIKE %s"
        params.append(f"%{court_filter.strip()}%")

    if year_filter and year_filter.strip() and year_filter != "All":
        try:
            sql += " AND cs.year = %s"
            params.append(int(year_filter.strip()))
        except ValueError:
            pass

    sql += " ORDER BY (ts_rank_cd(c.tsv, plainto_tsquery('english', %s)) + CASE WHEN c.text ILIKE %s THEN 0.5 ELSE 0.0 END) DESC LIMIT %s;"
    params.extend([query, ilike_pattern, limit])

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
                "keyword_score": float(r[16]) + float(r[17])
            })

    conn.close()
    return results
