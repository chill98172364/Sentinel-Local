import yaml
from pathlib import Path
from utils.logger import Logger
import elasticsearch

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

def CVE_to_ES(cve_list: list):
    """Adds a CVE list to elastic search"""
    actions = [
        {
            "_index": "cves",
            "_id": c["cve_id"],
            "_source": c
        } for c in cve_list if c
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
