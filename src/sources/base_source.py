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


class BaseSource(ABC):
    """Base interface for all RSS sources"""
    url: str # URL of the RSS feed

    def __init__(self, name: str):
        self.name = name
    
    @abstractmethod
    def consume(self) -> List[RSSItem]:
        """
        Consume the RSS feed and return a list of RSSItem objects
        
        Returns:
            List[RSSItem]: List of parsed RSS items
        """
        pass
    
    def __str__(self):
        return f"{self.name} ({self.url})"
    
    def __repr__(self):
        return f"<{self.__class__.__name__}(name='{self.name}', url='{self.url}')>" 