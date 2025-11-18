import utils.utils as utils
from utils.logger import Logger
from utils.constants import AdvisorySource

import feedparser, time
import cloudscraper
from bs4 import BeautifulSoup

log = Logger()

def _extract_info(URL:str):
    ses = cloudscraper.CloudScraper()
    r = ses.get(URL)
    parser = BeautifulSoup(r.text, 'html.parser')
    content = ""
    author = ""

    # Scrape paragraphs
    raw_content = parser.find("div", {"class": "rh-generic--component"})
    if raw_content == None:
        log.error("Couldn't find paragraph DIV")
        content = "[Error scraping webpage]"
    else:
        for paragraph in raw_content:
            if len(paragraph.text) > 5:
                content = f"{content}\n{paragraph.text}"
    
    # Scrape author
    author_text = parser.find("span", {"class": "rh-article-teaser-hero-author"})
    if author_text == None:
        log.error("Couldn't find author text")
        author =  "[Error scraping author name]"
    else:
        author = author_text.get_text()
        author = " ".join(author.split())

    return content, author

def _extract_RSS(URL, from_date):
    """Extracts data from RSS field"""
    data = []
    feed = feedparser.parse(URL)

    for entry in feed.entries:

        _pub_obj = entry["published_parsed"]
        pub_date = time.strftime("%Y-%m-%d", _pub_obj)

        if from_date != None and pub_date < from_date:
            log.debug(f"Skipping article (pub_date: {pub_date})")
            continue

        content, author = _extract_info(entry["link"])
        data.append(
            {
                "title":entry["title"],
                "description":entry["summary"],
                "published":pub_date,
                "author":author,
                "url":entry["link"],
                "content":content
            }
        )
        log.info(f'Parsed: {entry["title"]}')

    return data

def _start_scrape():
    config = utils.get_config("advisories","Red Hat Security") 
    last_run = utils.get_run_date(AdvisorySource.RED_HAT.value)

    interval_seconds = utils.parse_interval(config["schedule"])

    while True:
        log.info("Scraping Red Hat...")
        
        rss_data = _extract_RSS(config["url"], last_run)
        utils.upload_RSS(rss_data) # Converted to saving to disk for debugging purposes

        utils.update_run_date(AdvisorySource.RED_HAT.value)
        log.debug(f"Finished scraping Red Hat, waiting {interval_seconds}s")
        time.sleep(interval_seconds)

def main():
    _start_scrape()
    