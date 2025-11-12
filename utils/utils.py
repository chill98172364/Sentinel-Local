from utils.logger import Logger
from utils.constants import TimeUnits
import yaml, json, elasticsearch
from pathlib import Path
from datetime import datetime, timezone

log = Logger()

def get_config(feed:str,name:str):
    """Return the configuration dict for a specific feed source.

    Reads `config/sources.yaml` and looks up the `feed` section, then
    returns the feed entry whose `name` matches the provided `name`.

    Args:
        feed (str): Key under the top-level `feeds` mapping in sources.yaml.
        name (str): The `name` field of the specific feed to retrieve.

    Returns:
        dict: The feed configuration object matching `name`.

    Raises:
        KeyError: If `feed` is not present in the config or `name` not found.
    """
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
    """Get the last run datetime for a scraper by name.

    Reads `scraping/run_history.json` and returns the stored ISO 8601
    datetime string for the given `name`. If the stored value is an empty
    string this function returns ``None`` indicating a first-run or reset.

    Args:
        name (str): Key in `run_history.json` (typically camelCase name of the scraper).

    Returns:
        str | None: ISO 8601 UTC datetime string (no microseconds) or ``None`` when not set.
    """
    run_history_path = Path("scraping/run_history.json")
    with open(run_history_path, "r", encoding="utf-8") as f:
        run_history = json.loads(f.read())
    
    date = run_history[name]

    if date == "": # First build / Reset
        return None

    return date

# TODO 5
def update_run_date(name:str):
    """Update the run history for a scraper to the current UTC time.

    Loads `scraping/run_history.json`, sets the given `name` key to the
    current UTC time in ISO 8601 format (microseconds stripped), and
    writes the file back.

    Args:
        name (str): Key in `run_history.json` to update.

    Returns:
        None
    """
    run_history_path = Path("scraping/run_history.json")

    with open(run_history_path, "r", encoding="utf-8") as f:
        run_history = json.loads(f.read())
    
    current_gmt_time = datetime.now(timezone.utc)
    iso_gmt_string = current_gmt_time.replace(microsecond=0).isoformat()

    run_history[name] = iso_gmt_string

    with open(run_history_path, "w", encoding="utf-8") as f:
        f.write(json.dumps(run_history, indent=4))

def upload_CVE(cve_list: list):
    """Index a list of CVE objects into the Elasticsearch `cves` index.

    Each item in ``cve_list`` is expected to be a mapping containing a
    `cve_id` value which will be used as the document `_id`.

    Args:
        cve_list (list[dict]): List of CVE mappings to index.
    """
    actions = [
        {
            "_index": "cves",
            "_id": c["cve_id"],
            "_source": c
        } for c in cve_list if c
    ]
    helpers.bulk(es, actions)

def upload_RSS(rss_data: list):
    """Upload scraped RSS items to Elasticsearch 'news' index.

    Each item in ``rss_data`` is expected to be a mapping containing a
    `title` value which will be used as the document `_id`.

    Args:
        rss_data (iterable[dict]): Iterable of RSS item mappings to index.
    """
    # Strictly for debugging purposes: save a snapshot so I can inspect it
    file_path = Path("tmp.json")
    open(file_path, "w", encoding="utf-8").write(json.dumps(rss_data))
    log.debug("Saved data to tmp.json in cwd")

    # The indexing logic is left in place but intentionally not executed
    # during some debug runs. Uncomment the following lines to enable bulk upload.
    # actions = [
    #     {
    #         "_index": "news",
    #         "_id": r.get("title") or None,
    #         "_source": r
    #     } for r in rss_data if r
    # ]
    # helpers.bulk(es, actions)

def parse_interval(interval_str: str) -> int:
    """Convert a human-readable schedule string into seconds.

    Supported formats:
      - "N_unit" (e.g. "5_minutes", "1_hour")
      - "unit" (defaults to 1, e.g. "hour" -> 3600)

    Units supported: minute(s), hour(s), day(s).

    Args:
        interval_str (str): Schedule string.

    Returns:
        int: Number of seconds represented by the interval. Defaults to 3600 (1 hour)
             when the unit is unknown.
    """
    num, unit = interval_str.split("_") if "_" in interval_str else (1, interval_str)
    try:
        num = int(num)
    except ValueError:
        num = 1
    
    try:
        converted = num * TimeUnits[unit.rstrip("s")]
        log.debug(f"Converted {interval_str} to {converted}s")
        return converted
    except KeyError:
        log.error(f"Unkown time unit: {unit}. Defaulting to 1 hour")
        return TimeUnits.hour
