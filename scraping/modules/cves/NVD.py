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

import requests, os, zipfile, json
from urllib.parse import urlparse
from datetime import datetime
from utils.temp_manager import TempManager
from utils.logger import Logger
from elasticsearch import Elasticsearch, helpers

TmpMgr = TempManager()
log = Logger("DEBUG")
es = Elasticsearch("http://localhost:9200") # TODO 2

def _upload_to_ES(cve_list: list): # TODO 1
    actions = [
        {
            "_index": "cves",
            "_id": c["cve_id"],
            "_source": c
        } for c in cve_list if c
    ]
    helpers.bulk(es, actions)

def __extract_ES_data(entry: dict) -> dict | None: # TODO 1
    cve_data = entry.get("cve", {})
    cve_id = cve_data.get("id")
    published = cve_data.get("published")
    modified = cve_data.get("lastModified")
    status = cve_data.get("vulnStatus")
    
    summary = ""
    for _desc in cve_data.get("descriptions"):
        if _desc.get("lang") == "en":
            summary = _desc.get("value")

    _metrics = cve_data.get("cve", {}).get("metrics")
    cvss_data = {}
    # Use V3.1 If available
    if "cvssMetricV31" in _metrics:
        v3 = _metrics["cvssMetricV31"][0]["cvssData"]
        cvss_data = {
            "version" : v3.get("version"),
            "base_score" : v3.get("baseScore"),
            "access_vector" : v3.get("attackVector"),
            "exploitability_score" : _metrics["cvssMetricV31"][1].get("exploitabilityScore")
        }
    # Fallback to V2.0 (legacy)
    elif "cvssMetricV2" in _metrics:
        v2 = _metrics["cvssMetricV2"][0]["cvssData"]
        cvss_data = {
            "version" : v2.get("version"),
            "base_score" : v2.get("baseScore"),
            "access_vector" : v2.get("attackVector"),
            "exploitability_score" : _metrics["cvssMetricV2"][1].get("exploitabilityScore")
        }

    return {
        "cve_id": cve_id,
        "published": published,
        "modified": modified,
        "status": status,
        "summary": summary,
        "cvss": cvss_data,
        "source": "nvd",
        "last_synced": datetime.utcnow().isoformat()
    }

def _parse_files(path:str): # TODO 1,3
    # Go through all files in folder
    es_data = {}
    for file in os.listdir(path):
        log.info(f"Processing file: {file}")

        js = json.loads(   # TODO 4
            open(
                os.path.join(path,file), encoding='utf-8'
            ).read()
        )
        
        for entry in js["vulnerabilities"]:
            formatted = __extract_ES_data(entry)
            es_data # add to this somehow

    return es_data

def _download_archive(URL):
    """Downloads a file from a URL to a temp dir, returns folder path to downloaded file"""

    parsed_url = urlparse(URL)
    filename = os.path.basename(parsed_url.path)
    log.debug(f"filename: {filename}")
    folder_path = TmpMgr.create_folder()
    log.debug(f"folder_path: {folder_path}")
    path = os.path.join(folder_path, filename)
    log.debug(f"path: {path}")
    zip_path = TmpMgr.create_file_bytes(path, requests.get(URL).content)
    log.debug(f"zip_path: {zip_path}")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(folder_path)
    
    os.remove(zip_path)

    return folder_path