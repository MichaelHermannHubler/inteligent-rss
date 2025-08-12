from typing import List, Dict, Any
from ..base_source import BaseSource, RSSItem
from .generic_rss import GenericRSSSource


class TechCrunchSource(GenericRSSSource):
    """TechCrunch RSS source with custom processing"""
    
    def __init__(self):
        super().__init__(
            name="TechCrunch",
            url="https://techcrunch.com/feed/"
        )
    
    def consume(self) -> List[RSSItem]:
        """Consume TechCrunch RSS feed with custom processing"""
        items = super().consume()
        
        # Add custom processing for TechCrunch items
        for item in items:
            # Clean up TechCrunch specific content
            if item.content.startswith('TechCrunch'):
                item.content = item.content.replace('TechCrunch', '').strip()
            
            # Add source-specific metadata
            item.source = "TechCrunch"
        
        return items
    
    def get_source_info(self) -> Dict[str, Any]:
        """Get TechCrunch specific source info"""
        info = super().get_source_info()
        info['category'] = 'Technology News'
        info['region'] = 'Global'
        return info 