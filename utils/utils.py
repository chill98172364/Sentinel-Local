from utils.logger import Logger
import yaml, json, elasticsearch
from pathlib import Path
from datetime import datetime, timezone

log = Logger()

def get_config(feed:str,name:str):
    """Returns a Json obj for specific source within config/sources.yaml"""
    config_path = Path("config/sources.yaml")
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    
    # Navigate to the section
    feeds = config["feeds"]
    specific_feeds = feeds[feed]

    blog = next(feed for feed in specific_feeds if feed["name"] == name)

    return blog

# TODO 5
def get_run_date(name:str) -> str:
    """Returns the last run date of specific ......... given the name from scraping/run_history.json. returns: ISO format, name: camelCase """
    run_history_path = Path("scraping/run_history.json")
    with open(run_history_path, "r", encoding="utf-8") as f:
        run_history = json.loads(f.read())
    
    return run_history[name]

# TODO 5
def update_run_date(name:str):
    """Updates the run date (GMT) of specific ..... within scraping/run_history.json"""
    run_history_path = Path("scraping/run_history.json")
    with open(run_history_path, "r", encoding="utf-8") as f:
        run_history = json.loads(f.read())
    
    current_gmt_time = datetime.now(timezone.utc)
    iso_gmt_string = current_gmt_time.replace(microsecond=0).isoformat()

    run_history[name] = iso_gmt_string

def upload_CVE(cve_list: list):
    """Adds a CVE list to elastic search"""
    actions = [
        {
            "_index": "cves",
            "_id": c["cve_id"],
            "_source": c
        } for c in cve_list if c
    ]
    helpers.bulk(es, actions)

def upload_RSS(rss_data):
    """Uploads scraped RSS data to elastic search"""
    actions = [
        {
            "_index": "news",
            "_id": "darkReading",
            "_source": r
        } for r in rss_data if r
    ]
    helpers.bulk(es, actions)

def parse_interval(interval_str: str) -> int:
    """Convert schedule string into seconds."""
    units = {
        "minute": 60,
        "minutes": 60,
        "hour": 3600,
        "hours": 3600,
        "day": 86400,
        "days": 86400,
    }
    num, unit = interval_str.split("_") if "_" in interval_str else (1, interval_str)
    try:
        num = int(num)
    except ValueError:
        num = 1
    
    converted = num * units.get(unit.rstrip("s"), 3600)  # default to 1h
    log.debug(f"Converted {interval_str} to {converted}s")
    return converted
