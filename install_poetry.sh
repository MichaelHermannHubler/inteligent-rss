#!/bin/bash

# Installation script for Intelligent RSS Consumer using Poetry

echo "Installing Intelligent RSS Consumer using Poetry..."
echo "=================================================="

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.8+ first"
    exit 1
fi

# Check Python version
python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "Found Python version: $python_version"

# Check if Poetry is installed
if ! command -v poetry &> /dev/null; then
    echo "Poetry is not installed. Installing Poetry..."
    
    # Install Poetry using the official installer
    curl -sSL https://install.python-poetry.org | python3 -
    
    # Add Poetry to PATH (you may need to restart your shell or source your profile)
    export PATH="$HOME/.local/bin:$PATH"
    
    if ! command -v poetry &> /dev/null; then
        echo "Error: Poetry installation failed or not in PATH"
        echo "Please install Poetry manually: https://python-poetry.org/docs/#installation"
        echo "Or add $HOME/.local/bin to your PATH"
        exit 1
    fi
    
    echo "Poetry installed successfully!"
else
    echo "Poetry is already installed: $(poetry --version)"
fi

# Configure Poetry to create virtual environment in project directory
echo "Configuring Poetry..."
poetry config virtualenvs.in-project true

# Install dependencies
echo "Installing dependencies with Poetry..."
poetry install

if [ $? -ne 0 ]; then
    echo "Error: Failed to install dependencies"
    echo "You may need to install system dependencies for llama-cpp-python:"
    echo "  Ubuntu/Debian: sudo apt install build-essential cmake"
    echo "  CentOS/RHEL: sudo yum install gcc gcc-c++ make cmake"
    echo "  Arch: sudo pacman -S base-devel cmake"
    exit 1
fi

echo ""
echo "=================================================="
echo "Installation completed successfully!"
echo ""
echo "To use the RSS Consumer:"
echo "1. Activate the Poetry shell:"
echo "   poetry shell"
echo ""
echo "2. Or run commands directly with Poetry:"
echo "   poetry run python3 test_system.py"
echo "   poetry run python3 main.py --help"
echo "   poetry run rss-consumer --help"
echo ""
echo "3. Exit Poetry shell when done:"
echo "   exit"
echo ""
echo "Development commands:"
echo "  poetry run pytest          # Run tests"
echo "  poetry run black .         # Format code"
echo "  poetry run flake8          # Lint code"
echo "  poetry run mypy src        # Type checking"
echo ""
echo "Note: You'll still need to download a local LLM model file."
echo "You can find models at: https://huggingface.co/models?pipeline_tag=text-generation"
echo ""
echo "Example model download:"
echo "  mkdir -p models"
echo "  # Download a model file to the models/ directory"
echo "  # Then set: export LLM_MODEL_PATH=models/your-model.gguf" 