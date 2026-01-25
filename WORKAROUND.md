# Quick Fix: Running Market Intelligence Server Outside Claude Desktop

## The Simple Solution That Works NOW

Since Claude Desktop blocks network access in subprocess, the easiest fix is:

### **Just run your Python tests directly!**

Your direct Python works perfectly (we verified with diagnose_network.py). So:

```bash
# Terminal 1: Keep this open for testing
cd s:\Market-MCP\Market-MCP-Test
python

# In Python REPL:
>>> import asyncio
>>> from tools.exchange_tools import fetch_orderbook
>>> result = asyncio.run(fetch_orderbook("BTC/USDT", "binance", 20))
>>> print(result)
```

**Result:** Real Binance orderbook data! ✅

---

## The Workaround for Claude Desktop

Since FastMCP doesn't support standalone TCP mode easily, here's what works:

### **Option 1: Use Direct Python (RECOMMENDED)**
Test all your tools, agents, strategies directly in Python:

```python
# Test orderbook fetching
from tools.exchange_tools import fetch_orderbook
import asyncio
import json

result = asyncio.run(fetch_orderbook("BTC/USDT"))
data = json.loads(result)
print(f"Top bid: ${data['bids'][0][0]}")
```

### **Option 2: Modify Claude Desktop Config to Allow Network**
Unfortunately, Claude Desktop's subprocess isolation is intentional for security. There's no easy workaround without modifying Claude itself.

### **Option 3: Use the Dashboard Instead**
The Streamlit dashboard runs in YOUR Python (not Claude's subprocess):

```bash
streamlit run dashboard.py
```

Open http://localhost:8501 - Full network access! ✅

---

## Summary

**For Development:**
- ✅ Use Python REPL for testing tools
- ✅ Use Streamlit dashboard for UI
- ✅ Full network access; all exchanges work

**For Claude Desktop:**
- ❌ Subprocess blocks network (unfixable)
- ✅ Can still use non-network tools (sentiment, calculations, etc.)
- ⚠️ Exchange tools won't work until Claude fixes this

**Best Approach:** Develop with Python/Dashboard, deploy elsewhere when ready.

---

## What Actually Works in Claude Desktop

**These tools work fine:**
- ✅ `get_crypto_price` (CoinGecko - if API key set)
- ✅ `get_fear_greed_index`
- ✅ `analyze_orderbook` (if you paste orderbook data)
- ✅ `detect_spoofing` (if you paste orderbook data)
- ✅ All ML/Strategy calculations
- ✅ All agents (with manual data input)

**These fail due to network blocking:**
- ❌ `fetch_orderbook`
- ❌ `fetch_ticker`
- ❌ Any direct exchange API calls

**Solution:** Get data externally, paste into Claude for analysis!
