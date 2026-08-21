from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class SearchRequest(BaseModel):
    query: str = Field(..., description="Natural language legal query or case citation")
    court: Optional[str] = Field(default=None, description="Court filter (e.g. Supreme Court of India)")
    year: Optional[str] = Field(default=None, description="Year filter")
    document_type: Optional[str] = Field(default=None, description="Document type filter")
    top_k: int = Field(default=15, description="Number of results to return")

class SearchResultItem(BaseModel):
    case_id: int
    case_name: str
    citation: str
    court: str
    date: str
    year: int
    score: float
    passage: str
    page: Optional[int] = None
    paragraph: Optional[str] = None
    source: str = "AWS Supreme Court Judgments"
    source_url: Optional[str] = None
    judges: Optional[str] = None
    parties: Optional[str] = None
    disposal_nature: Optional[str] = None
    highlights: List[str] = []

class SearchResponse(BaseModel):
    query: str
    expanded_terms: List[str] = []
    total_results: int
    results: List[SearchResultItem]
    message: Optional[str] = None

class ChunkDetail(BaseModel):
    chunk_index: int
    page_number: int
    paragraph_reference: str
    text: str

class CaseDetailResponse(BaseModel):
    id: int
    path: str
    title: str
    citation: str
    court: str
    decision_date: Optional[str] = None
    year: int
    judges: Optional[str] = None
    parties: Optional[str] = None
    source_url: Optional[str] = None
    raw_text: str
    chunks: List[ChunkDetail]
    metadata: Dict[str, Any] = {}
