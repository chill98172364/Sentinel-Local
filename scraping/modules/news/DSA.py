# GET "https://ubuntu.com/security/notices/rss.xml"
# certified RSS moment
# 
# go by each <item>
# extract title, description, pubDate
# then GET "{<link>}"
# Use Beautiful Soup to extract content