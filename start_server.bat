@echo off
REM Standalone Market Intelligence MCP Server Launcher
REM Run this to start the server with full network access (bypasses Claude Desktop subprocess restrictions)

echo.
echo ========================================
echo Market Intelligence MCP Server
echo Standalone Mode (TCP)
echo ========================================
echo.

REM Change to the script directory
cd /d "%~dp0"

REM Activate virtual environment if it exists
if exist venv\Scripts\activate.bat (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
)

REM Start the server
echo Starting server on http://127.0.0.1:8765
echo.
echo Press Ctrl+C to stop the server
echo.

python market_server.py --mode tcp --host 127.0.0.1 --port 8765

pause
