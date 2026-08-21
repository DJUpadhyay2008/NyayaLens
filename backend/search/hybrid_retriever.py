import re
from typing import List, Dict, Any
from search.keyword_search import search_keywords
from search.vector_search import search_vectors

def hybrid_retrieve_and_rank(query: str, court_filter: str = None, year_filter: str = None, top_k: int = 15) -> Dict[str, Any]:
    # 1. Fetch Keyword results
    kw_results = search_keywords(query, court_filter=court_filter, year_filter=year_filter, limit=40)
    
    # 2. Fetch Vector results
    vec_results = search_vectors(query, court_filter=court_filter, year_filter=year_filter, limit=40)

    # Dictionary map by chunk_id
    combined: Dict[int, Dict[str, Any]] = {}
    
    # Compute RRF (Reciprocal Rank Fusion) parameters
    k_rrf = 60.0

    # Process Keyword Ranks
    for rank, item in enumerate(kw_results):
        cid = item["chunk_id"]
        if cid not in combined:
            combined[cid] = {**item, "kw_rank": rank + 1, "vec_rank": 999, "vector_score": 0.0, "keyword_score": item["keyword_score"]}
        else:
            combined[cid]["kw_rank"] = rank + 1
            combined[cid]["keyword_score"] = item["keyword_score"]

    # Process Vector Ranks
    for rank, item in enumerate(vec_results):
        cid = item["chunk_id"]
        if cid not in combined:
            combined[cid] = {**item, "kw_rank": 999, "vec_rank": rank + 1, "vector_score": item["vector_score"], "keyword_score": 0.0}
        else:
            combined[cid]["vec_rank"] = rank + 1
            combined[cid]["vector_score"] = item["vector_score"]

    if not combined:
        return {
            "results": [],
            "message": "Insufficient evidence found in the current legal corpus."
        }

    # Extract query tokens for highlight detection
    query_tokens = [t.lower() for t in re.findall(r'\b\w{3,}\b', query)]

    scored_items = []
    for cid, item in combined.items():
        # RRF Score calculation
        rrf_score = (1.0 / (k_rrf + item["kw_rank"])) + (1.0 / (k_rrf + item["vec_rank"]))
        
        # Raw vector similarity (0.0 to 1.0)
        v_score = max(0.0, item["vector_score"])
        
        # Title/Citation match bonus
        title_lower = (item.get("case_title") or "").lower()
        citation_lower = (item.get("citation") or "").lower()
        query_lower = query.lower()
        
        title_bonus = 0.20 if query_lower in title_lower or query_lower in citation_lower else 0.0
        
        # Final hybrid score normalized between 0.0 and 0.99
        hybrid_score = min(0.99, (rrf_score * 25.0) + (v_score * 0.45) + title_bonus)
        
        # Extract snippet/passage highlight terms
        passage_text = item.get("text", "")
        highlights = []
        for tok in query_tokens:
            if tok in passage_text.lower():
                highlights.append(tok)

        item["hybrid_score"] = round(hybrid_score, 4)
        item["highlights"] = list(set(highlights))
        scored_items.append(item)

    # Sort descending by hybrid_score
    scored_items.sort(key=lambda x: x["hybrid_score"], reverse=True)

    # Deduplicate by case_id (return top passage per case, or top overall chunks)
    final_results = []
    seen_cases = set()

    for item in scored_items:
        case_id = item["case_id"]
        # Allow up to 2 distinct passages per case
        count = sum(1 for res in final_results if res["case_id"] == case_id)
        if count < 2:
            final_results.append(item)
            if len(final_results) >= top_k:
                break

    if not final_results or (final_results and final_results[0]["hybrid_score"] < 0.12):
        return {
            "results": [],
            "message": "Insufficient evidence found in the current legal corpus."
        }

    return {
        "results": final_results,
        "message": None
    }
