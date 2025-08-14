import sqlite3
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path

from sources.base_source import RSSItem
from .utils import adapt_timeobj, convert_timeobj


class RSSDatabase:
    """SQLite database for storing RSS items and LLM processing results"""
    
    def __init__(self, db_path: str = "rss_data.db"):
        """
        Initialize the database
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path

        # Converts DT.time to TEXT when inserting
        sqlite3.register_adapter(datetime.time, adapt_timeobj)

        # Converts TEXT to DT.time when selecting
        sqlite3.register_converter("timeobj", convert_timeobj)

        self._create_tables()
    
    def _create_tables(self):
        """Create the necessary database tables"""
        with sqlite3.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES) as conn:
            cursor = conn.cursor()
            
            # Create RSS items table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS rss_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    link TEXT NOT NULL,
                    description TEXT,
                    content TEXT,
                    published TEXT NOT NULL,
                    source ID NOT NULL,
                    FOREIGN KEY (source) REFERENCES sources(name)
                )
            ''')
            
            # Create LLM processing results table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS llm_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    item_id INTEGER NOT NULL,
                    item_title TEXT NOT NULL,
                    item_source TEXT NOT NULL,
                    query TEXT NOT NULL,
                    relevance_score INTEGER NOT NULL,
                    relevance TEXT NOT NULL,
                    explanation TEXT,
                    key_information TEXT,
                    summary TEXT,
                    llm_response TEXT,
                    processed_at TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (item_id) REFERENCES rss_items (id)
                )
            ''')
            
            # Create sources table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sources (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    url TEXT NOT NULL,
                    last_consumed TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create indexes for better performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_rss_items_source ON rss_items(source)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_rss_items_published ON rss_items(published)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_llm_results_query ON llm_results(query)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_llm_results_score ON llm_results(relevance_score)')
            
            conn.commit()
    
    def store_rss_items(self, items: List[RSSItem]) -> int:
        """
        Store RSS items in the database
        
        Args:
            items: List of RSS items to store
            
        Returns:
            Number of items successfully stored
        """
        stored_count = 0
        
        with sqlite3.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES) as conn:
            cursor = conn.cursor()
            
            for item in items:
                try:
                    cursor.execute('SELECT id FROM rss_items WHERE link = ? AND source = ?', (item.link, item.source))
                    exists = cursor.fetchone()
                    if exists:
                        continue  # Skip if already exists

                    cursor.execute('''
                        INSERT OR REPLACE INTO rss_items 
                        (title, link, description, content, published, source)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        item.title,
                        item.link,
                        item.description,
                        item.content,
                        item.published,
                        item.source
                    ))
                    stored_count += 1
                    
                except sqlite3.Error as e:
                    print(f"Error storing RSS item '{item.title}': {e}")
                    continue
            
            conn.commit()
        
        return stored_count
    
    def store_llm_results(self, results: List[Dict[str, Any]]) -> int:
        """
        Store LLM processing results in the database
        
        Args:
            results: List of LLM processing results to store
            
        Returns:
            Number of results successfully stored
        """
        stored_count = 0
        
        with sqlite3.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES) as conn:
            cursor = conn.cursor()
            
            for result in results:
                try:
                    cursor.execute('''
                        INSERT INTO llm_results 
                        (item_guid, item_title, item_source, query, relevance_score, 
                         relevance, explanation, key_information, summary, llm_response, processed_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        result['item_guid'],
                        result['item_title'],
                        result['item_source'],
                        result['query'],
                        result['relevance_score'],
                        result['relevance'],
                        result['explanation'],
                        result['key_information'],
                        result['summary'],
                        result['llm_response'],
                        result['processed_at']
                    ))
                    stored_count += 1
                    
                except sqlite3.Error as e:
                    print(f"Error storing LLM result for '{result.get('item_title', 'Unknown')}': {e}")
                    continue
            
            conn.commit()
        
        return stored_count
    
    def store_source_info(self, name: str, url: str):
        """
        Store or update source information
        
        Args:
            source_info: Source metadata to store
        """
        with sqlite3.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES) as conn:
            cursor = conn.cursor()
            
            try:
                cursor.execute('''
                    INSERT OR REPLACE INTO sources 
                    (name, url, last_consumed)
                    VALUES (?, ?, ?)
                ''', (
                    name,
                    url,
                    datetime.now().isoformat(),
                ))
                
                conn.commit()
                
            except sqlite3.Error as e:
                print(f"Error storing source info for '{source_info.get('name', 'Unknown')}': {e}")
    
    def get_relevant_items(self, query: str, min_score: int = 50, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get items relevant to a specific query
        
        Args:
            query: The search query
            min_score: Minimum relevance score (0-100)
            limit: Maximum number of results to return
            
        Returns:
            List of relevant items with their LLM analysis
        """
        with sqlite3.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    r.guid, r.title, r.link, r.description, r.content, 
                    r.published, r.source, r.created_at,
                    l.relevance_score, l.relevance, l.explanation, 
                    l.key_information, l.summary, l.llm_response
                FROM rss_items r
                JOIN llm_results l ON r.guid = l.item_guid
                WHERE l.query = ? AND l.relevance_score >= ?
                ORDER BY l.relevance_score DESC, r.published DESC
                LIMIT ?
            ''', (query, min_score, limit))
            
            columns = [description[0] for description in cursor.description]
            results = []
            
            for row in cursor.fetchall():
                result = dict(zip(columns, row))
                results.append(result)
            
            return results
    
    def get_source_stats(self) -> List[Dict[str, Any]]:
        """
        Get statistics for all sources
        
        Returns:
            List of source statistics
        """
        with sqlite3.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    s.name, s.url, s.last_consumed, s.item_count, s.created_at,
                    COUNT(l.id) as processed_count,
                    AVG(l.relevance_score) as avg_relevance_score
                FROM sources s
                LEFT JOIN llm_results l ON s.name = l.item_source
                GROUP BY s.id, s.name, s.url, s.last_consumed, s.item_count, s.created_at
                ORDER BY s.name
            ''')
            
            columns = [description[0] for description in cursor.description]
            results = []
            
            for row in cursor.fetchall():
                result = dict(zip(columns, row))
                results.append(result)
            
            return results
    
    def get_query_stats(self) -> List[Dict[str, Any]]:
        """
        Get statistics for all queries
        
        Returns:
            List of query statistics
        """
        with sqlite3.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    query,
                    COUNT(*) as total_items,
                    AVG(relevance_score) as avg_relevance_score,
                    COUNT(CASE WHEN relevance_score >= 70 THEN 1 END) as highly_relevant,
                    COUNT(CASE WHEN relevance_score >= 50 THEN 1 END) as relevant,
                    COUNT(CASE WHEN relevance_score < 50 THEN 1 END) as not_relevant
                FROM llm_results
                GROUP BY query
                ORDER BY total_items DESC
            ''')
            
            columns = [description[0] for description in cursor.description]
            results = []
            
            for row in cursor.fetchall():
                result = dict(zip(columns, row))
                results.append(result)
            
            return results
    
    def cleanup_old_items(self, days_old: int = 30):
        """
        Clean up old RSS items and their LLM results
        
        Args:
            days_old: Remove items older than this many days
        """
        with sqlite3.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES) as conn:
            cursor = conn.cursor()
            
            try:
                # Delete old LLM results first (due to foreign key constraint)
                cursor.execute('''
                    DELETE FROM llm_results 
                    WHERE item_guid IN (
                        SELECT guid FROM rss_items 
                        WHERE datetime(published) < datetime('now', '-{} days')
                    )
                '''.format(days_old))
                
                # Delete old RSS items
                cursor.execute('''
                    DELETE FROM rss_items 
                    WHERE datetime(published) < datetime('now', '-{} days')
                '''.format(days_old))
                
                deleted_count = cursor.rowcount
                conn.commit()
                
                print(f"Cleaned up {deleted_count} old items")
                
            except sqlite3.Error as e:
                print(f"Error during cleanup: {e}")
    
    def get_database_info(self) -> Dict[str, Any]:
        """
        Get general database information
        
        Returns:
            Dictionary with database statistics
        """
        with sqlite3.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES) as conn:
            cursor = conn.cursor()
            
            # Get table row counts
            cursor.execute("SELECT COUNT(*) FROM rss_items")
            rss_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM llm_results")
            llm_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM sources")
            sources_count = cursor.fetchone()[0]
            
            # Get database size
            db_size = Path(self.db_path).stat().st_size if Path(self.db_path).exists() else 0
            
            return {
                'rss_items_count': rss_count,
                'llm_results_count': llm_count,
                'sources_count': sources_count,
                'database_size_bytes': db_size,
                'database_size_mb': round(db_size / (1024 * 1024), 2)
            } 