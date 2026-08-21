import os
from typing import List
import numpy as np

EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2")

_model = None

def get_embedding_model():
    global _model
    if _model is None:
        print(f"[Embeddings] Initializing embedding model '{EMBEDDING_MODEL_NAME}'...")
        try:
            from sentence_transformers import SentenceTransformer
            _model = SentenceTransformer(EMBEDDING_MODEL_NAME)
            print(f"[Embeddings] Model '{EMBEDDING_MODEL_NAME}' loaded successfully.")
        except Exception as e:
            print(f"[Embeddings] Warning loading '{EMBEDDING_MODEL_NAME}': {e}. Falling back to default.")
            from sentence_transformers import SentenceTransformer
            _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model

def generate_embedding(text: str) -> List[float]:
    model = get_embedding_model()
    # Normalize text
    clean_text = text.replace("\n", " ").strip()
    embedding = model.encode(clean_text, convert_to_numpy=True)
    # L2 normalize vector for cosine similarity
    norm = np.linalg.norm(embedding)
    if norm > 0:
        embedding = embedding / norm
    return embedding.tolist()

def generate_embeddings_batch(texts: List[str], batch_size: int = 32) -> List[List[float]]:
    model = get_embedding_model()
    clean_texts = [t.replace("\n", " ").strip() for t in texts]
    embeddings = model.encode(clean_texts, batch_size=batch_size, convert_to_numpy=True, show_progress_bar=False)
    
    normalized_embeddings = []
    for emb in embeddings:
        norm = np.linalg.norm(emb)
        if norm > 0:
            emb = emb / norm
        normalized_embeddings.append(emb.tolist())
        
    return normalized_embeddings

if __name__ == "__main__":
    res = generate_embedding("Delayed payment in commercial contract as material breach")
    print(f"Sample embedding generated. Vector length: {len(res)}, sample values: {res[:5]}")
