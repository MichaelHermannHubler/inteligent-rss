import sys
from sources.ots_rss import OTSRSSSource
from sources.orf_news_rss import ORFNewsRSSSource
from database.RSSDatabase import RSSDatabase

import feedparser

if __name__ == "__main__":
    print('Init')

    sources = [
        OTSRSSSource(name="OTS RSS Feed"),
        ORFNewsRSSSource(name="ORF News RSS Feed")
    ]
    database = RSSDatabase() 

    for source in sources:
        print(f'Consuming RSS feed {source.name}')
        items = source.consume()
        database.store_source_info(source.name, source.url)
        database.store_rss_items(items)

        for item in items:
            print(f"Title: {item.title}, Link: {item.link}, Published: {item.published}")