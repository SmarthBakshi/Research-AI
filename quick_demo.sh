#!/bin/bash

# Quick Demo Script for ResearchAI Frontend
# Launches UI in demo mode with mock data

set -e

echo "🚀 ResearchAI - Quick Frontend Demo"
echo "===================================="
echo ""

# Check if we're in the right directory
if [ ! -f "docker/ui/test_ui_standalone.py" ]; then
    echo "❌ Error: Please run this script from the Research-AI root directory"
    exit 1
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed"
    exit 1
fi

# Check if Gradio is installed
if ! python3 -c "import gradio" 2>/dev/null; then
    echo "📦 Installing Gradio..."
    pip3 install gradio httpx
fi

echo "✅ Dependencies ready"
echo ""
echo "🎨 Launching UI in demo mode..."
echo "📍 URL: http://localhost:7860"
echo "⚠️  Using mock data (no backend required)"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Run the standalone UI
cd docker/ui
python3 test_ui_standalone.py
