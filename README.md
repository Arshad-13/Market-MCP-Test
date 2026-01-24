# 🧠 Market Intelligence MCP Server

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE) [![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://python.org) [![MCP](https://img.shields.io/badge/MCP-2025--06--18-green.svg)](https://modelcontextprotocol.io)

**Production-Ready AI Trading Agent** | Multi-Agent Orchestration | Real-Time Market Intelligence

Transform your LLM (Claude/GPT) into an autonomous cryptocurrency trading analyst with institutional-grade market surveillance, predictive ML models, and risk management.

---

## ✨ Key Features

### 🤖 Multi-Agent AI System (Phase 15)
- **ManagerAgent**: Coordinates specialist agents with weighted voting
- **ResearchAgent**: Market data fetching, ML predictions, analysis reports
- **RiskAgent**: Portfolio concentration, exposure limits, pre-trade checks
- **ExecutionAgent**: Smart order routing with slippage optimization

**Agent Pipeline:**
```
User Request → ManagerAgent
    ↓
    ├─→ ResearchAgent (Fetch orderbook, run ML)
    ├─→ RiskAgent (Check limits, validate risk)
    ├─→ ExecutionAgent (Plan execution, estimate cost)
    └─→ ManagerAgent (Aggregate, weighted voting, decision)
```

### 📊 Real-Time Market Data
- **Live Order Books**: Binance, Kraken, Coinbase, Bybit, OKX via `ccxt`
- **Ticker Data**: Multi-asset price, volume, 24h change monitoring
- **Tools**: `fetch_orderbook`, `fetch_ticker`, `list_supported_exchanges`

### 🧠 AI & Predictive Analytics
- **DeepLOB Lite**: Price direction prediction from Order Flow Imbalance
- **Strategy Engine**: Multi-signal aggregation (ML + Sentiment + Risk)
- **Regime Detection**: Classify markets (Calm/Volatile/Manipulated)
- **Tools**: `predict_price_direction`, `get_trading_signal`

### 🔬 Market Microstructure Analysis
- **Anomaly Detection**: Spoofing, layering, liquidity gaps
- **Advanced Metrics**: OFI, OBI, Microprice, VPIN
- **Tools**: `analyze_orderbook`, `detect_spoofing`, `calculate_microstructure_features`

### 🛡️ Risk Management & Execution
- **Risk Engine**: Pre-trade checks (max size, daily loss limits)
- **Paper Trading**: Safe simulated execution mode
- **Slippage Simulation**: Market impact estimation for large orders
- **Tools**: `execute_order`, `get_positions`, `analyze_portfolio_risk`

### 🔔 Smart Notifications
- **Background Service**: Persistent monitoring for price alerts
- **SQLite Persistence**: Alert history survives restarts
- **Tools**: `create_price_alert`, `check_alerts`, `mark_alerts_read`

### 🌐 External Intelligence
- **Fear & Greed Index**: Real-time market sentiment (Alternative.me)
- **DeFi Intelligence**: TVL and protocol stats (DeFi Llama)
- **Gas Tracking**: Live Ethereum gas prices (Etherscan)
- **Tools**: `get_fear_greed_index`, `get_defi_tvl`, `get_gas_price`

### 📈 Interactive Dashboard
- **Technology**: Streamlit + Plotly
- **Tabs**: Market Intel, Deep Brain, Execution & Risk, Alerts
- **Run**: `streamlit run dashboard.py`

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.10+** (Python 3.13 recommended for Claude Desktop)
- **pip** or **uv** package manager
- **Claude Desktop** (optional, for MCP integration)

### Installation

```bash
# Clone the repository
git clone https://github.com/Arshad-13/Market-MCP-Test.git
cd Market-MCP-Test

# Install dependencies
pip install -r requirements.txt

# Optional: Create .env file for API keys
echo "CRYPTO_API_KEY=your_coingecko_key" > .env
```

### Running the Server

**Option 1: MCP Server Mode (for Claude Desktop)**
```bash
python market_server.py
```

**Option 2: Interactive Dashboard**
```bash
streamlit run dashboard.py
```

---

## 🔌 Claude Desktop Integration

### Configuration

1. **Locate config file**: `%APPDATA%\Claude\claude_desktop_config.json` (Windows) or `~/Library/Application Support/Claude/claude_desktop_config.json` (Mac)

2. **Add server configuration**:
```json
{
  "mcpServers": {
    "market-intelligence": {
      "command": "python",
      "args": ["s:/Market-MCP/Market-MCP-Test/market_server.py"],
      "cwd": "s:/Market-MCP/Market-MCP-Test"
    }
  }
}
```

3. **Restart Claude Desktop**

4. **Test with prompts**:
   - `"Run analysis pipeline for BTC/USDT"`
   - `"Get agent status"`
   - `"Fetch orderbook for ETH/USDT"`

### Firewall Configuration (Windows)

If exchange tools fail with `ExchangeNotAvailable`, add firewall rules:

1. Open **Windows Defender Firewall** → Advanced Settings
2. Create **Outbound Rule** for Python:
   - Program: `C:\Users\<YourUser>\AppData\Local\Programs\Python\Python313\python.exe`
   - Action: Allow all connections
3. Restart Claude Desktop

---

## 🧪 Testing

### Unit Tests
```bash
# Multi-Agent System
python tests/test_agents.py

# Strategy Engine
python tests/test_strategy.py

# Execution & Risk
python tests/test_execution.py

# All Integration Tests
python tests/test_integration.py
```

### MCP Tools Testing (in Claude Desktop)
```
Basic Tools:
- "Get the current price of bitcoin"
- "What's the Fear & Greed index?"

Advanced Tools:
- "Fetch orderbook for BTC/USDT on Binance"
- "Predict price direction for ETH based on current orderbook"
- "Analyze portfolio risk: 50% BTC, 50% ETH"

Multi-Agent Pipeline:
- "Run analysis pipeline for BTC/USDT"
- "Get agent status"
- "What do all the agents think about SOL/USDT?"
```

---

## 📁 Project Structure

```
Market-MCP-Test/
├── agents/                    # Multi-Agent System
│   ├── base_agent.py         # Abstract BaseAgent + AgentContext
│   ├── manager_agent.py      # Coordinator with weighted voting
│   ├── research_agent.py     # Market data + ML analysis
│   ├── risk_agent.py         # Portfolio risk specialist
│   └── execution_agent.py    # Smart order routing
├── core/                      # Analytics Engine
│   ├── analytics.py          # Microstructure (OFI, OBI, VPIN)
│   ├── ml_models.py          # DeepLOB Lite model
│   ├── strategy_engine.py    # Signal aggregation
│   ├── risk_engine.py        # Pre-trade checks
│   ├── database.py           # SQLite persistence
│   └── background_service.py # Alert monitoring
├── tools/                     # MCP Tool Definitions
│   ├── agent_tools.py        # Multi-agent orchestration
│   ├── exchange_tools.py     # CCXT connectivity
│   ├── ml_tools.py           # AI predictions
│   ├── strategy_tools.py     # Trading signals
│   ├── trading_tools.py      # Paper trading
│   ├── portfolio_tools.py    # Risk analysis
│   ├── alert_tools.py        # Notifications
│   └── sentiment_tools.py    # Fear/Greed, DeFi
├── prompts/                   # MCP Prompt Templates
│   └── market_prompts.py     # 3 prompts (briefing, liquidity, anomalies)
├── tests/                     # Test Suite (11 files)
├── dashboard.py              # Streamlit UI
├── market_server.py          # MCP Server Entry Point
└── requirements.txt          # Python dependencies
```

---

## 🛠️ Available MCP Tools (30+)

### Agent Orchestration
- `run_analysis_pipeline(symbol, sentiment_score)` - Trigger full agent swarm
- `get_agent_status()` - Check all agents' status
- `set_auto_execute(enabled)` - Enable/disable auto-trading

### Exchange Data
- `fetch_orderbook(symbol, exchange, limit)` - Live L2 data
- `fetch_ticker(symbol, exchange)` - Price, volume, 24h change
- `list_supported_exchanges()` - Available exchanges

### AI & Strategy
- `predict_price_direction(symbol, exchange)` - DeepLOB ML prediction
- `get_trading_signal(symbol, sentiment)` - Aggregated Buy/Sell/Hold signal

### Risk & Execution
- `execute_order(symbol, side, amount, price)` - Paper trading
- `get_positions()` - Current portfolio
- `analyze_portfolio_risk(holdings, total_value)` - Risk scoring
- `simulate_slippage(symbol, side, volume)` - Cost impact

### Market Analysis
- `analyze_orderbook(orderbook_json)` - Microstructure metrics
- `detect_spoofing(orderbook_json)` - Manipulation detection
- `calculate_microstructure_features(orderbook_json)` - OFI, OBI

### Alerts & Sentiment
- `create_price_alert(asset, target_price, direction)` - Set alert
- `check_alerts()` - View active alerts
- `get_fear_greed_index()` - Market sentiment
- `get_defi_tvl(protocol)` - DeFi stats

---

## 📊 Dashboard Features

Launch with `streamlit run dashboard.py` to access:

1. **Market Intel Tab**
   - Live BTC/USDT price
   - 24-hour change
   - Order book depth chart (bids vs asks)

2. **Deep Brain Tab**
   - Agent reasoning logs
   - ML signal (action, confidence, rationale)
   - Microstructure features (OFI, OBI, Microprice Divergence)

3. **Execution & Risk Tab**
   - Paper trading balance
   - Active positions
   - Risk engine limits (max trade size, daily loss, restricted assets)

4. **Alerts Tab**
   - Alert history with timestamps
   - Status indicators

---

## 🔧 Configuration

### Environment Variables (.env)
```bash
# Optional: CoinGecko API Key (for premium features)
CRYPTO_API_KEY=your_coingecko_api_key

# Optional: Etherscan API Key (for gas tracking)
ETHERSCAN_API_KEY=your_etherscan_key

# Optional: Enable live trading (NOT RECOMMENDED)
ENABLE_LIVE_TRADING=false

# Optional: Custom database path
DATABASE_PATH=./market_data.db
```

### Risk Engine Configuration
Edit `core/risk_engine.py` to customize:
- Max trade size (default: $100,000)
- Max daily loss (default: $10,000)
- Max position concentration (default: 10%)
- Restricted assets list

---

## 🐛 Known Issues & Troubleshooting

### Issue: Exchange APIs Fail with "ExchangeNotAvailable"
**Cause:** Windows Firewall blocking Python subprocess  
**Solution:** Add firewall rules for Python 3.13 (see Claude Desktop Integration section)

### Issue: Module Not Found Errors
**Cause:** Dependencies installed in wrong Python version  
**Solution:** 
```bash
# Check Python version
python --version

# Install to correct version
py -3.13 -m pip install -r requirements.txt
```

### Issue: Dashboard Shows No Data
**Cause:** No database file or empty alerts  
**Solution:** Create alerts first using MCP tools, then refresh dashboard

---

## 📈 Roadmap

### Planned Features
- [ ] WebSocket streaming for real-time orderbook updates
- [ ] Backtesting framework (historical data replay)
- [ ] Advanced ML models (Transformer-based LOB prediction)
- [ ] Portfolio optimization (Markowitz, Black-Litterman)
- [ ] Sentiment analysis (Twitter/Reddit integration)
- [ ] Docker containerization
- [ ] Cloud deployment (AWS/GCP)

---

## 📄 Documentation

- **[Implementation Plan](docs/implementation_plan.md)** - Original design document
- **[Project Status](docs/project_status.md)** - Current completion status
- **[Walkthrough](docs/walkthrough.md)** - Verification results & proof of work
- **[CHANGELOG](CHANGELOG.md)** - Version history

---

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📜 License

MIT License - See [LICENSE](LICENSE) file for details.

**Based on:** HFT Platform Genesis2025

---

## 🙏 Acknowledgments

- **MCP Protocol** - Model Context Protocol by Anthropic
- **CCXT** - CryptoCurrency eXchange Trading Library
- **DeepLOB** - Deep Learning for Limit Order Books
- **Genesis2025** - Original HFT analytics platform

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/Arshad-13/Market-MCP-Test/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Arshad-13/Market-MCP-Test/discussions)

---

**⚠️ Disclaimer**: This software is for educational and research purposes only. Not financial advice. Trade at your own risk.
