#!/bin/bash

set -e

echo "🎯 Starting Rendez-vous Monitor..."
echo "=================================="

# If virtual environment doesn't exist, run setup
if [ ! -d ".venv" ]; then
    echo "🛠️  Virtual environment not found. Running setup.sh..."
    ./setup.sh
fi

# Activate virtual environment
source .venv/bin/activate

echo "🐍 Virtual environment activated"

echo "🚀 Starting monitor..."
python main.py

# When exiting the monitor, deactivate virtual environment
deactivate 