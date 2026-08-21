import os
import psycopg2
from typing import Dict, Any, Optional

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASSWORD", "postgrespassword")
DB_NAME = os.getenv("DB_NAME", "ai_legal_research")

def get_case_by_id(case_id: int) -> Optional[Dict[str, Any]]:
    conn = psycopg2.connect(host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASS, dbname=DB_NAME)
    
    with conn.cursor() as cur:
        # Fetch case
        cur.execute("""
        SELECT id, path, title, citation, court, decision_date, year, judges, parties, source_url, metadata
        FROM cases
        WHERE id = %s;
        """, (case_id,))
        c = cur.fetchone()
        if not c:
            conn.close()
            return None

        case_data = {
            "id": c[0],
            "path": c[1],
            "title": c[2],
            "citation": c[3] or "",
            "court": c[4] or "Supreme Court of India",
            "decision_date": str(c[5]) if c[5] else "",
            "year": c[6],
            "judges": c[7] or "",
            "parties": c[8] or "",
            "source_url": c[9] or "",
            "metadata": c[10] or {}
        }

        # Fetch document raw text
        cur.execute("""
        SELECT id, filename, raw_text, page_count
        FROM documents
        WHERE case_id = %s
        LIMIT 1;
        """, (case_id,))
        doc = cur.fetchone()
        raw_text = doc[2] if doc else ""

        # Fetch document chunks
        cur.execute("""
        SELECT chunk_index, page_number, paragraph_reference, text
        FROM document_chunks
        WHERE case_id = %s
        ORDER BY chunk_index ASC;
        """, (case_id,))
        chunk_rows = cur.fetchall()

        chunks = []
        for r in chunk_rows:
            chunks.append({
                "chunk_index": r[0],
                "page_number": r[1],
                "paragraph_reference": r[2],
                "text": r[3]
            })

        case_data["raw_text"] = raw_text
        case_data["chunks"] = chunks

    conn.close()
    return case_data
