# Check if its downloaded them all, or a year is missing or something
# If not:
# GET "https://nvd.nist.gov/feeds/json/cve/2.0/nvdcve-2.0-2002.json.zip"
# GET "https://nvd.nist.gov/feeds/json/cve/2.0/nvdcve-2.0-2003.json.zip"
# ...
# GET "https://nvd.nist.gov/feeds/json/cve/2.0/nvdcve-2.0-2025.json.zip"
# (This is all in /config/sources.yaml)

# 2h Loop:
# GET "https://nvd.nist.gov/feeds/json/cve/2.0/nvdcve-2.0-recent.json.zip"
# Unzip, send to ES, delete

# Check /scraping/run_history.json for NVD "modified" and "recent"
# if the date is under 8 days, then scrape new info and move on
# if its longer than 8 days since scrape, re-scrape everything

import requests, os, zipfile
from urllib.parse import urlparse
from utils.temp_manager import TempManager

TmpMgr = TempManager()

def _download_archive(URL):
    """Downloads a file from a URL to a temp dir, returns file path to downloaded file"""

    parsed_url = urlparse(URL)
    filename = os.path.basename(parsed_url.path)
    
    zip_path = TmpMgr.create_file_bytes(filename, requests.get(URL).content)
    
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(TmpMgr.path)
    
    os.remove(zip_path)

    return os.path.join(TmpMgr.path, filename)