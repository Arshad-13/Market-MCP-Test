# Standalone MCP Server Setup Guide

## Problem Solved
This guide helps you run the Market Intelligence MCP Server **outside** Claude Desktop's subprocess, bypassing network restrictions.

---

## Quick Start (3 Steps)

### Step 1: Start the Standalone Server

**Windows:**
```bash
# Double-click or run in terminal:
s:\Market-MCP\Market-MCP-Test\start_server.bat
```

**Linux/Mac:**
```bash
chmod +x start_server.sh
./start_server.sh
```

You should see:
```
🚀 Starting Market Intelligence MCP Server in TCP mode
📡 Listening on 127.0.0.1:8765
🔗 Configure Claude Desktop to connect to: tcp://127.0.0.1:8765
⚡ Press Ctrl+C to stop
```

✅ **Leave this terminal open!** The server must keep running.

---

### Step 2: Configure Claude Desktop

Edit your Claude Desktop config file:
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
- **Mac:** `~/Library/Application Support/Claude/claude_desktop_config.json`

**Replace the old configuration with:**

```json
{
  "mcpServers": {
    "market-intelligence": {
      "url": "http://127.0.0.1:8765/sse"
    }
  }
}
```

**Important:** Remove the old `command` and `args` fields!

---

### Step 3: Restart Claude Desktop

1. **Fully close** Claude Desktop (check system tray)
2. **Reopen** Claude Desktop
3. **Test** with:
   ```
   "Fetch orderbook for BTC/USDT"
   ```

---

## Expected Result

✅ **Success:**
```json
{
  "exchange": "binance",
  "symbol": "BTC/USDT",
  "bids": [[89329.99, 0.5], [89329.0, 1.2], ...],
  "asks": [[89330.0, 0.3], [89331.0, 0.8], ...],
  "fallback_used": false
}
```

If Binance fails, it will automatically fall back to Kraken/Coinbase/etc.

---

## Troubleshooting

### Server won't start
**Error:** `Address already in use`
**Solution:** Another process is using port 8765. Change the port:
```bash
python market_server.py --mode tcp --port 8766
```
Then update Claude config to `http://127.0.0.1:8766/sse`

### Claude can't connect
**Error:** `Connection refused`
**Solution:** 
1. Check server terminal is still running
2. Verify URL in config: `http://127.0.0.1:8765/sse`
3. Restart Claude Desktop

### Firewall blocking
**Solution:** Firewall rules should work now since server runs with YOUR privileges (not Claude's subprocess)

---

## Advanced Options

### Custom Host/Port
```bash
python market_server.py --mode tcp --host 0.0.0.0 --port 9000
```

### Run in Background (Linux/Mac)
```bash
nohup python market_server.py --mode tcp &
```

### Run as Windows Service
Use `nssm` or Task Scheduler to run `start_server.bat` on startup.

---

## Comparison: Subprocess vs Standalone

| Feature | Subprocess (Old) | Standalone (New) |
|---------|------------------|------------------|
| **Network Access** | ❌ Blocked by Claude | ✅ Full access |
| **Startup** | Automatic | Manual |
| **Firewall Rules** | Ignored | ✅ Respected |
| **Debugging** | Hard (hidden process) | ✅ Easy (visible terminal) |
| **Performance** | Same | Same |

---

## Next Steps

Once this works:
1. Test all MCP tools
2. Verify WebSocket streaming
3. Run agent pipeline
4. Test dashboard connectivity

**You're now unblocked!** 🚀
