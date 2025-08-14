import feedparser
import requests
from datetime import datetime
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from .base_source import BaseSource, RSSItem


class GenericRSSSource(BaseSource):
    """Generic RSS source that can handle most standard RSS feeds"""
    
    def __init__(self, name: str, url: str, timeout: int = 30):
        super().__init__(name, url)
        self.timeout = timeout
    
    def consume(self) -> List[RSSItem]:
        """Consume the RSS feed and return parsed items"""
        try:
            # Parse the RSS feed
            feed = feedparser.parse(self.url)
            
            if feed.bozo:
                print(f"Warning: Feed {self.name} has parsing issues")
            
            items = []
            for entry in feed.entries:
                try:
                    # Extract content
                    content = self._extract_content(entry)
                    
                    # Parse publication date
                    published = self._parse_date(entry)
                    
                    # Create RSS item
                    item = RSSItem(
                        title=entry.get('title', 'No Title'),
                        link=entry.get('link', ''),
                        description=entry.get('description', ''),
                        published=published,
                        content=content,
                        source=self.name,
                        guid=entry.get('id', entry.get('link', ''))
                    )
                    items.append(item)
                    
                except Exception as e:
                    print(f"Error processing item from {self.name}: {e}")
                    continue
            
            return items
            
        except Exception as e:
            print(f"Error consuming feed {self.name}: {e}")
            return []
    
    def _extract_content(self, entry) -> str:
        """Extract content from RSS entry"""
        # Try different content fields
        content_fields = ['content', 'summary', 'description']
        
        for field in content_fields:
            if field in entry:
                content = entry[field]
                if isinstance(content, list) and len(content) > 0:
                    content = content[0].get('value', '')
                elif isinstance(content, str):
                    pass
                else:
                    continue
                
                if content:
                    # Clean HTML tags if present
                    soup = BeautifulSoup(content, 'html.parser')
                    return soup.get_text(strip=True)
        
        return entry.get('description', '')
    
    def _parse_date(self, entry) -> datetime:
        """Parse publication date from entry"""
        date_fields = ['published_parsed', 'updated_parsed', 'created_parsed']
        
        for field in date_fields:
            if field in entry and entry[field]:
                try:
                    return datetime(*entry[field][:6])
                except (ValueError, TypeError):
                    continue
        
        # Fallback to current time
        return datetime.now()
    
    def get_source_info(self) -> Dict[str, Any]:
        """Get source metadata"""
        try:
            feed = feedparser.parse(self.url)
            return {
                'name': self.name,
                'url': self.url,
                'title': getattr(feed.feed, 'title', 'Unknown'),
                'description': getattr(feed.feed, 'description', ''),
                'language': getattr(feed.feed, 'language', ''),
                'last_updated': getattr(feed.feed, 'updated', ''),
                'item_count': len(feed.entries) if hasattr(feed, 'entries') else 0
            }
        except Exception as e:
            return {
                'name': self.name,
                'url': self.url,
                'error': str(e)
            } 