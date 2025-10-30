# GET "https://www.darkreading.com/rss.xml"
# XML like structure
# 
# go by each <item>
# extract title, description, pubDate
# then GET "{<link>}"
# Use Beautiful Soup to extract content

# reaaaaalllyyyy similar to hackernews.py

import feedparser, time
import cloudscraper
from bs4 import BeautifulSoup
from utils.utils import get_config
from utils.logger import Logger
from utils.utils import parse_interval

log = Logger()
config = get_config("news","Dark Reading")

def __extract_contents(URL:str):
    ses = cloudscraper.CloudScraper()
    r = ses.get(URL)
    parser = BeautifulSoup(r.text, 'html.parser')

    div = parser.find("div", {"class": "ArticleBase-BodyContent ArticleBase-BodyContent_Article"})
    if div == None:
        log.error("Couldn't find paragraph DIV")
        return "[Error scraping webpage]"
    content = ""
    for paragraph in div:
        content = f"{content}\n{paragraph.text}"
    
    return content

# FUNCTION __process_loop(config, scraper_func):
#     interval_seconds = parse_interval(config["schedule"])

#     LOOP FOREVER:
#         LOG "Starting scrape"
#         data = scraper_func()
#         SAVE data to disk or Elasticsearch
#         LOG "Completed scrape"

#         LOG "Sleeping for interval_seconds"
#         WAIT interval_seconds seconds


def __process_loop():
    # Remember to update scraping/run_history.json

    interval_seconds = parse_interval(config["schedule"])

    while True:
        log.info("Scraping Dark Reading")
        #data = 


        time.sleep(interval_seconds)
    

def _extract_RSS():
    URL = config["url"]
    
    data = []
    feed = feedparser.parse(URL)
    for entry in feed.entries:
        _pub_obj = entry["published_parsed"]
        iso_date = time.strftime("%Y-%m-%d", _pub_obj)
        content = __extract_contents(entry["link"])
        data.append(
            {
                "title":entry["title"],
                "description":entry["summary"],
                "published":iso_date,
                "author":entry["author"],
                "url":entry["link"],
                "content":content
            }
        )
        log.info(f'Parsed: {entry["title"]}')

    return data

# ==================================================================
# Not sure where to add this logic but:                            #
# 1. Store most recent news title                                  #
# 2. Start loop, feed it the last title it scraped                 #
# 3. After time.sleep(2_hours), get all the news articles after it #
#                                                                  #
# Can also store the pubDate                                       #
# dont waste time scraping the contents if you dont need to        #
# ==================================================================

def main():
    _extract_RSS()