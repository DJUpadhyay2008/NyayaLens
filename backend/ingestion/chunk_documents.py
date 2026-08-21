import re
from typing import List, Dict, Any

def chunk_parsed_document(parsed_doc: Dict[str, Any], chunk_size_words: int = 350, overlap_words: int = 50) -> List[Dict[str, Any]]:
    chunks = []
    chunk_index = 0
    pages = parsed_doc.get("pages", [])
    case_meta = parsed_doc.get("metadata", {})
    
    if not pages:
        return chunks
        
    for page in pages:
        page_num = page["page_number"]
        page_text = page["text"]
        
        if not page_text.strip():
            continue

        # Split page into paragraph blocks
        paragraphs = [p.strip() for p in re.split(r'\n\s*\n|\n(?=\d{1,3}\.\s+[A-Z])', page_text) if p.strip()]
        
        current_chunk_words = []
        current_para_ref = f"Page {page_num}"
        
        for para in paragraphs:
            # Check paragraph header numbers (e.g. "15. The court observed...")
            para_num_match = re.match(r'^(\d{1,3})\.\s+', para)
            if para_num_match:
                current_para_ref = f"Paragraph {para_num_match.group(1)}"

            para_words = para.split()
            if len(current_chunk_words) + len(para_words) <= chunk_size_words:
                current_chunk_words.extend(para_words)
            else:
                if current_chunk_words:
                    chunk_text = " ".join(current_chunk_words)
                    chunks.append({
                        "chunk_index": chunk_index,
                        "page_number": page_num,
                        "paragraph_reference": current_para_ref,
                        "text": chunk_text,
                        "metadata": {
                            "document_id": parsed_doc.get("document_id"),
                            "filename": parsed_doc.get("filename"),
                            "title": case_meta.get("title"),
                            "citation": case_meta.get("citation"),
                            "court": case_meta.get("court"),
                            "year": case_meta.get("year"),
                            "judge": case_meta.get("judge"),
                            "decision_date": case_meta.get("decision_date"),
                            "disposal_nature": case_meta.get("disposal_nature")
                        }
                    })
                    chunk_index += 1
                
                # Keep overlap for smooth context continuity
                if len(current_chunk_words) > overlap_words:
                    current_chunk_words = current_chunk_words[-overlap_words:] + para_words
                else:
                    current_chunk_words = para_words
                    
        if current_chunk_words:
            chunk_text = " ".join(current_chunk_words)
            chunks.append({
                "chunk_index": chunk_index,
                "page_number": page_num,
                "paragraph_reference": current_para_ref,
                "text": chunk_text,
                "metadata": {
                    "document_id": parsed_doc.get("document_id"),
                    "filename": parsed_doc.get("filename"),
                    "title": case_meta.get("title"),
                    "citation": case_meta.get("citation"),
                    "court": case_meta.get("court"),
                    "year": case_meta.get("year"),
                    "judge": case_meta.get("judge"),
                    "decision_date": case_meta.get("decision_date"),
                    "disposal_nature": case_meta.get("disposal_nature")
                }
            })
            chunk_index += 1

    return chunks
