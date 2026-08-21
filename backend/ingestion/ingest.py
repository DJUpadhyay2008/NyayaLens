import os
import sys
import json
import time
import psycopg2
from psycopg2.extras import execute_values, Json

# Add parent directories to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ingestion.download_metadata import download_metadata_for_years
from ingestion.filter_judgments import filter_commercial_judgments
from ingestion.download_selected import download_selected_judgments
from ingestion.parse_documents import parse_pdf_file
from ingestion.chunk_documents import chunk_parsed_document
from ingestion.generate_embeddings import generate_embeddings_batch

# DB Connection Config
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASSWORD", "postgrespassword")
DB_NAME = os.getenv("DB_NAME", "ai_legal_research")

def get_db_connection():
    # Ensure database exists
    conn_root = psycopg2.connect(host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASS, dbname="postgres")
    conn_root.autocommit = True
    with conn_root.cursor() as cur:
        cur.execute(f"SELECT 1 FROM pg_database WHERE datname='{DB_NAME}'")
        if not cur.fetchone():
            cur.execute(f"CREATE DATABASE {DB_NAME};")
            print(f"[Database] Created database {DB_NAME}")
    conn_root.close()

    conn = psycopg2.connect(host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASS, dbname=DB_NAME)
    return conn

def init_db_schema(conn):
    with conn.cursor() as cur:
        # Create cases table
        cur.execute("""
        CREATE TABLE IF NOT EXISTS cases (
            id SERIAL PRIMARY KEY,
            path VARCHAR(255) UNIQUE NOT NULL,
            title TEXT NOT NULL,
            citation TEXT,
            court TEXT,
            decision_date DATE,
            year INT,
            judges TEXT,
            parties TEXT,
            source TEXT DEFAULT 'AWS Supreme Court Judgments',
            source_url TEXT,
            metadata JSONB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # Create documents table
        cur.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id SERIAL PRIMARY KEY,
            case_id INT REFERENCES cases(id) ON DELETE CASCADE,
            filename VARCHAR(255) NOT NULL,
            raw_text TEXT,
            page_count INT,
            source_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # Create document_chunks table
        cur.execute("""
        CREATE TABLE IF NOT EXISTS document_chunks (
            id SERIAL PRIMARY KEY,
            document_id INT REFERENCES documents(id) ON DELETE CASCADE,
            case_id INT REFERENCES cases(id) ON DELETE CASCADE,
            chunk_index INT NOT NULL,
            page_number INT,
            paragraph_reference TEXT,
            text TEXT NOT NULL,
            embedding float8[],
            metadata JSONB,
            tsv tsvector,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # Cosine similarity SQL function
        cur.execute("""
        CREATE OR REPLACE FUNCTION cosine_similarity(a float8[], b float8[])
        RETURNS float8 AS $$
        DECLARE
            dot float8 := 0;
            norm_a float8 := 0;
            norm_b float8 := 0;
            i int;
        BEGIN
            FOR i IN 1..array_length(a, 1) LOOP
                dot := dot + a[i] * b[i];
                norm_a := norm_a + a[i] * a[i];
                norm_b := norm_b + b[i] * b[i];
            END LOOP;
            IF norm_a = 0 OR norm_b = 0 THEN
                RETURN 0;
            END IF;
            RETURN dot / (sqrt(norm_a) * sqrt(norm_b));
        END;
        $$ LANGUAGE plpgsql IMMUTABLE STRICT;
        """)

        # Indexes for fast search
        cur.execute("CREATE INDEX IF NOT EXISTS idx_cases_year ON cases(year);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_cases_court ON cases(court);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_chunks_case_id ON document_chunks(case_id);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_chunks_document_id ON document_chunks(document_id);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_chunks_tsv ON document_chunks USING GIN(tsv);")

        conn.commit()
        print("[Database] Schema initialized successfully with PostgreSQL full-text index and vector similarity.")

def run_ingestion_pipeline(start_year: int = 2010, end_year: int = 2025, max_cases: int = 750):
    start_time = time.time()
    years = list(range(start_year, end_year + 1))
    
    print("==================================================")
    print("STEP 1: Downloading AWS S3 metadata...")
    print("==================================================")
    download_metadata_for_years(years)
    
    print("==================================================")
    print("STEP 2: Filtering commercial law judgments...")
    print("==================================================")
    filtered_cases = filter_commercial_judgments(years, target_count=max_cases)
    
    print("==================================================")
    print("STEP 3: Downloading selected judgment PDF files...")
    print("==================================================")
    download_selected_judgments(max_workers=12)
    
    print("==================================================")
    print("STEP 4: Database connection & schema setup...")
    print("==================================================")
    conn = get_db_connection()
    init_db_schema(conn)
    
    selected_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "selected")
    
    ingested_cases = 0
    ingested_docs = 0
    ingested_chunks = 0
    
    print("==================================================")
    print(f"STEP 5: Extracting, Chunking, Embedding & Ingesting {len(filtered_cases)} cases...")
    print("==================================================")
    
    for idx, case in enumerate(filtered_cases):
        path = case["path"]
        pdf_filename = f"{path}_EN.pdf"
        pdf_filepath = os.path.join(selected_dir, pdf_filename)
        
        if not os.path.exists(pdf_filepath):
            continue

        try:
            # Format decision date safely
            dec_date = case.get("decision_date") or None
            if dec_date and len(dec_date.split("-")) == 3:
                parts = dec_date.split("-")
                # Handle DD-MM-YYYY format
                if len(parts[0]) == 2 and len(parts[2]) == 4:
                    dec_date = f"{parts[2]}-{parts[1]}-{parts[0]}"

            with conn.cursor() as cur:
                cur.execute("""
                INSERT INTO cases (path, title, citation, court, decision_date, year, judges, parties, source_url, metadata)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (path) DO UPDATE SET
                    title = EXCLUDED.title,
                    citation = EXCLUDED.citation
                RETURNING id;
                """, (
                    path,
                    case.get("title"),
                    case.get("citation"),
                    case.get("court"),
                    dec_date if dec_date and len(dec_date) == 10 else None,
                    case.get("year"),
                    case.get("judge"),
                    f"{case.get('petitioner', '')} v. {case.get('respondent', '')}".strip(" v. "),
                    case.get("source_url"),
                    Json(case)
                ))
                case_id = cur.fetchone()[0]
                ingested_cases += 1

                # Parse PDF document
                parsed = parse_pdf_file(pdf_filepath, case_meta=case)
                
                # Save Document entry
                cur.execute("""
                INSERT INTO documents (case_id, filename, raw_text, page_count, source_path)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id;
                """, (
                    case_id,
                    parsed["filename"],
                    parsed["raw_text"],
                    parsed["page_count"],
                    parsed["filepath"]
                ))
                doc_id = cur.fetchone()[0]
                ingested_docs += 1

                # Chunk document
                chunks = chunk_parsed_document(parsed, chunk_size_words=350, overlap_words=50)
                if not chunks:
                    conn.commit()
                    continue

                chunk_texts = [c["text"] for c in chunks]
                embeddings = generate_embeddings_batch(chunk_texts, batch_size=32)

                chunk_rows = []
                for c, emb in zip(chunks, embeddings):
                    chunk_rows.append((
                        doc_id,
                        case_id,
                        c["chunk_index"],
                        c["page_number"],
                        c["paragraph_reference"],
                        c["text"],
                        emb,
                        Json(c["metadata"]),
                        c["text"] # 9th item for to_tsvector('english', %s)
                    ))

                execute_values(cur, """
                INSERT INTO document_chunks (document_id, case_id, chunk_index, page_number, paragraph_reference, text, embedding, metadata, tsv)
                VALUES %s
                """, chunk_rows, template="(%s, %s, %s, %s, %s, %s, %s, %s, to_tsvector('english', %s))")

                ingested_chunks += len(chunk_rows)
                conn.commit()

            if (idx + 1) % 10 == 0 or (idx + 1) == len(filtered_cases):
                print(f"[Ingestion Progress] Ingested {idx + 1}/{len(filtered_cases)} cases ({ingested_chunks} chunks stored)...")

        except Exception as e:
            conn.rollback()
            print(f"[Ingestion Error] Case {path}: {e}")

    conn.close()
    elapsed = time.time() - start_time
    print("==================================================")
    print(f"INGESTION COMPLETE IN {elapsed:.2f} SECONDS!")
    print(f"Cases Ingested: {ingested_cases}")
    print(f"Documents Ingested: {ingested_docs}")
    print(f"Document Chunks Ingested: {ingested_chunks}")
    print("==================================================")

if __name__ == "__main__":
    run_ingestion_pipeline()
