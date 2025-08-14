"""
Example custom RSS source implementation

This file demonstrates how to create a custom RSS source by inheriting from BaseSource.
You can use this as a template to create sources for specific websites or RSS feeds.
"""

from typing import List, Dict, Any
from .BaseSource import BaseSource, RSSItem
from .GenericRSS import GenericRSSSource


class CustomSourceExample(GenericRSSSource):
    """
    Example custom source that demonstrates custom processing
    
    This source inherits from GenericRSSSource and adds custom logic
    specific to a particular website or RSS feed.
    """
    
    def __init__(self, name: str, url: str, custom_param: str = None):
        """
        Initialize the custom source
        
        Args:
            name: Name of the source
            url: RSS feed URL
            custom_param: Custom parameter for this source
        """
        super().__init__(name, url)
        self.custom_param = custom_param
    
    def consume(self) -> List[RSSItem]:
        """
        Consume the RSS feed with custom processing
        
        Returns:
            List of processed RSS items
        """
        # Get items from parent class
        items = super().consume()
        
        # Apply custom processing
        processed_items = []
        for item in items:
            # Example: Filter items based on custom criteria
            if self._should_process_item(item):
                # Apply custom transformations
                processed_item = self._apply_custom_processing(item)
                processed_items.append(processed_item)
        
        return processed_items
    
    def _should_process_item(self, item: RSSItem) -> bool:
        """
        Determine if an item should be processed
        
        Args:
            item: RSS item to check
            
        Returns:
            True if item should be processed, False otherwise
        """
        # Example: Only process items with certain keywords
        keywords = ['python', 'programming', 'technology']
        content_lower = item.content.lower()
        
        return any(keyword in content_lower for keyword in keywords)
    
    def _apply_custom_processing(self, item: RSSItem) -> RSSItem:
        """
        Apply custom processing to an RSS item
        
        Args:
            item: RSS item to process
            
        Returns:
            Processed RSS item
        """
        # Example: Add custom metadata
        if self.custom_param:
            item.description = f"[{self.custom_param}] {item.description}"
        
        # Example: Clean up content
        item.content = self._clean_content(item.content)
        
        # Example: Add source-specific tags
        item.source = f"{item.source} (Custom)"
        
        return item
    
    def _clean_content(self, content: str) -> str:
        """
        Clean up content text
        
        Args:
            content: Raw content text
            
        Returns:
            Cleaned content text
        """
        # Example: Remove common HTML artifacts
        content = content.replace('&nbsp;', ' ')
        content = content.replace('&amp;', '&')
        content = content.replace('&lt;', '<')
        content = content.replace('&gt;', '>')
        
        # Example: Remove excessive whitespace
        import re
        content = re.sub(r'\s+', ' ', content)
        
        return content.strip()
    
    def get_source_info(self) -> Dict[str, Any]:
        """
        Get custom source information
        
        Returns:
            Dictionary with source metadata
        """
        info = super().get_source_info()
        
        # Add custom information
        info['custom_param'] = self.custom_param
        info['processing_type'] = 'Custom'
        info['filters_applied'] = 'Keyword filtering, content cleaning'
        
        return info


class BlogSource(GenericRSSSource):
    """
    Example source for a specific blog with custom parsing
    
    This demonstrates how to create a source for a specific website
    that might need custom parsing logic.
    """
    
    def __init__(self, blog_name: str, feed_url: str):
        super().__init__(blog_name, feed_url)
        self.blog_name = blog_name
    
    def consume(self) -> List[RSSItem]:
        """Consume blog RSS feed with custom parsing"""
        items = super().consume()
        
        # Apply blog-specific processing
        for item in items:
            # Extract author information if available
            if hasattr(item, 'author') and not item.author:
                item.author = self._extract_author_from_content(item.content)
            
            # Add blog-specific metadata
            item.source = f"{self.blog_name} Blog"
            
            # Clean up blog-specific content
            item.content = self._clean_blog_content(item.content)
        
        return items
    
    def _extract_author_from_content(self, content: str) -> str:
        """Extract author information from content"""
        # This is a placeholder - implement based on your blog's format
        import re
        
        # Example: Look for "By [Author Name]" pattern
        author_match = re.search(r'By\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', content)
        if author_match:
            return author_match.group(1)
        
        return "Unknown Author"
    
    def _clean_blog_content(self, content: str) -> str:
        """Clean up blog-specific content"""
        # Remove common blog artifacts
        content = content.replace('Read more...', '')
        content = content.replace('Continue reading...', '')
        
        # Remove social media sharing buttons text
        content = content.replace('Share this:', '')
        content = content.replace('Tweet this:', '')
        
        return content.strip()


# Example usage functions
def create_custom_sources():
    """Create examples of custom sources"""
    sources = [
        # Custom source with filtering
        CustomSourceExample(
            name="Tech Blog Filtered",
            url="https://example-tech-blog.com/feed/",
            custom_param="AI/ML Focus"
        ),
        
        # Blog source
        BlogSource(
            blog_name="Python Weekly",
            feed_url="https://www.pythonweekly.com/rss.xml"
        ),
    ]
    return sources


if __name__ == "__main__":
    # Example of how to use custom sources
    print("Custom Source Examples:")
    
    # Create a custom source
    custom_source = CustomSourceExample(
        name="Example Source",
        url="https://example.com/feed/",
        custom_param="Custom Processing"
    )
    
    print(f"Source: {custom_source}")
    print(f"Custom param: {custom_source.custom_param}")
    
    # Show source info
    info = custom_source.get_source_info()
    print(f"Source info: {info}") 