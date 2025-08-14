import sys
from sources.OTSRSS import OTSRSSSource
from sources.ORFNewsRSS import ORFNewsRSSSource
from database.RSSDatabase import RSSDatabase
from llm.ArticleQueryMatcher import ArticleQueryMatcher
import itertools

import feedparser

if __name__ == "__main__":
    print('Init')

    sources = [
        OTSRSSSource(name="OTS RSS Feed"),
        ORFNewsRSSSource(name="ORF News RSS Feed")
    ]

    #sources[0].consume() 

    database = RSSDatabase() 
    matcher = ArticleQueryMatcher()

    for source in sources:
        print(f'Consuming RSS feed {source.name}')
        items = source.consume()
        database.store_source_info(source.name, source.url)
        database.store_rss_items(items)

        open_queries = database.get_queries(False)  # Fetch unresolved queries

        for item, query in itertools.product(items, open_queries):
            result = matcher.check_match(item.content, query['query'])
            database.store_llm_results(query['id'], item.title, source.name, result)
            
            if result:
                print(f"Query '{query['query']}' matched with item '{item.title}' from source '{source.name}'")
                database.resolve_query(query['id'], item.title, source.name)