# Market Intelligence MCP Server - Installation Guide

## Prerequisites

- **Python 3.10+** (Python 3.13 recommended)
- **Windows/Mac/Linux**
- **Claude Desktop** (for MCP integration)

---

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/Arshad-13/CryptoIntel-MCP.git
cd CryptoIntel-MCP
```

### 2. Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

**Core dependencies:**
- `mcp[cli]` - Model Context Protocol framework
- `httpx` - HTTP client for exchange APIs
- `streamlit` - Interactive dashboard
- `plotly` - Data visualization
- `websockets` - Real-time streaming
- `aiosqlite` - Async database
- `onnxruntime` - ML model inference

---

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Optional: API keys for extended functionality
CRYPTO_API_KEY=your_coingecko_api_key
```

### Claude Desktop Integration

1. **Copy configuration:**
   ```bash
   cp docs/claude_desktop_config.json %APPDATA%\Claude\claude_desktop_config.json
   ```

2. **Edit paths** in the config file to match your installation

3. **Restart Claude Desktop**

---

## Verify Installation

### Test Core Tools

```bash
python -c "import asyncio; from tools.exchange_tools import fetch_orderbook; print(asyncio.run(fetch_orderbook('BTC/USDT', 'binance', 5)))"
```

**Expected output:**
```json
{
  "exchange": "binance",
  "symbol": "BTC/USDT",
  "bids": [[88360.79, 0.5], ...],
  "asks": [[88360.80, 0.3], ...]
}
```

### Launch Dashboard

```bash
streamlit run dashboard.py
```

Open http://localhost:8501

---

## Troubleshooting

### Issue: Claude Desktop won't connect

**Solution:**
- Verify `claude_desktop_config.json` has correct paths
- Check MCP server starts without errors
- Restart Claude Desktop completely

### Issue: Exchange API errors

**Solution:**
- Check internet connection
- APIs use direct HTTP (no firewall rules needed)
- Try different exchange: `fetch_orderbook('BTC/USDT', 'kraken')`

### Issue: Dashboard errors

**Solution:**
```bash
pip install --upgrade -r requirements.txt
streamlit cache clear
```

---

## Next Steps

- Read [API Documentation](API.md)
- Explore [Dashboard Usage](DASHBOARD.md)
- Review [Architecture](ARCHITECTURE.md)
