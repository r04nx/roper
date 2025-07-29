#!/bin/bash

# Roper MCQ Solver Launcher
# This script properly activates the virtual environment and starts roper

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
cd "$SCRIPT_DIR"

# Check if virtual environment exists
if [ ! -d "overlay_env" ]; then
    echo "❌ Virtual environment not found. Please run setup first."
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found. Please create it with your GEMINI_API_KEY."
    exit 1
fi

# Activate virtual environment and run roper
source overlay_env/bin/activate

echo "🚀 Starting Roper MCQ Solver..."
echo "📝 Press Ctrl+Alt+2 to analyze screen MCQs"
echo "🛑 Press Escape to quit"

python roper.py
