import os
import json
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any

SELECTED_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "selected")
METADATA_JSON = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "metadata", "commercial_judgments.json")

def download_single_pdf(case: Dict[str, Any]) -> str:
    path = case["path"]
    year = case["year"]
    dest_file = os.path.join(SELECTED_DIR, f"{path}_EN.pdf")
    
    if os.path.exists(dest_file) and os.path.getsize(dest_file) > 1000:
        return dest_file
        
    url = case.get("source_url") or f"https://indian-supreme-court-judgments.s3.amazonaws.com/data/pdf/year={year}/english/{path}_EN.pdf"
    
    try:
        res = requests.get(url, timeout=20)
        if res.status_code == 200 and len(res.content) > 1000:
            with open(dest_file, "wb") as f:
                f.write(res.content)
            return dest_file
        else:
            print(f"[Download] S3 PDF returned status {res.status_code} for {path}")
    except Exception as e:
        print(f"[Download] Error downloading PDF for {path}: {e}")
        
    return ""

def download_selected_judgments(max_workers: int = 10) -> List[str]:
    os.makedirs(SELECTED_DIR, exist_ok=True)
    
    if not os.path.exists(METADATA_JSON):
        raise FileNotFoundError(f"Metadata file {METADATA_JSON} not found. Run filter_judgments.py first.")
        
    with open(METADATA_JSON, "r", encoding="utf-8") as f:
        cases = json.load(f)
        
    print(f"[Download] Starting download of {len(cases)} selected commercial judgments into {SELECTED_DIR}...")
    
    downloaded_paths = []
    failed_count = 0
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(download_single_pdf, case): case for case in cases}
        for future in as_completed(futures):
            res_file = future.result()
            if res_file:
                downloaded_paths.append(res_file)
            else:
                failed_count += 1

    print(f"[Download] Complete. Successfully stored {len(downloaded_paths)} PDFs. Failed/skipped: {failed_count}.")
    return downloaded_paths

if __name__ == "__main__":
    download_selected_judgments()
