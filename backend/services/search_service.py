import os
import re
from typing import Dict, Any
from search.hybrid_retriever import hybrid_retrieve_and_rank

def execute_legal_search(query: str, court: str = None, year: str = None, document_type: str = None, top_k: int = 15) -> Dict[str, Any]:
    query_str = query.strip()
    if not query_str:
        return {
            "query": query,
            "total_results": 0,
            "results": [],
            "message": "Query string cannot be empty."
        }

    # Extract expanded search terms for legal clarity
    expanded_terms = [t for t in re.findall(r'\b\w{4,}\b', query_str) if t.lower() not in {'cases', 'with', 'from', 'that', 'this', 'where', 'have', 'been', 'which'}]

    # Run hybrid retrieval
    retrieved = hybrid_retrieve_and_rank(query_str, court_filter=court, year_filter=year, top_k=top_k)

    results_list = []
    for item in retrieved["results"]:
        results_list.append({
            "case_id": item["case_id"],
            "case_name": item.get("case_title") or "Commercial Law Judgment",
            "citation": item.get("citation") or f"[{item.get('year')}] SC",
            "court": item.get("court") or "Supreme Court of India",
            "date": item.get("decision_date") or str(item.get("year")),
            "year": item.get("year"),
            "score": item["hybrid_score"],
            "passage": item["text"],
            "page": item.get("page_number") or 1,
            "paragraph": item.get("paragraph_reference") or "Page 1",
            "source": "AWS Supreme Court Judgments",
            "source_url": item.get("source_url") or "",
            "judges": item.get("judges") or "",
            "parties": item.get("parties") or "",
            "disposal_nature": item.get("case_meta", {}).get("disposal_nature") or "",
            "highlights": item.get("highlights", [])
        })

    return {
        "query": query,
        "expanded_terms": expanded_terms[:6],
        "total_results": len(results_list),
        "results": results_list,
        "message": retrieved.get("message")
    }
