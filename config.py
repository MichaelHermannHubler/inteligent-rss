"""
Configuration file for the Intelligent RSS Consumer

This file contains all the configurable settings for the RSS consumer system.
Modify these values to customize the behavior without changing the main code.
"""

import os
from pathlib import Path

# LLM Configuration
LLM_CONFIG = {
    'default_model_path': os.getenv('LLM_MODEL_PATH', 'models/llama-2-7b-chat.gguf'),
    'max_tokens': 512,
    'temperature': 0.1,
    'context_length': 2048,
    'threads': 4,
    'verbose': False
}

# Database Configuration
DATABASE_CONFIG = {
    'default_path': 'rss_data.db',
    'backup_enabled': True,
    'backup_interval_days': 7,
    'max_backups': 5,
    'cleanup_enabled': True,
    'cleanup_days_old': 30
}

# RSS Sources Configuration
RSS_SOURCES = {
    # Generic RSS feeds
    'generic_feeds': [
        {
            'name': 'Hacker News',
            'url': 'https://news.ycombinator.com/rss',
            'enabled': True,
            'timeout': 30
        },
        {
            'name': 'Ars Technica',
            'url': 'https://feeds.arstechnica.com/arstechnica/index',
            'enabled': True,
            'timeout': 30
        },
        {
            'name': 'The Verge',
            'url': 'https://www.theverge.com/rss/index.xml',
            'enabled': True,
            'timeout': 30
        },
        {
            'name': 'TechCrunch',
            'url': 'https://techcrunch.com/feed/',
            'enabled': True,
            'timeout': 30
        }
    ],
    
    # Reddit feeds
    'reddit_feeds': [
        {
            'subreddit': 'python',
            'enabled': True
        },
        {
            'subreddit': 'programming',
            'enabled': True
        },
        {
            'subreddit': 'technology',
            'enabled': True
        },
        {
            'subreddit': 'artificial',
            'enabled': True
        },
        {
            'subreddit': 'MachineLearning',
            'enabled': True
        }
    ],
    
    # Custom feeds (add your own here)
    'custom_feeds': [
        # Example custom feed
        # {
        #     'name': 'My Tech Blog',
        #     'url': 'https://mytechblog.com/feed/',
        #     'enabled': False,
        #     'timeout': 30,
        #     'custom_processing': True
        # }
    ]
}

# Processing Configuration
PROCESSING_CONFIG = {
    'default_query': 'artificial intelligence machine learning',
    'min_relevance_score': 50,
    'max_results_per_query': 100,
    'content_truncation_length': 1000,
    'delay_between_sources': 1,  # seconds
    'retry_attempts': 3,
    'retry_delay': 5  # seconds
}

# Scheduled Processing Configuration
SCHEDULED_CONFIG = {
    'default_interval_minutes': 60,
    'max_concurrent_runs': 1,
    'auto_cleanup': True,
    'cleanup_interval_hours': 24
}

# Logging Configuration
LOGGING_CONFIG = {
    'level': 'INFO',  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file_enabled': True,
    'log_file': 'rss_consumer.log',
    'max_log_size_mb': 10,
    'backup_count': 3
}

# HTTP Configuration
HTTP_CONFIG = {
    'user_agent': 'IntelligentRSSConsumer/1.0',
    'timeout': 30,
    'max_redirects': 5,
    'verify_ssl': True,
    'proxies': None,  # {'http': 'http://proxy:port', 'https': 'https://proxy:port'}
}

# Content Processing Configuration
CONTENT_CONFIG = {
    'remove_html_tags': True,
    'remove_extra_whitespace': True,
    'normalize_unicode': True,
    'max_content_length': 10000,
    'min_content_length': 50
}

# LLM Prompt Templates
PROMPT_TEMPLATES = {
    'default': """### Task: Analyze the following RSS content for relevance to the query: "{query}"

### Content:
Title: {title}
Description: {description}
Content: {content}

### Instructions:
1. Determine if this content is relevant to the query: "{query}"
2. Provide a relevance score from 0-100 (0 = not relevant, 100 = highly relevant)
3. Explain why it is or isn't relevant
4. Extract any key information related to the query
5. Provide a brief summary

### Response Format:
Relevance Score: [0-100]
Relevance: [Yes/No/Partially]
Explanation: [Brief explanation]
Key Information: [Extracted key points]
Summary: [Brief summary]

### Analysis:""",

    'technical': """### Task: Technical Analysis of RSS Content

### Query: {query}
### Content: {content}

### Instructions:
Analyze this technical content for relevance to "{query}".
Focus on technical accuracy, implementation details, and practical applications.

### Response Format:
Relevance Score: [0-100]
Technical Relevance: [Yes/No/Partially]
Technical Details: [Key technical information]
Implementation Notes: [Practical implementation details]
Summary: [Technical summary]

### Analysis:""",

    'news': """### Task: News Relevance Analysis

### Query: {query}
### Content: {content}

### Instructions:
Analyze this news content for relevance to "{query}".
Consider timeliness, impact, and newsworthiness.

### Response Format:
Relevance Score: [0-100]
News Relevance: [Yes/No/Partially]
Impact Level: [High/Medium/Low]
Key Facts: [Important facts and figures]
Summary: [News summary]

### Analysis:"""
}

# Database Queries Configuration
DB_QUERIES = {
    'get_relevant_items': """
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
    """,
    
    'get_source_stats': """
        SELECT 
            s.name, s.url, s.last_consumed, s.item_count, s.created_at,
            COUNT(l.id) as processed_count,
            AVG(l.relevance_score) as avg_relevance_score
        FROM sources s
        LEFT JOIN llm_results l ON s.name = l.item_source
        GROUP BY s.id, s.name, s.url, s.last_consumed, s.item_count, s.created_at
        ORDER BY s.name
    """
}

# Environment-specific overrides
def get_config():
    """Get configuration based on environment"""
    env = os.getenv('RSS_ENV', 'development').lower()
    
    if env == 'production':
        # Production overrides
        LOGGING_CONFIG['level'] = 'WARNING'
        PROCESSING_CONFIG['delay_between_sources'] = 2
        HTTP_CONFIG['timeout'] = 60
        
    elif env == 'testing':
        # Testing overrides
        DATABASE_CONFIG['default_path'] = 'test_rss_data.db'
        PROCESSING_CONFIG['delay_between_sources'] = 0
        SCHEDULED_CONFIG['default_interval_minutes'] = 1
    
    return {
        'llm': LLM_CONFIG,
        'database': DATABASE_CONFIG,
        'rss_sources': RSS_SOURCES,
        'processing': PROCESSING_CONFIG,
        'scheduled': SCHEDULED_CONFIG,
        'logging': LOGGING_CONFIG,
        'http': HTTP_CONFIG,
        'content': CONTENT_CONFIG,
        'prompt_templates': PROMPT_TEMPLATES,
        'db_queries': DB_QUERIES,
        'environment': env
    }

# Utility functions
def get_enabled_sources():
    """Get list of enabled RSS sources"""
    config = get_config()
    sources = []
    
    # Add generic feeds
    for feed in config['rss_sources']['generic_feeds']:
        if feed['enabled']:
            sources.append(feed)
    
    # Add Reddit feeds
    for feed in config['rss_sources']['reddit_feeds']:
        if feed['enabled']:
            sources.append(feed)
    
    # Add custom feeds
    for feed in config['rss_sources']['custom_feeds']:
        if feed['enabled']:
            sources.append(feed)
    
    return sources

def get_model_path():
    """Get the LLM model path, checking environment variables first"""
    config = get_config()
    model_path = os.getenv('LLM_MODEL_PATH', config['llm']['default_model_path'])
    
    # Expand user path if needed
    model_path = os.path.expanduser(model_path)
    
    return model_path

def get_database_path():
    """Get the database path"""
    config = get_config()
    db_path = os.getenv('RSS_DB_PATH', config['database']['default_path'])
    
    # Create directory if it doesn't exist
    db_dir = os.path.dirname(db_path)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir)
    
    return db_path 