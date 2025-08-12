#!/bin/bash

# Installation script for Intelligent RSS Consumer in virtual environment

echo "Installing Intelligent RSS Consumer in virtual environment..."
echo "=========================================================="

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.8+ first"
    exit 1
fi

# Check Python version
python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "Found Python version: $python_version"

# Check if venv module is available
if ! python3 -c "import venv" &> /dev/null; then
    echo "Error: Python venv module not available"
    echo "Please install python3-venv package:"
    echo "  Ubuntu/Debian: sudo apt install python3-venv"
    echo "  CentOS/RHEL: sudo yum install python3-venv"
    echo "  Arch: sudo pacman -S python-venv"
    exit 1
fi

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

if [ $? -ne 0 ]; then
    echo "Error: Failed to create virtual environment"
    exit 1
fi

echo "Virtual environment created successfully!"

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

if [ $? -ne 0 ]; then
    echo "Error: Failed to activate virtual environment"
    exit 1
fi

echo "Virtual environment activated!"

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "Error: Failed to install dependencies"
    echo "You may need to install system dependencies for llama-cpp-python:"
    echo "  Ubuntu/Debian: sudo apt install build-essential cmake"
    echo "  CentOS/RHEL: sudo yum install gcc gcc-c++ make cmake"
    echo "  Arch: sudo pacman -S base-devel cmake"
    exit 1
fi

echo ""
echo "=========================================================="
echo "Installation completed successfully!"
echo ""
echo "To use the RSS Consumer:"
echo "1. Activate the virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "2. Test the system:"
echo "   python3 test_system.py"
echo ""
echo "3. Run the RSS consumer:"
echo "   python3 main.py --help"
echo ""
echo "4. Deactivate when done:"
echo "   deactivate"
echo ""
echo "Note: You'll still need to download a local LLM model file."
echo "You can find models at: https://huggingface.co/models?pipeline_tag=text-generation"
echo ""
echo "Example model download:"
echo "  mkdir -p models"
echo "  # Download a model file to the models/ directory"
echo "  # Then set: export LLM_MODEL_PATH=models/your-model.gguf" 