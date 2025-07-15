#!/bin/bash

set -e

echo "🚀 Setting up Rendez-vous Monitor..."
echo "====================================="

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3 first."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "🛠️  Creating Python virtual environment (.venv)..."
    python3 -m venv .venv
fi

echo "✅ Virtual environment ready"

# Activate virtual environment
source .venv/bin/activate

echo "🐍 Virtual environment activated"

# Update pip
pip install --upgrade pip

# Install dependencies
echo "📦 Installing dependencies in virtual environment..."
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully!"
else
    echo "❌ Error installing dependencies"
    deactivate
    exit 1
fi

# Make scripts executable
chmod +x main.py

echo ""
echo "🎉 Setup completed!"
echo ""
echo "To activate the virtual environment later:"
echo "  source .venv/bin/activate"
echo ""
echo "To run the monitor:"
echo "  python main.py"
echo ""
echo "To stop the monitor:"
echo "  Press Ctrl+C"
echo ""
echo "To exit the virtual environment:"
echo "  deactivate"
echo "" 