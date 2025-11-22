#!/bin/bash
# Ollama Oracle Interface Launcher
# Handles CORS issues automatically

echo "🔮 Ollama Oracle Interface Launcher"
echo "===================================="

# Check if Ollama is running
if curl -s http://localhost:11434 > /dev/null 2>&1; then
    echo "✓ Ollama is running"
else
    echo "⚠ Ollama doesn't appear to be running"
    echo "  Starting Ollama..."
    ollama serve &
    sleep 2
fi

# Check if requests module is installed
if ! python3 -c "import requests" 2>/dev/null; then
    echo "📦 Installing requests module..."
    pip install --user requests
fi

# Find the directory containing our files
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo ""
echo "🌐 Starting web server..."
echo "📁 Serving from: $SCRIPT_DIR"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔗 Open in browser:"
echo "   http://localhost:8888/hexchat_gui.html"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Press Ctrl+C to stop"
echo ""

cd "$SCRIPT_DIR"
python3 hexchat_server.py