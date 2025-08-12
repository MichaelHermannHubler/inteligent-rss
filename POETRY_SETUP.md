# Poetry Setup Guide for Intelligent RSS Consumer

This guide explains how to set up and use the Intelligent RSS Consumer project using Poetry for dependency management.

## What is Poetry?

[Poetry](https://python-poetry.org/) is a modern dependency management and packaging tool for Python. It offers several advantages:

- **Dependency Resolution**: Automatically resolves and installs compatible package versions
- **Virtual Environment Management**: Creates and manages isolated Python environments
- **Lock File**: Ensures reproducible builds across different environments
- **Build System**: Simplifies packaging and distribution
- **Modern Standards**: Uses `pyproject.toml` instead of `setup.py`

## Prerequisites

- Python 3.8 or higher
- Basic command line knowledge

## Installation Options

### Option 1: Automatic Installation Script

The easiest way to get started:

```bash
# Make the script executable
chmod +x install_poetry.sh

# Run the installation script
./install_poetry.sh
```

This script will:
1. Check if Python 3.8+ is available
2. Install Poetry if not already installed
3. Configure Poetry to create virtual environments in the project directory
4. Install all dependencies

### Option 2: Manual Installation

#### Step 1: Install Poetry

```bash
# Install Poetry using the official installer
curl -sSL https://install.python-poetry.org | python3 -

# Add Poetry to your PATH (you may need to restart your shell)
export PATH="$HOME/.local/bin:$PATH"

# Verify installation
poetry --version
```

#### Step 2: Configure Poetry

```bash
# Configure Poetry to create virtual environments in the project directory
poetry config virtualenvs.in-project true

# This creates a `.venv/` folder in your project directory instead of a global location
```

#### Step 3: Install Dependencies

```bash
# Install all dependencies (including development tools)
poetry install

# Or install only production dependencies
poetry install --only main
```

## Project Structure with Poetry

After installation, your project will have this structure:

```
inteligent-rss/
├── .venv/                  # Poetry virtual environment
├── src/                    # Source code
├── examples/               # Example scripts
├── pyproject.toml          # Poetry configuration
├── poetry.lock            # Locked dependency versions
├── Makefile               # Common commands
├── install_poetry.sh      # Installation script
└── README.md              # Project documentation
```

## Using Poetry

### Basic Commands

```bash
# Activate the Poetry shell (creates/activates virtual environment)
poetry shell

# Run commands directly without activating shell
poetry run python3 main.py --help

# Install new dependencies
poetry add package_name

# Install development dependencies
poetry add --group dev package_name

# Remove dependencies
poetry remove package_name

# Update dependencies
poetry update

# Show dependency tree
poetry show --tree
```

### Using the Makefile

The project includes a comprehensive Makefile for common tasks:

```bash
# Show all available commands
make help

# Initial setup
make setup

# Activate Poetry shell
make shell

# Install development dependencies
make install-dev

# Run tests
make test

# Format code
make format

# Lint code
make lint

# Development workflow (format, lint, test)
make dev

# Clean up
make clean
```

## RSS Consumer Commands

### Basic Usage

```bash
# Activate Poetry shell
poetry shell

# Run RSS consumer
python3 main.py --model models/your-model.gguf --query "artificial intelligence"

# Run in scheduled mode
python3 main.py --model models/your-model.gguf --query "machine learning" --scheduled
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

## Development Workflow

### 1. Setup Development Environment

```bash
# Install all dependencies including development tools
poetry install --with dev

# Or use Makefile
make install-dev
```

### 2. Code Quality Tools

The project includes several code quality tools configured in `pyproject.toml`:

- **Black**: Code formatting
- **Flake8**: Linting
- **MyPy**: Type checking
- **Pytest**: Testing

```bash
# Format code
poetry run black src/

# Lint code
poetry run flake8 src/

# Type checking
poetry run mypy src/

# Run tests
poetry run pytest

# Or use Makefile shortcuts
make format
make lint
make test
make dev  # Runs all three
```

### 3. Adding New Dependencies

```bash
# Add production dependency
poetry add requests

# Add development dependency
poetry add --group dev pytest

# Add with specific version
poetry add "requests>=2.25.0"

# Add with version constraints
poetry add "requests^2.25.0"
```

## Troubleshooting

### Common Issues

#### Poetry Not Found

```bash
# Add Poetry to PATH
export PATH="$HOME/.local/bin:$PATH"

# Or restart your shell
source ~/.bashrc  # or ~/.zshrc
```

#### Virtual Environment Issues

```bash
# Remove existing virtual environment
rm -rf .venv/

# Recreate virtual environment
poetry install
```

#### Dependency Installation Failures

Some packages like `llama-cpp-python` require system dependencies:

```bash
# Ubuntu/Debian
sudo apt install build-essential cmake

# CentOS/RHEL
sudo yum install gcc gcc-c++ make cmake

# Arch Linux
sudo pacman -S base-devel cmake
```

#### Permission Issues

```bash
# Check Poetry configuration
poetry config --list

# Reset Poetry configuration
poetry config --unset virtualenvs.in-project
poetry config virtualenvs.in-project true
```

### Getting Help

```bash
# Poetry help
poetry --help
poetry install --help

# Show Poetry configuration
poetry config --list

# Show dependency information
poetry show
poetry show --tree
poetry show --outdated
```

## Migration from pip/requirements.txt

If you're coming from a pip-based setup:

1. **Remove old virtual environment**:
   ```bash
   rm -rf venv/
   ```

2. **Install Poetry** (see installation steps above)

3. **Install dependencies**:
   ```bash
   poetry install
   ```

4. **Update your workflow**:
   - Use `poetry shell` instead of `source venv/bin/activate`
   - Use `poetry run` for one-off commands
   - Use `poetry add` instead of `pip install`

## Benefits of Poetry

- **Reproducible Builds**: `poetry.lock` ensures exact same versions across environments
- **Dependency Resolution**: Automatically handles complex dependency conflicts
- **Modern Standards**: Uses `pyproject.toml` (PEP 518)
- **Virtual Environment Management**: No need to manually create/manage venvs
- **Build System**: Easy packaging and distribution
- **Development Tools**: Integrated testing, formatting, and linting

## Next Steps

1. **Download an LLM Model**: You'll need a local LLM model file to process RSS content
2. **Configure RSS Sources**: Add or modify RSS sources in the `src/sources/` directory
3. **Run the System**: Start consuming RSS feeds with your LLM model
4. **Customize**: Add custom processing logic or new RSS sources

For more information, see the main [README.md](README.md) file. 