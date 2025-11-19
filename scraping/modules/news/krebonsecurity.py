# GET "https://krebsonsecurity.com/feed"
# in HTML/XML like code, parse for ES fields
# shouldnt be terribly difficult

import utils.utils as utils
from utils.logger import Logger
from utils.constants import AdvisorySource

import feedparser, time, json
import cloudscraper
from bs4 import BeautifulSoup

log = Logger()

def _extract_content(entry_content:json):
    raw_content = entry_content[0]["value"]
    parser = BeautifulSoup(raw_content, "html.parser")
    text = parser.get_text()
    return text

def _extract_XML(URL, from_date):
    """Extracts data from RSS field"""
    data = []
    feed = feedparser.parse(URL)
    for entry in feed.entries:

        _pub_obj = entry["published_parsed"]
        pub_date = time.strftime("%Y-%m-%d", _pub_obj)

        content = _extract_content(entry["content"])

        data.append(
            {
                "title":entry["title"],
                "description":entry["summary"],
                "published":pub_date,
                "author":entry["author"],
                "url":entry["link"],
                "content":content
            }
        )
        log.info(f'Parsed: {entry["title"]}')

    return data

def _start_scrape():
    config = utils.get_config("news","Krebs on Security")
    last_run = utils.get_run_date(AdvisorySource.KERBON_SECURITY.value)

    interval_seconds = utils.parse_interval(config["schedule"])

    while True:
        log.info("Scraping Krebs on Security...")
        
        xml_data = _extract_XML(config["url"], last_run)
        utils.upload_RSS(xml_data) # Converted to saving to disk for debugging purposes

        utils.update_run_date(AdvisorySource.KERBON_SECURITY.value)
        log.debug(f"Finished scraping Krebs on Security, waiting {interval_seconds}s")
        time.sleep(interval_seconds)

def main():
    _start_scrape()