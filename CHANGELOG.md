# Changelog

All notable changes to the Market Intelligence MCP Server project.

## [1.26.0] - 2026-01-25

### Added - Phase 16: WebSocket Streaming
- **WebSocket Manager**: `core/websocket_manager.py`
  - Real-time WebSocket connections with auto-reconnection
  - Exponential backoff for connection resilience (up to 5 attempts)
  - Message normalization to unified format across exchanges
  - Connection pooling for multi-symbol concurrent streaming
- **Streaming Tools**: `tools/streaming_tools.py` - 5 new MCP tools
  - `subscribe_orderbook_stream(symbol, exchange)`: Subscribe to live orderbook
  - `subscribe_ticker_stream(symbol, exchange)`: Subscribe to live ticker
  - `stop_stream(stream_id)`: Stop an active stream
  - `list_active_streams()`: Get all active WebSocket connections
  - `check_stream_health(stream_id)`: Check connection status
- **Binance Integration**: WebSocket support for orderbook (@depth20) and ticker streams
- **Test Suite**: `tests/test_websocket.py` - 11 comprehensive tests
  - StreamSubscription dataclass verification
  - WebSocketManager initialization and lifecycle
  - Message normalization (orderbook + ticker)
  - Stream subscription/unsubscription
  - Tool function validation

### Changed
- **Dependencies**: Added `websockets>=12.0` to requirements.txt
- **Server Integration**: Updated `market_server.py` to register streaming tools
- **Package Exports**: Updated `tools/__init__.py` to export streaming functions

---

## [1.25.0] - 2026-01-25

### Added - Phase 15: Multi-Agent Orchestration
- **Multi-Agent System**: 4 specialized agents + ManagerAgent coordinator
  - `ManagerAgent`: Weighted voting aggregation, pipeline orchestration
  - `ResearchAgent`: Market data fetching, ML predictions, analysis reports
  - `RiskAgent`: Portfolio concentration checks, exposure limits
  - `ExecutionAgent`: Smart order routing, slippage optimization
- **Agent Tools**: 3 new MCP tools
  - `run_analysis_pipeline(symbol, sentiment_score)`: Trigger full agent swarm
  - `get_agent_status()`: Check all agents' current state
  - `set_auto_execute(enabled)`: Toggle automatic trade execution
- **Agent Communication**: `AgentContext` and `AgentDecision` dataclasses for inter-agent messaging
- **Test Suite**: `tests/test_agents.py` - Comprehensive agent pipeline verification

### Changed
- **Exchange Tools**: Enhanced error handling with debug logging for firewall issues
  - Added stderr logging for troubleshooting network blocking
  - Increased timeout from 10s to 30s for exchange API calls
  - Fixed circular import in `tools/agent_tools.py` with lazy imports

### Fixed
- **Firewall Compatibility**: Resolved `ExchangeNotAvailable` errors in Claude Desktop
  - Root cause: Windows Firewall blocking Python subprocess HTTPS requests
  - Solution: Added firewall rule instructions in README
- **Circular Import**: Fixed import dependency between `agents` and `tools` packages
  - Changed to lazy imports in `tools/agent_tools.py`

---

## [1.24.0] - 2026-01-15

### Added - Phase 14: Interactive Dashboard
- **Streamlit Dashboard**: `dashboard.py` with 4 tabs
  - Market Intel: Live price, 24h change, orderbook depth chart
  - Deep Brain: Agent reasoning, ML signals, microstructure features
  - Execution & Risk: Portfolio balance, positions, risk limits
  - Alerts: Alert history with timestamps
- **Dependencies**: Added `streamlit` and `plotly` to requirements

### Changed
- **Tool Refactoring**: Moved all tool functions to module scope
  - `exchange_tools.py`: `fetch_orderbook`, `fetch_ticker` now importable
  - `strategy_tools.py`: `get_trading_signal` exposed at module level
  - `trading_tools.py`: `execute_order`, `get_positions` made accessible
  - `alert_tools.py`: Alert functions moved to module scope
- **Shared Library Pattern**: Dashboard can directly import core/tool functions

---

## [1.23.0] - 2026-01-14

### Added - Phase 13: Strategy Engine
- **Strategy Orchestration**: `core/strategy_engine.py`
  - Multi-signal aggregation (ML + Sentiment + Risk/Reward)
  - Weighted confidence scoring
  - Final Buy/Sell/Hold decision logic
- **Strategy Tools**: `tools/strategy_tools.py`
  - `get_trading_signal(symbol, sentiment_score)`: Aggregated trading signal
- **Dependencies**: Added `onnxruntime` for ML inference
- **Test Suite**: `tests/test_strategy.py`

---

## [1.22.0] - 2026-01-13

### Added - Phase 12: Execution Engine
- **Risk Engine**: `core/risk_engine.py`
  - Pre-trade checks: max trade size, daily loss limits
  - Position concentration validation
  - Restricted assets blacklist
- **Paper Trading**: `tools/trading_tools.py`
  - Mock order execution with price validation
  - Portfolio state management (in-memory)
  - Position tracking with P&L
- **Test Suite**: `tests/test_execution.py`

---

## [1.21.0] - 2026-01-12

### Added - Phase 11: Persistence Layer
- **Database**: `core/database.py`
  - SQLite schema for alerts, market data, portfolios
  - Async operations with `aiosqlite`
  - Automatic table creation on startup
- **Alert Persistence**: Updated `alert_tools.py` to use DB
- **Background Service**: Updated to log alerts to database
- **Dependency**: Added `aiosqlite`
- **Test Suite**: `tests/test_persistence.py`

---

## [1.20.0] - 2026-01-11

### Added - Phase 10: Smart Notifications
- **Background Service**: `core/background_service.py`
  - Persistent monitoring loop for price alerts
  - Integrated into `market_server.py` startup
- **Alert Tools**: `tools/alert_tools.py`
  - `create_price_alert`, `check_alerts`, `mark_alerts_read`
- **Test Suite**: `tests/test_alert_tools.py`

---

## [1.19.0] - 2026-01-10

### Added - Phase 9: Portfolio & Risk Intelligence
- **Portfolio Tools**: `tools/portfolio_tools.py`
  - `analyze_portfolio_risk`: Concentration, volatility, VaR scoring
  - `simulate_slippage`: Market impact estimation for large orders
- **Test Suite**: `tests/test_portfolio_tools.py`

---

## [1.18.0] - 2026-01-09

### Added - Phase 8: AI Prediction Engine
- **DeepLOB Lite**: `core/ml_models.py`
  - Lightweight price direction prediction
  - Order Flow Imbalance (OFI) based features
  - Mock model (no actual training)
- **ML Tools**: `tools/ml_tools.py`
  - `predict_price_direction(symbol, exchange)`
- **Test Suite**: `tests/test_ml_prediction.py`

---

## [1.17.0] - 2026-01-08

### Added - Phase 7: Exchange Connectivity
- **CCXT Integration**: `tools/exchange_tools.py`
  - `fetch_orderbook`: Live L2 data from 6+ exchanges
  - `fetch_ticker`: Price, volume, 24h change
  - `list_supported_exchanges`
- **Dependencies**: Added `ccxt`, `numpy`
- **Test Suite**: `tests/test_exchange_tools.py` (with mocking)

---

## [1.16.0] - 2026-01-07

### Added - Phase 5: MCP Prompts
- **Prompt Templates**: `prompts/market_prompts.py`
  - `daily_briefing`: Market summary for a symbol
  - `analyze_liquidity`: Liquidity and slippage analysis
  - `hunt_anomalies`: Manipulation detection

---

## [1.15.0] - 2026-01-06

### Added - Phase 4: External API Integration
- **Sentiment Tools**: `tools/sentiment_tools.py`
  - `get_fear_greed_index`: Fear & Greed Index (Alternative.me)
- **DeFi Tools**: `tools/defi_tools.py`
  - `get_defi_tvl`: DeFi protocol TVL (DeFi Llama)
  - `get_gas_price`: Ethereum gas tracker (Etherscan stub)
- **Dependencies**: Added `httpx`, `cachetools`
- **Test Suite**: `tests/test_external_apis.py`

---

## [1.14.0] - 2026-01-05

### Added - Phase 3: Anomaly Detection
- **Anomaly Detection**: `core/anomaly_detection.py`
  - Spoofing detection logic
  - Layering detection logic
  - Market regime classification
- **Anomaly Tools**: `tools/anomaly_tools.py`
  - `detect_spoofing`, `detect_layering`, `classify_market_regime`

---

## [1.13.0] - 2026-01-04

### Added - Phase 2: Core Analytics
- **Analytics Engine**: `core/analytics.py`
  - Microstructure calculations (OFI, OBI, Microprice, VPIN)
  - Ported from Genesis2025
- **Data Validator**: `core/data_validator.py`
  - Order book validation utilities
- **Microstructure Tools**: `tools/microstructure_tools.py`
  - `calculate_microstructure_features`, `analyze_orderbook`
- **Price Tools**: `tools/price_tools.py`
  - `get_crypto_price`, `analyze_spread`
- **Test Suite**: `tests/test_core_analytics.py`

---

## [1.12.0] - 2026-01-03

### Added - Phase 1: Project Setup
- **Project Structure**: Created clean directory layout
  - `core/`, `tools/`, `prompts/`, `tests/`
- **MCP Server**: `market_server.py` entry point
- **Dependencies**: `requirements.txt` with MCP, FastMCP, pydantic
- **Git**: Initialized repository with `.gitignore`

---

## Format
- **[Version]** - Date
- **Added**: New features
- **Changed**: Changes to existing functionality
- **Deprecated**: Soon-to-be removed features
- **Removed**: Removed features
- **Fixed**: Bug fixes
- **Security**: Vulnerability patches
