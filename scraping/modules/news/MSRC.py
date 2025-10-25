# Microsoft Security Response Center (MSRC)
# GET "https://api.msrc.microsoft.com/update-guide/rss"
# XML Structure
#
# inter through each <item> in <channel>
# extract title, description, pubDate, category (for ES)
#
# GET "{<link>}"
# beautiful soup to extract contents