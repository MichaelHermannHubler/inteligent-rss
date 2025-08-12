# Intelligent RSS Feed Consumer

A Python program that consumes RSS feeds from specified sources, processes content with a locally running LLM to find relevant information based on queries, and stores results in a SQLite database.

## Features

- **Modular RSS Sources**: Each RSS source is implemented as a separate Python file inheriting from a base interface
- **Local LLM Processing**: Uses locally running LLM models (via llama-cpp-python) for content analysis
- **SQLite Storage**: Stores RSS items and LLM processing results in a structured database
- **Flexible Querying**: Search for content relevant to specific queries with relevance scoring
- **Scheduled Processing**: Run continuous RSS consumption at specified intervals
- **Extensible Architecture**: Easy to add new RSS sources and customize processing logic

## Architecture

```
src/
├── base_source.py          # Base interface for all RSS sources
├── sources/                # Directory containing RSS source implementations
│   ├── generic_rss.py     # Generic RSS source for most feeds
│   ├── tech_crunch.py     # TechCrunch-specific source
│   ├── reddit.py          # Reddit RSS source
│   └── custom_source_example.py  # Example custom source
├── llm_processor.py        # LLM processing logic
├── database.py             # SQLite database operations
└── rss_consumer.py         # Main orchestrator class
```

## Installation

### Option 1: Using Poetry (Recommended)

Poetry is a modern dependency management and packaging tool for Python.

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd inteligent-rss
   ```

2. **Install Poetry** (if not already installed):
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

3. **Install dependencies**:
   ```bash
   poetry install
   ```

4. **Activate the virtual environment**:
   ```bash
   poetry shell
   ```

5. **Alternative: Run commands directly**:
   ```bash
   poetry run python3 main.py --help
   ```

### Option 2: Using pip and virtual environment

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd inteligent-rss
   ```

2. **Create virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

### Option 3: Using the installation script

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd inteligent-rss
   ```

2. **Run the installation script**:
   ```bash
   # For Poetry (recommended)
   chmod +x install_poetry.sh
   ./install_poetry.sh
   
   # For pip/venv
   chmod +x install_venv.sh
   ./install_venv.sh
   ```

## Quick Start with Poetry

After installation, you can use the Makefile for common commands:

```bash
# Show all available commands
make help

# Initial setup
make setup

# Activate Poetry shell
make shell

# Test the system
make test-system

# Run RSS consumer
make rss-help

# Development workflow
make dev
```

## Downloading LLM Models

You'll need to download a local LLM model file. You can find models on:
- [Hugging Face](https://huggingface.co/models?pipeline_tag=text-generation)
- [TheBloke's models](https://huggingface.co/TheBloke) (GGUF format)

Example models:
- `llama-2-7b-chat.gguf` (smaller, faster)
- `llama-2-13b-chat.gguf` (larger, better quality)
- `mistral-7b-instruct-v0.2.gguf` (good balance)

```bash
# Create models directory
mkdir -p models

# Download a model (example)
cd models
wget https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGUF/resolve/main/llama-2-7b-chat.Q4_K_M.gguf

# Set environment variable
export LLM_MODEL_PATH=models/llama-2-7b-chat.Q4_K_M.gguf
```

## Usage

### Basic Usage

```bash
# Activate Poetry shell
poetry shell

# Run a single consumption cycle
python3 main.py --model /path/to/your/model.gguf --query "artificial intelligence"

# Run in scheduled mode (every 60 minutes)
python3 main.py --model /path/to/your/model.gguf --query "machine learning" --scheduled

# Run scheduled with custom interval (every 30 minutes)
python3 main.py --model /path/to/your/model.gguf --query "python programming" --scheduled --interval 30
```

### Using Makefile Commands

```bash
# Run RSS consumption
make rss-run QUERY="artificial intelligence" MODEL="models/llama-2-7b.gguf"

# Run scheduled consumption
make rss-scheduled QUERY="machine learning" MODEL="models/llama-2-7b.gguf" INTERVAL=30

# Show database statistics
make rss-stats

# Show relevant results
make rss-results
```

### Command Line Options

- `--model`: Path to local LLM model file (required)
- `--query`: Search query for content relevance (default: "artificial intelligence machine learning")
- `--db`: SQLite database path (default: "rss_data.db")
- `--scheduled`: Run in scheduled mode (continuous consumption)
- `--interval`: Interval between consumption runs in minutes (default: 60)
- `--max-runs`: Maximum number of runs in scheduled mode
- `--cleanup`: Clean up items older than N days (default: 30)
- `--stats`: Show database statistics and exit
- `--results`: Show relevant results and exit
- `--min-score`: Minimum relevance score for results (default: 50)

### Viewing Results

```bash
# Show database statistics
python3 main.py --model /path/to/your/model.gguf --stats

# Show relevant results for a query
python3 main.py --model /path/to/your/model.gguf --query "python" --results

# Show results with higher relevance threshold
python3 main.py --model /path/to/your/model.gguf --query "python" --results --min-score 70
```

## Development

### Poetry Commands

```bash
# Install development dependencies
poetry install --with dev

# Run tests
poetry run pytest

# Format code
poetry run black src/

# Lint code
poetry run flake8 src/

# Type checking
poetry run mypy src/

# Add new dependency
poetry add package_name

# Add development dependency
poetry add --group dev package_name
```

### Makefile Commands

```bash
# Development workflow (format, lint, test)
make dev

# Install development dependencies
make install-dev

# Run tests
make test

# Format code
make format

# Lint code
make lint

# Clean up
make clean
```

## Creating Custom RSS Sources

### 1. Inherit from BaseSource

Create a new Python file in the `src/sources/` directory:

```python
from ..base_source import BaseSource, RSSItem
from typing import List, Dict, Any

class MyCustomSource(BaseSource):
    def __init__(self, name: str, url: str):
        super().__init__(name, url)
    
    def consume(self) -> List[RSSItem]:
        # Implement your RSS consumption logic here
        # Return a list of RSSItem objects
        pass
    
    def get_source_info(self) -> Dict[str, Any]:
        # Return source metadata
        return {
            'name': self.name,
            'url': self.url,
            'custom_field': 'custom_value'
        }
```

### 2. Inherit from GenericRSSSource (Recommended)

For most cases, inherit from `GenericRSSSource` and add custom processing:

```python
from .generic_rss import GenericRSSSource
from typing import List, Dict, Any

class MyBlogSource(GenericRSSSource):
    def __init__(self, blog_name: str):
        url = f"https://{blog_name}.com/feed/"
        super().__init__(blog_name, url)
        self.blog_name = blog_name
    
    def consume(self) -> List[RSSItem]:
        # Get items from parent class
        items = super().consume()
        
        # Apply custom processing
        for item in items:
            item.content = self._clean_content(item.content)
            item.source = f"{self.blog_name} Blog"
        
        return items
    
    def _clean_content(self, content: str) -> str:
        # Add your custom content cleaning logic
        return content.replace('Read more...', '').strip()
```

### 3. Add to Main Script

Update `main.py` to include your custom source:

```python
from sources.my_custom_source import MyCustomSource

def create_example_sources():
    sources = [
        # ... existing sources ...
        MyCustomSource("My Blog", "https://myblog.com/feed/"),
    ]
    return sources
```

## Database Schema

The system creates three main tables:

### RSS Items Table
- `id`: Primary key
- `guid`: Unique identifier for the RSS item
- `title`: Item title
- `link`: Item URL
- `description`: Item description
- `content`: Full content text
- `published`: Publication date
- `source`: Source name
- `created_at`: When item was stored

### LLM Results Table
- `id`: Primary key
- `item_guid`: Reference to RSS item
- `query`: Search query used
- `relevance_score`: Relevance score (0-100)
- `relevance`: Relevance classification (Yes/No/Partially)
- `explanation`: LLM explanation of relevance
- `key_information`: Extracted key points
- `summary`: Brief summary
- `llm_response`: Full LLM response
- `processed_at`: When processing occurred

### Sources Table
- `id`: Primary key
- `name`: Source name
- `url`: RSS feed URL
- `last_consumed`: Last consumption timestamp
- `item_count`: Number of items from this source

## Example Workflow

1. **Setup**: Install dependencies using Poetry
2. **Configure**: Add RSS sources to the system
3. **Download Model**: Get a local LLM model file
4. **Run**: Execute the consumer with your query
5. **Monitor**: Check database statistics and results
6. **Customize**: Add custom sources or modify processing logic

## Performance Considerations

- **LLM Processing**: Processing speed depends on your model size and hardware
- **Database**: SQLite is suitable for moderate data volumes; consider PostgreSQL for large-scale deployments
- **Memory**: Large LLM models require significant RAM
- **Network**: RSS consumption depends on feed availability and network speed

## Troubleshooting

### Common Issues

1. **LLM Model Not Found**: Ensure the model path is correct and the file exists
2. **Import Errors**: Make sure you're running from the project root directory with Poetry
3. **Database Errors**: Check file permissions for the SQLite database
4. **RSS Parsing Issues**: Some feeds may have malformed XML; check the source feed

### Debug Mode

Add debug prints to your custom sources:

```python
def consume(self) -> List[RSSItem]:
    print(f"Debug: Consuming feed from {self.url}")
    items = super().consume()
    print(f"Debug: Found {len(items)} items")
    return items
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add your custom RSS source or improvements
4. Test thoroughly with `make dev`
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with [llama-cpp-python](https://github.com/abetlen/llama-cpp-python) for local LLM inference
- Uses [feedparser](https://feedparser.readthedocs.io/) for RSS parsing
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) for HTML processing
- [Poetry](https://python-poetry.org/) for dependency management and packaging
