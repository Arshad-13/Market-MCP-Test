#!/bin/bash
# Standalone Market Intelligence MCP Server Launcher
# Run this to start the server with full network access

echo ""
echo "========================================"
echo "Market Intelligence MCP Server"
echo "Standalone Mode (TCP)"
echo "========================================"
echo ""

# Change to script directory
cd "$(dirname "$0")"

# Activate virtual environment if it exists
if [ -f venv/bin/activate ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Start the server
echo "Starting server on http://127.0.0.1:8765"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python market_server.py --mode tcp --host 127.0.0.1 --port 8765
