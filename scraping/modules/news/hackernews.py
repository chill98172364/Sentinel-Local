# GET "https://feeds.feedburner.com/TheHackersNews"
# XML like structure
# 
# go by each <item>
# extract title, description, pubDate
# then GET "{<link>}"
# Use Beautiful Soup to extract content