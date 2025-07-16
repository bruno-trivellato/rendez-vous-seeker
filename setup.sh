#!/bin/bash

set -e

echo "🛠️  Setting up Rendez-vous Monitor environment..."
echo "================================================"

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    echo "   Visit: https://www.python.org/downloads/"
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip first."
    exit 1
fi

echo "✅ pip3 found: $(pip3 --version)"

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install setuptools first (needed for Python 3.13 compatibility)
echo "🔧 Installing setuptools for Python 3.13 compatibility..."
pip install setuptools

# Install requirements
echo "📚 Installing Python dependencies..."
pip install -r requirements.txt

echo ""
echo "🎉 Setup completed successfully!"
echo "=================================="
echo "To start the monitor, run:"
echo "  source .venv/bin/activate"
echo "  python main.py"
echo ""
echo "Or simply run:"
echo "  ./start_monitor.sh"
echo "" 