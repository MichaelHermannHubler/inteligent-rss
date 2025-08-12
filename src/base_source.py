from abc import ABC, abstractmethod
from typing import List, Dict, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class RSSItem:
    """Represents a single RSS feed item"""
    title: str
    link: str
    description: str
    published: datetime
    content: str
    source: str
    guid: str


class BaseSource(ABC):
    """Base interface for all RSS sources"""
    
    def __init__(self, name: str, url: str):
        self.name = name
        self.url = url
    
    @abstractmethod
    def consume(self) -> List[RSSItem]:
        """
        Consume the RSS feed and return a list of RSSItem objects
        
        Returns:
            List[RSSItem]: List of parsed RSS items
        """
        pass
    
    @abstractmethod
    def get_source_info(self) -> Dict[str, Any]:
        """
        Get information about the source
        
        Returns:
            Dict[str, Any]: Source metadata
        """
        pass
    
    def __str__(self):
        return f"{self.name} ({self.url})"
    
    def __repr__(self):
        return f"<{self.__class__.__name__}(name='{self.name}', url='{self.url}')>" 