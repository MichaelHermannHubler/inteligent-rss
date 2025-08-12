import time
from typing import List, Dict, Any
from .base_source import BaseSource, RSSItem
from .llm_processor import LLMProcessor
from .database import RSSDatabase


class RSSConsumer:
    """Main RSS consumer that orchestrates the entire process"""
    
    def __init__(self, model_path: str, query: str, db_path: str = "rss_data.db"):
        """
        Initialize the RSS consumer
        
        Args:
            model_path: Path to the local LLM model file
            query: The query to search for in content
            db_path: Path to the SQLite database
        """
        self.model_path = model_path
        self.query = query
        self.db = RSSDatabase(db_path)
        self.llm_processor = LLMProcessor(model_path, query)
        self.sources: List[BaseSource] = []
    
    def add_source(self, source: BaseSource):
        """
        Add a source to the consumer
        
        Args:
            source: RSS source to add
        """
        self.sources.append(source)
        print(f"Added source: {source}")
    
    def add_sources(self, sources: List[BaseSource]):
        """
        Add multiple sources to the consumer
        
        Args:
            sources: List of RSS sources to add
        """
        for source in sources:
            self.add_source(source)
    
    def consume_all_sources(self) -> Dict[str, Any]:
        """
        Consume all RSS sources and process with LLM
        
        Returns:
            Dictionary with processing statistics
        """
        if not self.sources:
            print("No sources configured")
            return {}
        
        total_items = 0
        total_processed = 0
        total_stored = 0
        source_stats = {}
        
        print(f"Starting to consume {len(self.sources)} sources...")
        print(f"Query: '{self.query}'")
        print("-" * 50)
        
        for source in self.sources:
            try:
                print(f"Processing source: {source.name}")
                
                # Consume RSS feed
                items = source.consume()
                if not items:
                    print(f"  No items found for {source.name}")
                    continue
                
                print(f"  Found {len(items)} items")
                total_items += len(items)
                
                # Store RSS items in database
                items_dict = [self._rss_item_to_dict(item) for item in items]
                stored_count = self.db.store_rss_items(items_dict)
                print(f"  Stored {stored_count} RSS items")
                
                # Process items with LLM
                if self.llm_processor.llm:
                    print(f"  Processing {len(items)} items with LLM...")
                    llm_results = self.llm_processor.process_items(items)
                    
                    if llm_results:
                        # Store LLM results
                        stored_llm_count = self.db.store_llm_results(llm_results)
                        print(f"  Stored {stored_llm_count} LLM results")
                        total_processed += len(llm_results)
                        total_stored += stored_llm_count
                    else:
                        print(f"  No LLM results generated for {source.name}")
                else:
                    print(f"  LLM not available, skipping processing for {source.name}")
                
                # Store source information
                source_info = source.get_source_info()
                source_info['item_count'] = len(items)
                self.db.store_source_info(source_info)
                
                # Collect statistics
                source_stats[source.name] = {
                    'items_found': len(items),
                    'items_stored': stored_count,
                    'llm_processed': len(llm_results) if 'llm_results' in locals() else 0,
                    'llm_stored': stored_llm_count if 'stored_llm_count' in locals() else 0
                }
                
                print(f"  Completed {source.name}")
                print()
                
                # Small delay to be respectful to RSS servers
                time.sleep(1)
                
            except Exception as e:
                print(f"Error processing source {source.name}: {e}")
                source_stats[source.name] = {'error': str(e)}
                continue
        
        # Print summary
        print("=" * 50)
        print("PROCESSING SUMMARY")
        print("=" * 50)
        print(f"Total sources: {len(self.sources)}")
        print(f"Total RSS items found: {total_items}")
        print(f"Total items processed with LLM: {total_processed}")
        print(f"Total LLM results stored: {total_stored}")
        print()
        
        # Print source-specific statistics
        print("SOURCE STATISTICS:")
        for source_name, stats in source_stats.items():
            if 'error' in stats:
                print(f"  {source_name}: ERROR - {stats['error']}")
            else:
                print(f"  {source_name}: {stats['items_found']} items, "
                      f"{stats['llm_processed']} processed, {stats['llm_stored']} stored")
        
        return {
            'total_sources': len(self.sources),
            'total_items': total_items,
            'total_processed': total_processed,
            'total_stored': total_stored,
            'source_stats': source_stats
        }
    
    def _rss_item_to_dict(self, item: RSSItem) -> Dict[str, Any]:
        """Convert RSSItem to dictionary for database storage"""
        return {
            'guid': item.guid,
            'title': item.title,
            'link': item.link,
            'description': item.description,
            'content': item.content,
            'published': item.published,
            'source': item.source
        }
    
    def get_relevant_results(self, min_score: int = 50, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get items relevant to the query
        
        Args:
            min_score: Minimum relevance score (0-100)
            limit: Maximum number of results to return
            
        Returns:
            List of relevant items with their LLM analysis
        """
        return self.db.get_relevant_items(self.query, min_score, limit)
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get processing statistics
        
        Returns:
            Dictionary with various statistics
        """
        db_info = self.db.get_database_info()
        source_stats = self.db.get_source_stats()
        query_stats = self.db.get_query_stats()
        
        return {
            'database': db_info,
            'sources': source_stats,
            'queries': query_stats,
            'current_query': self.query,
            'sources_configured': len(self.sources)
        }
    
    def cleanup_old_data(self, days_old: int = 30):
        """
        Clean up old data from the database
        
        Args:
            days_old: Remove items older than this many days
        """
        print(f"Cleaning up data older than {days_old} days...")
        self.db.cleanup_old_items(days_old)
    
    def run_scheduled_consumption(self, interval_minutes: int = 60, max_runs: int = None):
        """
        Run continuous RSS consumption at specified intervals
        
        Args:
            interval_minutes: Minutes between consumption runs
            max_runs: Maximum number of runs (None for infinite)
        """
        print(f"Starting scheduled consumption every {interval_minutes} minutes...")
        print("Press Ctrl+C to stop")
        
        run_count = 0
        
        try:
            while max_runs is None or run_count < max_runs:
                print(f"\n--- Run {run_count + 1} ---")
                print(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
                
                # Consume all sources
                stats = self.consume_all_sources()
                
                # Print summary
                if stats:
                    print(f"Run completed: {stats['total_items']} items processed")
                
                run_count += 1
                
                if max_runs and run_count >= max_runs:
                    print(f"Completed {max_runs} runs")
                    break
                
                # Wait for next run
                if max_runs is None or run_count < max_runs:
                    print(f"Waiting {interval_minutes} minutes until next run...")
                    time.sleep(interval_minutes * 60)
                
        except KeyboardInterrupt:
            print("\nScheduled consumption stopped by user")
        except Exception as e:
            print(f"Error in scheduled consumption: {e}") 