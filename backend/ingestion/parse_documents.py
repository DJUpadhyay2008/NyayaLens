import os
import re
import pypdf
from typing import Dict, Any, List

def parse_pdf_file(pdf_path: str, case_meta: Dict[str, Any] = None) -> Dict[str, Any]:
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"File not found: {pdf_path}")
        
    pages_data = []
    full_text_parts = []
    
    try:
        reader = pypdf.PdfReader(pdf_path)
        page_count = len(reader.pages)
        
        for i, page in enumerate(reader.pages):
            page_num = i + 1
            raw_page_text = page.extract_text() or ""
            # Clean common artifacts or header noise if needed
            cleaned_page_text = raw_page_text.strip()
            
            # Find paragraph references on this page if present (e.g., "12.", "Para 15", "Paragraph 8")
            para_matches = re.findall(r'(?:Paragraph|Para|\b)\s*(\d{1,3})\.\s+[A-Z]', cleaned_page_text)
            para_refs = [f"Paragraph {p}" for p in para_matches] if para_matches else []
            
            pages_data.append({
                "page_number": page_num,
                "text": cleaned_page_text,
                "paragraph_references": para_refs
            })
            full_text_parts.append(cleaned_page_text)
            
        full_text = "\n\n".join(full_text_parts)
        
        doc_id = os.path.splitext(os.path.basename(pdf_path))[0]
        
        return {
            "document_id": doc_id,
            "filename": os.path.basename(pdf_path),
            "filepath": pdf_path,
            "page_count": page_count,
            "raw_text": full_text,
            "pages": pages_data,
            "metadata": case_meta or {}
        }
    except Exception as e:
        print(f"[Parser] Error parsing {pdf_path}: {e}")
        return {
            "document_id": os.path.basename(pdf_path),
            "filename": os.path.basename(pdf_path),
            "filepath": pdf_path,
            "page_count": 0,
            "raw_text": "",
            "pages": [],
            "metadata": case_meta or {}
        }
