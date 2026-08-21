import os
import requests
import pandas as pd
from typing import List

METADATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "metadata")

def download_metadata_for_years(years: List[int]) -> List[str]:
    os.makedirs(METADATA_DIR, exist_ok=True)
    downloaded_files = []
    
    base_url = "https://indian-supreme-court-judgments.s3.amazonaws.com/metadata/parquet"
    
    for year in years:
        file_path = os.path.join(METADATA_DIR, f"metadata_{year}.parquet")
        if os.path.exists(file_path):
            print(f"[Metadata] Using cached metadata for year {year}: {file_path}")
            downloaded_files.append(file_path)
            continue
            
        url = f"{base_url}/year={year}/metadata.parquet"
        print(f"[Metadata] Downloading metadata for year {year} from {url}...")
        try:
            res = requests.get(url, timeout=30)
            if res.status_code == 200:
                with open(file_path, "wb") as f:
                    f.write(res.content)
                print(f"[Metadata] Saved {file_path} ({len(res.content)} bytes)")
                downloaded_files.append(file_path)
            else:
                print(f"[Metadata] Failed to fetch {url}, status code: {res.status_code}")
        except Exception as e:
            print(f"[Metadata] Error downloading year {year}: {e}")
            
    return downloaded_files

if __name__ == "__main__":
    # Test downloading metadata for recent years
    years_to_fetch = list(range(2010, 2026))
    download_metadata_for_years(years_to_fetch)
