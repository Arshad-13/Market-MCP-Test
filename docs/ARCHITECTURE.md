# Architecture - Market Intelligence MCP Server

## System Overview

The Market Intelligence MCP Server is a modular, production-ready platform for cryptocurrency market analysis, trading strategies, and multi-agent orchestration.

```
┌─────────────────────────────────────────────────────────┐
│                   Claude Desktop                         │
│              (MCP Client / User Interface)               │
└────────────────────┬────────────────────────────────────┘
                     │ JSON-RPC / STDIO
                     │
┌────────────────────▼────────────────────────────────────┐
│              Market Intelligence MCP Server              │
│  ┌──────────────────────────────────────────────────┐  │
│  │            MCP Tool Registry (30+ tools)         │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  Exchange   │  │  Analytics   │  │   Strategy   │  │
│  │    Tools    │  │    Engine    │  │    Engine    │  │
│  └──────┬──────┘  └──────┬───────┘  └──────┬───────┘  │
│         │                 │                  │          │
│  ┌──────▼──────┐  ┌──────▼───────┐  ┌──────▼───────┐  │
│  │   Direct    │  │ Microstructure│  │  Multi-Agent │  │
│  │ HTTP APIs   │  │   Analytics   │  │Orchestration │  │
│  └─────────────┘  └──────────────┘  └──────────────┘  │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   WebSocket  │  │  Persistence │  │  Background  │  │
│  │    Manager   │  │   (SQLite)   │  │   Services   │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
┌───────▼──────┐ ┌──▼──────┐ ┌──▼──────────┐
│   Binance    │ │ Kraken  │ │  Coinbase   │
│     API      │ │   API   │ │     API     │
└──────────────┘ └─────────┘ └─────────────┘
```

---

## Directory Structure

```
CryptoIntel-MCP/
├── core/                      # Core business logic
│   ├── analytics.py           # Microstructure calculations
│   ├── anomaly_detection.py   # Market manipulation detection
│   ├── background_service.py  # Alert monitoring
│   ├── data_validator.py      # Input validation
│   ├── database.py            # SQLite async operations
│   ├── ml_models.py           # DeepLOB-Lite predictor
│   ├── risk_engine.py         # Pre-trade risk checks
│   ├── strategy_engine.py     # Signal aggregation
│   └── websocket_manager.py   # WebSocket pooling
│
├── tools/                     # MCP tool implementations
│   ├── exchange_tools.py      # Orderbook/ticker fetching
│   ├── microstructure_tools.py# Market microstructure
│   ├── ml_tools.py            # ML predictions
│   ├── strategy_tools.py      # Trading signals
│   ├── trading_tools.py       # Paper trading
│   ├── portfolio_tools.py     # Risk analytics
│   ├── agent_tools.py         # Multi-agent orchestration
│   ├── alert_tools.py         # Price alerts
│   ├── sentiment_tools.py     # Fear & Greed Index
│   ├── anomaly_tools.py       # Spoofing/layering
│   └── streaming_tools.py     # WebSocket subscriptions
│
├── agents/                    # Multi-agent system
│   ├── manager_agent.py       # Coordination & voting
│   ├── research_agent.py      # Data gathering & analysis
│   ├── risk_agent.py          # Risk assessment
│   └── execution_agent.py     # Order execution
│
├── prompts/                   # MCP prompt templates
│   └── market_prompts.py      # Daily briefing, liquidity analysis
│
├── tests/                     # Comprehensive test suite
│   ├── test_exchange_tools.py
│   ├── test_core_analytics.py
│   ├── test_agents.py
│   ├── test_websocket.py
│   └── ... (13 test files total)
│
├── docs/                      # Documentation
│   ├── API.md                 # API reference
│   ├── ARCHITECTURE.md        # This file
│   ├── INSTALLATION.md        # Setup guide
│   ├── DASHBOARD.md           # Dashboard usage
│   ├── CHANGELOG.md           # Version history
│   └── claude_desktop_config.json
│
├── dashboard.py               # Streamlit UI
├── market_server.py           # MCP server entry point
├── requirements.txt           # Python dependencies
├── .env                       # Environment config
└── README.md                  # Project overview
```

---

## Core Components

### 1. Exchange Connectivity (`tools/exchange_tools.py`)

**Technology:** Direct HTTP APIs (httpx)
- ✅ No CCXT dependency (simplified, faster)
- ✅ Multi-exchange fallback
- ✅ Supports: Binance, Kraken, Coinbase

**Key Functions:**
- `fetch_orderbook()` - L2 order book data
- `fetch_ticker()` - 24h ticker stats
- Symbol conversion for exchange-specific formats

---

### 2. Analytics Engine (`core/analytics.py`)

**Algorithms:**
- **OFI** (Order Flow Imbalance)
- **OBI** (Order Book Imbalance)
- **Microprice** calculation
- **VPIN** (Volume-Synchronized Probability of Informed Trading)
- **Spread analysis**

**Purpose:** High-frequency market microstructure analytics

---

### 3. ML Prediction (`core/ml_models.py`)

**Model:** DeepLOB-Lite (Lightweight limit order book predictor)

**Features:**
- Order flow imbalance
- Mid-price changes
- Volume ratios

**Output:** Buy/Sell/Hold + confidence score

---

### 4. Strategy Engine (`core/strategy_engine.py`)

**Signal Aggregation:**
1. ML prediction (40% weight)
2. Sentiment analysis (30% weight)
3. Risk/reward ratio (30% weight)

**Output:** Final BUY/SELL/HOLD recommendation

---

### 5. Multi-Agent System (`agents/`)

**Architecture:** Manager + 3 specialized agents

**Agents:**
- **ManagerAgent**: Weighted voting, pipeline orchestration
- **ResearchAgent**: Data fetching, ML predictions
- **RiskAgent**: Portfolio checks, exposure limits
- **ExecutionAgent**: Smart order routing, slippage optimization

**Communication:** Shared context via `AgentContext` dataclass

---

### 6. WebSocket Manager (`core/websocket_manager.py`)

**Features:**
- Concurrent multi-symbol streaming
- Auto-reconnection with exponential backoff
- Message normalization (unified format)
- Connection health monitoring

**Supported Streams:**
- Binance orderbook (@depth20)
- Binance ticker (24hrTicker)

---

### 7. Persistence Layer (`core/database.py`)

**Database:** SQLite (async via aiosqlite)

**Tables:**
- `alerts` - Price alert definitions
- `market_data_cache` - Cached API responses
- `portfolio_state` - Paper trading positions

---

### 8. Background Services (`core/background_service.py`)

**Monitors:**
- Active price alerts
- Database writes on trigger
- Polling interval: 10 seconds

---

## Data Flow

### Example: Fetch Orderbook

```
1. User (Claude Desktop)
   ↓ "Fetch orderbook for BTC/USDT"
   
2. MCP Server (market_server.py)
   ↓ Parses request, calls tool
   
3. fetch_orderbook() (tools/exchange_tools.py)
   ↓ Tries Binance first
   
4. Direct HTTP API (httpx)
   ↓ GET api.binance.com/api/v3/depth
   
5. Response normalization
   ↓ Convert to unified format
   
6. Return JSON to Claude
   ✅ Display orderbook
```

---

## Security & Best Practices

### API Keys
- Stored in `.env` (git-ignored)
- Optional for most features
- Required only for premium APIs

### Rate Limiting
- Built-in via httpx timeout (30s)
- Exchange fallback prevents overload

### Input Validation
- `core/data_validator.py` validates all inputs
- Prevents injection attacks

### Error Handling
- Graceful degradation (fallback exchanges)
- Comprehensive logging to stderr
- User-friendly error messages

---

## Performance Characteristics

| Operation | Latency | Notes |
|-----------|---------|-------|
| Fetch Orderbook | <300ms | Direct API, no CCXT overhead |
| ML Prediction | <100ms | Lightweight model |
| Agent Pipeline | <1s | Parallel agent execution |
| WebSocket Stream | Real-time | ~50ms updates |
| Dashboard Load | <2s | Streamlit caching |

---

## Scalability

**Current:**
- Single-process, async I/O
- SQLite (local)
- Suitable for: Personal use, testing, small teams

**Future Enhancements:**
- Redis caching (distributed)
- PostgreSQL (production DB)
- Kubernetes deployment
- Multi-process workers

---

## Technology Stack

| Layer | Technology |
|-------|-----------|
| **Protocol** | Model Context Protocol (MCP) |
| **Language** | Python 3.13 |
| **Async** | asyncio, aiohttp, aiosqlite |
| **HTTP** | httpx |
| **WebSockets** | websockets library |
| **ML** | ONNX Runtime |
| **Database** | SQLite |
| **Dashboard** | Streamlit, Plotly |
| **Testing** | pytest, AsyncMock |

---

## Extension Points

### Adding New Exchanges

1. Add endpoint to `EXCHANGE_APIS` dict
2. Implement `_fetch_EXCHANGE_orderbook()`
3. Add symbol conversion in `_convert_symbol()`
4. Update fallback order

### Adding New Tools

1. Create function in `tools/`
2. Register in `market_server.py`
3. Export in `tools/__init__.py`
4. Add tests in `tests/`

### Adding New Agents

1. Create agent in `agents/`
2. Inherit shared patterns
3. Register in `agents/__init__.py`
4. Update manager agent voting

---

## Monitoring & Debugging

**Logs:**
- All operations log to `stderr`
- Claude Desktop logs: Available in app settings

**Dashboard:**
- Real-time health checks
- Agent status display
- Stream connection monitoring

**Testing:**
```bash
pytest tests/ -v
```

13 test files, 100+ test cases
