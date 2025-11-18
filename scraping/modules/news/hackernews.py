# GET "https://feeds.feedburner.com/TheHackersNews"
# XML like structure
# 
# go by each <item>
# extract title, description, pubDate
# then GET "{<link>}"
# Use Beautiful Soup to extract content

import utils.utils as utils
from utils.logger import Logger
from utils.constants import AdvisorySource

import feedparser, time
import cloudscraper
from bs4 import BeautifulSoup

log = Logger()

def _extract_contents(URL:str):
    ses = cloudscraper.CloudScraper()
    r = ses.get(URL)
    parser = BeautifulSoup(r.text, 'html.parser')

    div = parser.find("div", {"class": "articlebody clear cf", "id": "articlebody"})
    if div == None:
        log.error("Couldn't find paragraph DIV")
        return "[Error scraping webpage]"
    content = ""
    for paragraph in div:
        if len(paragraph.text) > 5:
            content = f"{content}\n{paragraph.text}"
    
    return content

def _extract_RSS(URL, from_date):
    """Extracts data from RSS field"""
    data = []
    feed = feedparser.parse(URL)
    for entry in feed.entries:
        # if "thehackernews.com/events" in entry["link"]:
        #     log.debug("Skipping event")
        #     continue

        _pub_obj = entry["published_parsed"]
        pub_date = time.strftime("%Y-%m-%d", _pub_obj)

        if from_date != None and pub_date < from_date:
            log.debug(f"Skipping article (pub_date: {pub_date})")
            continue

        content = _extract_contents(entry["link"])
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
    config = utils.get_config("news","The Hacker News")
    last_run = utils.get_run_date(AdvisorySource.HACKER_NEWS.value)

    interval_seconds = utils.parse_interval(config["schedule"])

    while True:
        log.info("Scraping Hacker News...")
        
        rss_data = _extract_RSS(config["url"], last_run)
        utils.upload_RSS(rss_data) # Converted to saving to disk for debugging purposes

        utils.update_run_date(AdvisorySource.HACKER_NEWS.value)
        log.debug(f"Finished scraping Hacker News, waiting {interval_seconds}s")
        time.sleep(interval_seconds)

def main():
    _start_scrape()