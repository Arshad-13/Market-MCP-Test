# Market Intelligence MCP Server

> A production-ready Model Context Protocol server for cryptocurrency market intelligence, powered by real-time exchange data, machine learning, and multi-agent orchestration.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![MCP Compatible](https://img.shields.io/badge/MCP-Compatible-green.svg)](https://modelcontextprotocol.io/)

---

## 🚀 Features

### **30+ MCP Tools** Across 11 Categories
- 📊 **Real-Time Exchange Data** - Binance, Kraken, Coinbase orderbooks & tickers
- 🔬 **Market Microstructure** - OFI, OBI, Microprice, VPIN analytics
- 🤖 **ML Price Prediction** - DeepLOB-Lite model for buy/sell signals
- 🎯 **Trading Strategies** - Multi-signal aggregation engine
- 👥 **Multi-Agent System** - Research, Risk, Execution agents with voting
- 📡 **WebSocket Streaming** - Real-time orderbook/ticker updates
- 🔔 **Smart Alerts** - Price-based notifications with background monitoring
- 💼 **Portfolio Management** - Risk analysis, P&L tracking, paper trading
- 🕵️ **Anomaly Detection** - Spoofing, layering, market regime classification
- 📈 **Interactive Dashboard** - Streamlit UI for live market visualization
- 🌐 **Sentiment Analysis** - Fear & Greed Index integration

---

## 📋 Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/Arshad-13/Market-MCP-Test.git
cd Market-MCP-Test

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Claude Desktop Integration

1. **Copy configuration** to Claude Desktop:
   ```bash
   cp docs/claude_desktop_config.json %APPDATA%\Claude\claude_desktop_config.json
   ```

2. **Update paths** in the config file to match your installation

3. **Restart Claude Desktop**

4. **Test:**
   ```
   "Fetch orderbook for BTC/USDT"
   "Run analysis pipeline for ETH/USDT with sentiment 0.7"
   ```

### Launch Dashboard

```bash
streamlit run dashboard.py
```

Open http://localhost:8501

---

## 🎯 Use Cases

### **1. Market Analysis with Claude**

```
You: "What's the current liquidity situation for BTC/USDT?"

Claude: [Fetches orderbook, calculates depth, analyzes spread]
"The BTC/USDT orderbook shows strong liquidity with 
$2.3M in bids within 0.5% of mid-price..."
```

### **2. ML-Driven Trading Signals**

```python
from tools.strategy_tools import get_trading_signal

signal = await get_trading_signal('ETH/USDT', sentiment_score=0.6)
# Returns: {'signal': 'BUY', 'confidence': 0.82, ...}
```

### **3. Multi-Agent Pipeline**

```
You: "Run full analysis on SOL/USDT"

Claude: [Orchestrates Research → Risk → Execution agents]
"Research Agent: ML prediction BUY (78% confidence)
Risk Agent: Position size approved (2x BTC)
Execution Agent: Recommended entry: $142.35"
```

### **4. Real-Time Monitoring**

- **Dashboard:** Live orderbook depth charts, ML predictions, portfolio P&L
- **WebSocket Streams:** Subscribe to orderbook/ticker updates
- **Alerts:** Get notified when BTC crosses $90,000

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Claude Desktop                         │
└────────────────────┬────────────────────────────────────┘
                     │ JSON-RPC / STDIO
┌────────────────────▼────────────────────────────────────┐
│          Market Intelligence MCP Server                 │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │  Exchange    │  │  Analytics   │  │   Strategy   │ │
│  │   Tools      │  │    Engine    │  │    Engine    │ │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘ │
│         │  Direct HTTP     │  ML Models       │  Agents│ │
│  ┌──────▼──────────────────▼──────────────────▼───────┐ │
│  │   Binance  │  Kraken  │  Coinbase  │  WebSockets  │ │
│  └──────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

**Key Technologies:**
- 🐍 **Python 3.13** - Async I/O, type hints
- 🔌 **httpx** - Direct REST API calls (no CCXT overhead)
- ⚡ **websockets** - Real-time streaming
- 🧠 **ONNX Runtime** - ML model inference
- 📊 **Streamlit** - Interactive dashboard
- 💾 **SQLite** - Local persistence

**See [Architecture Documentation](docs/ARCHITECTURE.md) for details**

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [Installation Guide](docs/INSTALLATION.md) | Setup, configuration, troubleshooting |
| [API Reference](docs/API.md) | Complete tool documentation with examples |
| [Architecture](docs/ARCHITECTURE.md) | System design, data flows, scalability |
| [Dashboard Guide](docs/DASHBOARD.md) | Dashboard features and customization |
| [Changelog](docs/CHANGELOG.md) | Version history and feature timeline |

---

## 🛠️ Development

### Project Structure

```
Market-MCP-Test/
├── core/           # Business logic (analytics, ML, risk)
├── tools/          # MCP tool implementations
├── agents/         # Multi-agent system
├── tests/          # Test suite (pytest)
├── docs/           # Documentation
├── dashboard.py    # Streamlit UI
└── market_server.py # MCP server entry point
```

### Running Tests

```bash
pytest tests/ -v
```

**Coverage:** 13 test files, 100+ test cases

### Adding New Tools

1. Create function in `tools/your_tool.py`
2. Register in `market_server.py`:
   ```python
   @mcp.tool()
   def your_tool(param: str) -> str:
       return your_function(param)
   ```
3. Add tests in `tests/test_your_tool.py`

---

## 🔧 Configuration

### Environment Variables (`.env`)

```env
# Optional: For premium APIs
CRYPTO_API_KEY=your_coingecko_api_key
```

### Exchange Fallback

Automatic failover: Binance → Kraken → Coinbase

Configure in `tools/exchange_tools.py`:
```python
EXCHANGE_FALLBACK_ORDER = ["binance", "kraken", "coinbase"]
```

---

## 📊 Example Outputs

### Orderbook Data
```json
{
  "symbol": "BTC/USDT",
  "exchange": "binance",
  "bids": [[88360.79, 0.5], [88360.0, 1.2]],
  "asks": [[88361.0, 0.3], [88361.5, 0.8]],
  "fallback_used": false
}
```

### Trading Signal
```json
{
  "signal": "BUY",
  "confidence": 0.85,
  "components": {
    "ml_prediction": "buy",
    "ml_confidence": 0.78,
    "sentiment_score": 0.7,
    "risk_reward_ratio": 3.2
  }
}
```

### Multi-Agent Pipeline
```json
{
  "final_decision": "BUY",
  "confidence": 0.82,
  "agents": {
    "research": {"recommendation": "buy", "confidence": 0.78},
    "risk": {"approved": true, "max_size": 0.05},
    "execution": {"entry_price": 88360.0, "slippage": 0.02}
  }
}
```

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Model Context Protocol (MCP)** - Anthropic's extensible AI integration framework
- **DeepLOB** - Limit order book prediction research
- **Alternative.me** - Fear & Greed Index data

---

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/Arshad-13/CryptoIntel-MCP/issues)
- **Discussions:** [GitHub Discussions](https://github.com/Arshad-13/CryptoIntel-MCP/discussions)
- **Documentation:** [docs/](docs/)

---

**Built with ❤️ for the crypto trading community**

*Disclaimer: This is an educational project. Not financial advice. Trade at your own risk.*
