# 🧠 Market Intelligence MCP Server

A **Best-in-Class** Model Context Protocol (MCP) server for Professional Crypto Market Analysis. 

This server transforms your LLM (Claude/Gemini) into an **Autonomous HFT Quant Agent** capable of real-time surveillance, predictive modeling, and risk assessment.

![License](https://img.shields.io/badge/license-MIT-blue.svg) ![Python](https://img.shields.io/badge/python-3.10+-blue.svg) ![MCP](https://img.shields.io/badge/MCP-Enabled-green.svg)

---

## ✨ Key Capabilities

The server integrates institutional-grade analytics from **Genesis2025** and expands them with live connectivity.

### 1. ⚡ Real-Time Exchange Connectivity
- **Live Order Books**: Fetch Level 2 data directly from Binance, Kraken, Coinbase, and more via `ccxt`.
- **Tickers**: Multi-asset price and volume monitoring.
- **Tools**: `fetch_orderbook`, `fetch_ticker`

### 2. 🧠 AI & Predictive Analytics
- **DeepLOB Lite**: Lightweight ML model that predicts short-term price direction ("UP"/"DOWN") based on Order Flow Imbalance (OFI).
- **Regime Detection**: Classify markets as "Calm", "Volatile", or "Manipulated".
- **Tools**: `predict_price_direction`, `analyze_volatility_regime`

### 3. 🔬 Microstructure Surveillance
- **Anomaly Detection**: Detect layering, spoofing, and liquidity gaps in the order book.
- **Advanced Metrics**: Calculate Microprice, VPIN (Volume-Synchronized Probability of Informed Trading), and Spread efficiency.
- **Tools**: `analyze_orderbook`, `detect_spoofing`, `calculate_microprice`

### 4. 🛡️ Portfolio & Risk Intelligence
- **Risk Scoring**: Evaluate portfolios for concentration risk and volatility exposure.
- **Slippage Simulator**: Estimate execution costs and market impact for large trades ("Whale Simulation").
- **Tools**: `analyze_portfolio_risk`, `simulate_slippage`

### 5. 🔔 Smart Notifications
- **Background Monitor**: Persistent service detecting market events.
- **Alert System**: Set price triggers and receive proactive notifications.
- **Tools**: `create_price_alert`, `check_alerts`

### 6. 🌐 Macro & Sentiment
- **Fear & Greed**: Real-time market sentiment index.
- **DeFi Intelligence**: TVL and Protocol stats via DeFi Llama.
- **Gas Tracking**: Live Ethereum gas prices.
- **Tools**: `get_fear_and_greed_index`, `get_defi_global_stats`, `get_gas_price`

---

## 🚀 Installation

#- **Alerts**: Create and check alerts (`create_price_alert`, `check_alerts`).

### 8. Persistence (New)
- **SQLite Database**: Stores alerts and history locally (`market_data.db`).
- **Resiliency**: Data survives server generation restarts.

### 9. Execution Engine (New)
- **Risk Guard**: Pre-trade checks for max size and loss limits (`risk_engine`).
- **Paper Trading**: Safe, simulated execution mode (`execute_order`).

### 10. Strategy Engine (New)
- **Orchestrator**: Combines ML, Sentiment, and Risk/Reward into a final `Signal`.
### 10. Strategy Engine (New)
- **Orchestrator**: Combines ML, Sentiment, and Risk/Reward into a final `Signal`.
- **Tools**: `get_trading_signal` (Buy/Sell/Hold confidence).

### 11. Interactive Dashboard (New)
- **UI**: Streamlit web interface.
- **Features**: Live Orderbook, ML Confidence charting, Portfolio view.
- **Run**: `streamlit run dashboard.py`

### 12. Multi-Agent System (New)
- **RiskAgent**: Portfolio concentration, exposure limits.
- **ExecutionAgent**: Smart order routing.
- **ResearchAgent**: Deep market analysis.
- **ManagerAgent**: Orchestrates all agents with weighted voting.
- **Tools**: `run_analysis_pipeline` (triggers full agent swarm).

## Prerequisites
- Python 3.10 or higher
- [uv](https://github.com/astral-sh/uv) (recommended) or pip

### Quick Start

1. **Clone & Install**
   ```bash
   git clone https://github.com/Arshad-13/Market-MCP-Test.git
   cd Market-MCP-Test
   pip install -r requirements.txt
   ```

2. **Configuration**
   Create a `.env` file in the root directory:
   ```env
   # Required for CoinGecko Pro (optional for free tier but recommended)
   CRYPTO_API_KEY=your_coingecko_key_here
   
   # Optional for Gas tracking
   ETHERSCAN_API_KEY=your_etherscan_key_here
   ```

3. **Running the Server**
   ```bash
   mcp run market_server.py
   ```

---

## 🔌 Integration with Claude Desktop

Add this to your `%APPDATA%\Claude\claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "market-intelligence": {
      "command": "python",
      "args": [
        "S:\\Market-MCP\\Market-MCP-Test\\market_server.py"
      ],
      "env": {
        "CRYPTO_API_KEY": "your_key",
        "PYTHONPATH": "S:\\Market-MCP\\Market-MCP-Test"
      }
    }
  }
}
```

---

## 🧪 Testing

The project includes a comprehensive verification suite:

```bash
# 1. Core Analytics Logic
python tests/test_core_analytics.py

# 2. External APIs (Sentiment/DeFi)
python tests/test_external_apis.py

# 3. Exchange Connectivity (Mocked)
python tests/test_exchange_tools.py

# 4. AI Prediction Engine
python tests/test_ml_prediction.py

# 5. Portfolio Risk
python tests/test_portfolio_tools.py

# 6. Alerts & Notifications
python tests/test_alert_tools.py

# Run All Integration Tests
python tests/test_integration.py
```

---

## 🏗️ Architecture

```
Market-MCP-Test/
├── core/                   # Analytics Engine (Ported from Genesis2025)
│   ├── analytics.py        # Microstructure math (OFI, OBI, VPIN)
│   ├── anomaly_detection.py# Spoofing/Layering logic
│   └── background_service.py # Alert monitor
├── tools/                  # MCP Tool Definitions
│   ├── exchange_tools.py   # ccxt connectivity
│   ├── ml_tools.py         # AI inference
│   ├── portfolio_tools.py  # Risk analysis
│   └── ...
├── prompts/                # Prompt Templates
├── tests/                  # Verification Suite
└── market_server.py        # Main Entry Point
```

---

## 📜 License

MIT License. Based on the HFT Platform.
