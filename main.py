#!/usr/bin/env python3
"""
Intelligent RSS Feed Consumer

This program consumes RSS feeds from specified sources, processes content with a local LLM
to find relevant information based on a query, and stores results in a SQLite database.

Usage:
    python main.py [--query QUERY] [--model MODEL_PATH] [--scheduled] [--interval MINUTES]
"""

import argparse
import os
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from rss_consumer import RSSConsumer
from sources.generic_rss import GenericRSSSource
from sources.tech_crunch import TechCrunchSource
from sources.reddit import RedditSource


def create_example_sources():
    """Create example RSS sources"""
    sources = [
        # Generic RSS sources
        GenericRSSSource("Hacker News", "https://news.ycombinator.com/rss"),
        GenericRSSSource("Ars Technica", "https://feeds.arstechnica.com/arstechnica/index"),
        GenericRSSSource("The Verge", "https://www.theverge.com/rss/index.xml"),
        
        # Specialized sources
        TechCrunchSource(),
        
        # Reddit sources
        RedditSource("python"),
        RedditSource("programming"),
        RedditSource("technology"),
    ]
    return sources


def main():
    parser = argparse.ArgumentParser(
        description="Intelligent RSS Feed Consumer with Local LLM Processing"
    )
    parser.add_argument(
        "--query", 
        default="artificial intelligence machine learning",
        help="Search query for content relevance (default: 'artificial intelligence machine learning')"
    )
    parser.add_argument(
        "--model", 
        required=True,
        help="Path to local LLM model file (required)"
    )
    parser.add_argument(
        "--db", 
        default="rss_data.db",
        help="SQLite database path (default: rss_data.db)"
    )
    parser.add_argument(
        "--scheduled", 
        action="store_true",
        help="Run in scheduled mode (continuous consumption)"
    )
    parser.add_argument(
        "--interval", 
        type=int, 
        default=60,
        help="Interval between consumption runs in minutes (default: 60)"
    )
    parser.add_argument(
        "--max-runs", 
        type=int,
        help="Maximum number of runs in scheduled mode (default: infinite)"
    )
    parser.add_argument(
        "--cleanup", 
        type=int, 
        default=30,
        help="Clean up items older than N days (default: 30)"
    )
    parser.add_argument(
        "--stats", 
        action="store_true",
        help="Show database statistics and exit"
    )
    parser.add_argument(
        "--results", 
        action="store_true",
        help="Show relevant results and exit"
    )
    parser.add_argument(
        "--min-score", 
        type=int, 
        default=50,
        help="Minimum relevance score for results (default: 50)"
    )
    
    args = parser.parse_args()
    
    # Check if model file exists
    if not os.path.exists(args.model):
        print(f"Error: Model file not found: {args.model}")
        print("Please provide a valid path to a local LLM model file.")
        print("You can download models from Hugging Face or other sources.")
        sys.exit(1)
    
    # Initialize RSS consumer
    print("Initializing Intelligent RSS Consumer...")
    consumer = RSSConsumer(
        model_path=args.model,
        query=args.query,
        db_path=args.db
    )
    
    # Add sources
    print("Adding RSS sources...")
    sources = create_example_sources()
    consumer.add_sources(sources)
    
    # Handle different modes
    if args.stats:
        print("\n" + "="*50)
        print("DATABASE STATISTICS")
        print("="*50)
        stats = consumer.get_statistics()
        
        print(f"Current Query: {stats['current_query']}")
        print(f"Sources Configured: {stats['sources_configured']}")
        print()
        
        print("Database Info:")
        db_info = stats['database']
        print(f"  RSS Items: {db_info['rss_items_count']}")
        print(f"  LLM Results: {db_info['llm_results_count']}")
        print(f"  Sources: {db_info['sources_count']}")
        print(f"  Database Size: {db_info['database_size_mb']} MB")
        print()
        
        print("Source Statistics:")
        for source in stats['sources']:
            print(f"  {source['name']}: {source['item_count']} items, "
                  f"{source.get('processed_count', 0)} processed")
        
        print("\nQuery Statistics:")
        for query in stats['queries']:
            print(f"  '{query['query']}': {query['total_items']} items, "
                  f"avg score: {query['avg_relevance_score']:.1f}")
        
        return
    
    if args.results:
        print(f"\nRelevant results for query: '{args.query}' (min score: {args.min_score})")
        print("="*70)
        
        results = consumer.get_relevant_results(min_score=args.min_score, limit=20)
        
        if not results:
            print("No relevant results found.")
            return
        
        for i, result in enumerate(results, 1):
            print(f"\n{i}. {result['item_title']}")
            print(f"   Source: {result['item_source']}")
            print(f"   Score: {result['relevance_score']}/100")
            print(f"   Relevance: {result['relevance']}")
            print(f"   Summary: {result['summary'][:200]}{'...' if len(result['summary']) > 200 else ''}")
            print(f"   Link: {result['link']}")
            print("-" * 70)
        
        return
    
    # Clean up old data if requested
    if args.cleanup > 0:
        consumer.cleanup_old_data(args.cleanup)
    
    # Run consumption
    if args.scheduled:
        print(f"Starting scheduled consumption every {args.interval} minutes...")
        consumer.run_scheduled_consumption(
            interval_minutes=args.interval,
            max_runs=args.max_runs
        )
    else:
        print("Running single consumption cycle...")
        stats = consumer.consume_all_sources()
        
        if stats:
            print(f"\nConsumption completed successfully!")
            print(f"Total items processed: {stats['total_items']}")
            print(f"Total LLM results: {stats['total_stored']}")
        else:
            print("Consumption completed with errors.")


if __name__ == "__main__":
    main() 