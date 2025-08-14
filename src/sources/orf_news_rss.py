"""
Example custom RSS source implementation

This file demonstrates how to create a custom RSS source by inheriting from BaseSource.
You can use this as a template to create sources for specific websites or RSS feeds.
"""

from typing import List, Dict, Any

from .utils import get_content_from_link
from .base_source import BaseSource, RSSItem

import feedparser


class ORFNewsRSSSource(BaseSource):
    """
    OTS RSS source implementation
    """
    
    def __init__(self, name: str):
        """
        Initialize the OTS RSS source
        
        Args:
            name: Name of the source
            url: RSS feed URL
        """
        super().__init__(name)
        self.url = 'https://rss.orf.at/news.xml'  
    
    def consume(self) -> List[RSSItem]:
        """
        Consume the RSS feed and return a list of RSSItem objects
        
        Returns:
            List[RSSItem]: List of parsed RSS items
        """
        # Custom logic to fetch and parse the RSS feed would go here
        feed = feedparser.parse(self.url)
        return [
            RSSItem(
                title=item.title,
                link=item.link,
                description=item.title,  # ORF News RSS does not provide a description
                published=item.updated,
                content=get_content_from_link(item.link, class_name='story-story'),
                source=self.name
            )
            for item in feed.entries
        ]