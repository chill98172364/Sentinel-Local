import yaml
from pathlib import Path
import elasticsearch

def get_config(feed:str,name:str):
    config_path = Path("config/sources.yaml")
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    
    # Navigate to the section
    feeds = config["feeds"]
    specific_feeds = feeds[feed]

    blog = next(feed for feed in specific_feeds if feed["name"] == name)

    return blog

def _upload_to_ES(cve_list: list): # TODO 1
    actions = [
        {
            "_index": "cves",
            "_id": c["cve_id"],
            "_source": c
        } for c in cve_list if c
    ]
    helpers.bulk(es, actions)