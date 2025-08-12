#!/usr/bin/env python3
"""
Basic Usage Example for Intelligent RSS Consumer

This script demonstrates how to use the RSS consumer system with basic configuration.
"""

import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from rss_consumer import RSSConsumer
from sources.generic_rss import GenericRSSSource
from sources.tech_crunch import TechCrunchSource


def basic_example():
    """Basic example of RSS consumption"""
    
    # Configuration
    model_path = "models/llama-2-7b-chat.gguf"  # Update this path
    query = "artificial intelligence"
    db_path = "example_rss_data.db"
    
    # Check if model exists
    if not os.path.exists(model_path):
        print(f"Error: Model file not found: {model_path}")
        print("Please update the model_path variable with a valid path to your LLM model.")
        return
    
    print("=== Basic RSS Consumer Example ===")
    print(f"Query: {query}")
    print(f"Model: {model_path}")
    print(f"Database: {db_path}")
    print()
    
    # Initialize consumer
    consumer = RSSConsumer(
        model_path=model_path,
        query=query,
        db_path=db_path
    )
    
    # Add some RSS sources
    sources = [
        GenericRSSSource("Hacker News", "https://news.ycombinator.com/rss"),
        GenericRSSSource("Ars Technica", "https://feeds.arstechnica.com/arstechnica/index"),
        TechCrunchSource(),
    ]
    
    for source in sources:
        consumer.add_source(source)
        print(f"Added source: {source.name}")
    
    print(f"\nTotal sources: {len(consumer.sources)}")
    print()
    
    # Consume RSS feeds
    print("Starting RSS consumption...")
    stats = consumer.consume_all_sources()
    
    if stats:
        print("\n=== Consumption Results ===")
        print(f"Total items found: {stats['total_items']}")
        print(f"Total items processed with LLM: {stats['total_processed']}")
        print(f"Total LLM results stored: {stats['total_stored']}")
        
        # Show source statistics
        print("\nSource Statistics:")
        for source_name, source_stats in stats['source_stats'].items():
            if 'error' not in source_stats:
                print(f"  {source_name}: {source_stats['items_found']} items, "
                      f"{source_stats['llm_processed']} processed")
            else:
                print(f"  {source_name}: ERROR - {source_stats['error']}")
    else:
        print("No results from consumption")


def query_results_example():
    """Example of querying results from the database"""
    
    model_path = "models/llama-2-7b-chat.gguf"  # Update this path
    query = "artificial intelligence"
    db_path = "example_rss_data.db"
    
    if not os.path.exists(model_path):
        print(f"Error: Model file not found: {model_path}")
        return
    
    print("\n=== Query Results Example ===")
    
    # Initialize consumer
    consumer = RSSConsumer(
        model_path=model_path,
        query=query,
        db_path=db_path
    )
    
    # Get relevant results
    results = consumer.get_relevant_results(min_score=50, limit=10)
    
    if not results:
        print("No relevant results found in database.")
        print("Try running the basic example first to populate the database.")
        return
    
    print(f"Found {len(results)} relevant results for query: '{query}'")
    print()
    
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['item_title']}")
        print(f"   Source: {result['item_source']}")
        print(f"   Relevance Score: {result['relevance_score']}/100")
        print(f"   Relevance: {result['relevance']}")
        print(f"   Summary: {result['summary'][:150]}{'...' if len(result['summary']) > 150 else ''}")
        print(f"   Link: {result['link']}")
        print("-" * 60)


def statistics_example():
    """Example of viewing database statistics"""
    
    model_path = "models/llama-2-7b-chat.gguf"  # Update this path
    query = "artificial intelligence"
    db_path = "example_rss_data.db"
    
    if not os.path.exists(model_path):
        print(f"Error: Model file not found: {model_path}")
        return
    
    print("\n=== Database Statistics Example ===")
    
    # Initialize consumer
    consumer = RSSConsumer(
        model_path=model_path,
        query=query,
        db_path=db_path
    )
    
    # Get statistics
    stats = consumer.get_statistics()
    
    print(f"Current Query: {stats['current_query']}")
    print(f"Sources Configured: {stats['sources_configured']}")
    print()
    
    # Database info
    db_info = stats['database']
    print("Database Information:")
    print(f"  RSS Items: {db_info['rss_items_count']}")
    print(f"  LLM Results: {db_info['llm_results_count']}")
    print(f"  Sources: {db_info['sources_count']}")
    print(f"  Database Size: {db_info['database_size_mb']} MB")
    print()
    
    # Source statistics
    if stats['sources']:
        print("Source Statistics:")
        for source in stats['sources']:
            print(f"  {source['name']}: {source['item_count']} items, "
                  f"{source.get('processed_count', 0)} processed")
        print()
    
    # Query statistics
    if stats['queries']:
        print("Query Statistics:")
        for query_stat in stats['queries']:
            print(f"  '{query_stat['query']}': {query_stat['total_items']} items, "
                  f"avg score: {query_stat['avg_relevance_score']:.1f}")


def main():
    """Main function to run examples"""
    
    print("Intelligent RSS Consumer - Basic Usage Examples")
    print("=" * 50)
    
    # Check if model path is provided
    model_path = os.getenv('LLM_MODEL_PATH', 'models/llama-2-7b-chat.gguf')
    
    if not os.path.exists(model_path):
        print(f"Warning: Model file not found at: {model_path}")
        print("Please set the LLM_MODEL_PATH environment variable or update the model_path in this script.")
        print("You can download models from Hugging Face or other sources.")
        print()
        print("Example:")
        print("  export LLM_MODEL_PATH=/path/to/your/model.gguf")
        print("  python examples/basic_usage.py")
        print()
        return
    
    try:
        # Run examples
        basic_example()
        query_results_example()
        statistics_example()
        
        print("\n=== Examples Completed ===")
        print("Check the database file for stored data:")
        print(f"  Database: example_rss_data.db")
        print("\nYou can also run the main script for more options:")
        print("  python main.py --help")
        
    except Exception as e:
        print(f"Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 