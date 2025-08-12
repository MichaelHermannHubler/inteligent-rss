from typing import List, Dict, Any
from ..base_source import BaseSource, RSSItem
from .generic_rss import GenericRSSSource


class RedditSource(GenericRSSSource):
    """Reddit RSS source for specific subreddits"""
    
    def __init__(self, subreddit: str):
        url = f"https://www.reddit.com/r/{subreddit}/.rss"
        super().__init__(
            name=f"Reddit r/{subreddit}",
            url=url
        )
        self.subreddit = subreddit
    
    def consume(self) -> List[RSSItem]:
        """Consume Reddit RSS feed with custom processing"""
        items = super().consume()
        
        # Add Reddit-specific processing
        for item in items:
            # Clean up Reddit specific content
            if item.content.startswith('submitted by'):
                item.content = item.content.split('submitted by')[0].strip()
            
            # Add subreddit information
            item.source = f"Reddit r/{self.subreddit}"
            
            # Extract Reddit-specific metadata if available
            if 'reddit' in item.link:
                item.guid = item.link  # Reddit URLs are unique
        
        return items
    
    def get_source_info(self) -> Dict[str, Any]:
        """Get Reddit specific source info"""
        info = super().get_source_info()
        info['platform'] = 'Reddit'
        info['subreddit'] = self.subreddit
        info['category'] = 'Social Media'
        return info 