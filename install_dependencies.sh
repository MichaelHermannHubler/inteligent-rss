#!/bin/bash

# Installation script for Intelligent RSS Consumer dependencies

echo "Installing dependencies for Intelligent RSS Consumer..."
echo "=================================================="

# Check if we're on a Debian/Ubuntu system
if command -v apt-get &> /dev/null; then
    echo "Detected Debian/Ubuntu system"
    
    # Update package list
    echo "Updating package list..."
    sudo apt-get update
    
    # Install Python and pip
    echo "Installing Python and pip..."
    sudo apt-get install -y python3 python3-pip python3-venv
    
    # Install system dependencies for llama-cpp-python
    echo "Installing system dependencies for LLM..."
    sudo apt-get install -y build-essential cmake
    
elif command -v yum &> /dev/null; then
    echo "Detected Red Hat/CentOS system"
    
    # Install Python and pip
    echo "Installing Python and pip..."
    sudo yum install -y python3 python3-pip gcc gcc-c++ make cmake
    
elif command -v pacman &> /dev/null; then
    echo "Detected Arch Linux system"
    
    # Install Python and pip
    echo "Installing Python and pip..."
    sudo pacman -S --noconfirm python python-pip base-devel cmake
    
else
    echo "Unsupported package manager. Please install Python 3.8+ and pip manually."
    exit 1
fi

# Create virtual environment
echo "Creating Python virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

echo ""
echo "=================================================="
echo "Installation completed!"
echo ""
echo "To activate the virtual environment, run:"
echo "  source venv/bin/activate"
echo ""
echo "To test the system, run:"
echo "  source venv/bin/activate"
echo "  python3 test_system.py"
echo ""
echo "To run the RSS consumer, run:"
echo "  source venv/bin/activate"
echo "  python3 main.py --help"
echo ""
echo "Note: You'll still need to download a local LLM model file."
echo "You can find models at: https://huggingface.co/models?pipeline_tag=text-generation" 