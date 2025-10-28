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

log = Logger("DEBUG")

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

def _extract_RSS():
    config = get_config("news","Dark Reading")
    URL = config["url"]
    scheule = config["schedule"]
    
    data = []
    feed = feedparser.parse(URL)
    for entry in feed.entries:
        _pub_obj = entry["published_parsed"]
        iso_date = time.strftime("%Y-%m-%d", _pub_obj)
        content = __extract_contents(entry["link"])
        data.append(
            {
                "title":entry["title"],         #["title"]
                "description":entry["summary"], #["summary"]
                "published":iso_date,           #["published_parsed"]
                "author":entry["author"],       #["author"]
                "url":entry["link"],            #["link"]
                "content":content
            }
        )
        log.info(f'Parsed: {entry["title"]}')
    
    # TODO, start x hour loop (config/souces.yaml)
    # Maybe it can be generalized and put into utils/utils.py

    return data