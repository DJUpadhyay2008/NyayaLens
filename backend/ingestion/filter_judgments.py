import os
import json
import pandas as pd
from typing import List, Dict, Any

METADATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "metadata")
OUTPUT_JSON = os.path.join(METADATA_DIR, "commercial_judgments.json")

# Core commercial keywords and legal domain topics
COMMERCIAL_KEYWORDS = [
    "contract", "breach", "commercial", "arbitration", "arbitral", "award",
    "sale of goods", "company", "companies", "insolvency", "ibc", "nclt", "nclat",
    "bank", "banking", "negotiable instrument", "cheque", "financial",
    "partnership", "agency", "damages", "liquidated damages", "specific performance",
    "specific relief", "trademark", "patent", "copyright", "guarantee", "indemnity",
    "mortgage", "promissory", "debt", "creditor", "debtor", "commercial dispute",
    "commercial transaction", "letter of credit", "pledge", "surety"
]

def filter_commercial_judgments(years: List[int], target_count: int = 750) -> List[Dict[str, Any]]:
    filtered_cases = []
    seen_ids = set()

    for year in years:
        file_path = os.path.join(METADATA_DIR, f"metadata_{year}.parquet")
        if not os.path.exists(file_path):
            print(f"[Filter] File not found: {file_path}")
            continue

        try:
            df = pd.read_parquet(file_path)
            pattern = "|".join(COMMERCIAL_KEYWORDS)
            
            # Combine title, description, and raw_html check for keywords
            mask = df["title"].str.contains(pattern, case=False, na=False)
            if "description" in df.columns:
                mask = mask | df["description"].str.contains(pattern, case=False, na=False)
                
            matched_df = df[mask]
            
            for _, row in matched_df.iterrows():
                path = str(row.get("path") or "")
                if not path or path in seen_ids:
                    continue
                seen_ids.add(path)
                
                title = str(row.get("title") or "").strip()
                citation = str(row.get("citation") or "").strip()
                case_id = str(row.get("case_id") or row.get("nc_display") or path).strip()
                decision_date = str(row.get("decision_date") or "").strip()
                judge = str(row.get("judge") or row.get("author_judge") or "").strip()
                court = str(row.get("court") or "Supreme Court of India").strip()
                cnr = str(row.get("cnr") or "").strip()
                disposal = str(row.get("disposal_nature") or "").strip()
                petitioner = str(row.get("petitioner") or "").strip()
                respondent = str(row.get("respondent") or "").strip()

                case_item = {
                    "path": path,
                    "year": int(row.get("year") or year),
                    "title": title,
                    "citation": citation if citation else f"[{row.get('year') or year}] SC (Commercial)",
                    "case_id": case_id,
                    "cnr": cnr,
                    "decision_date": decision_date,
                    "judge": judge,
                    "court": court,
                    "disposal_nature": disposal,
                    "petitioner": petitioner,
                    "respondent": respondent,
                    "source_url": f"https://indian-supreme-court-judgments.s3.amazonaws.com/data/pdf/year={row.get('year') or year}/english/{path}_EN.pdf",
                    "json_url": f"https://indian-supreme-court-judgments.s3.amazonaws.com/metadata/json/year={row.get('year') or year}/{path}.json"
                }
                filtered_cases.append(case_item)

        except Exception as e:
            print(f"[Filter] Error reading {file_path}: {e}")

    print(f"[Filter] Found {len(filtered_cases)} total matching commercial judgments.")
    
    # Cap to target count if necessary
    selected = filtered_cases[:target_count]
    os.makedirs(os.path.dirname(OUTPUT_JSON), exist_ok=True)
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(selected, f, indent=2, ensure_ascii=False)
        
    print(f"[Filter] Saved {len(selected)} commercial judgment metadata entries to {OUTPUT_JSON}")
    return selected

if __name__ == "__main__":
    years = list(range(2010, 2026))
    filter_commercial_judgments(years, target_count=750)
