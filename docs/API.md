# API Reference - Market Intelligence MCP Server

## Overview

The Market Intelligence MCP Server exposes **30+ tools** for crypto market analysis, trading strategies, and multi-agent orchestration.

---

## Exchange Tools

### `fetch_orderbook`

Fetch real-time Level 2 orderbook data with multi-exchange fallback.

**Parameters:**
- `symbol` (string): Trading pair (e.g., 'BTC/USDT')
- `exchange` (string, optional): Exchange name (default: 'binance')
- `limit` (int, optional): Order book depth (default: 20)
- `fallback` (bool, optional): Enable fallback (default: true)

**Returns:**
```json
{
  "symbol": "BTC/USDT",
  "exchange": "binance",
  "bids": [[88360.79, 0.5], [88360.0, 1.2], ...],
  "asks": [[88361.0, 0.3], [88361.5, 0.8], ...],
  "timestamp": "2026-01-25T15:00:00",
  "fallback_used": false
}
```

**Example:**
```python
import asyncio
from tools.exchange_tools import fetch_orderbook

result = asyncio.run(fetch_orderbook('ETH/USDT', 'kraken', 10))
```

---

### `fetch_ticker`

Fetch 24-hour ticker statistics.

**Parameters:**
- `symbol` (string): Trading pair
- `exchange` (string, optional): Exchange (default: 'binance')

**Returns:**
```json
{
  "symbol": "BTC/USDT",
  "last_price": 88360.79,
  "volume_24h": 12345.67,
  "high_24h": 89000.0,
  "low_24h": 87500.0,
  "price_change_percent_24h": 2.34
}
```

---

### `list_supported_exchanges`

List available exchanges.

**Returns:**
```json
{
  "recommended": ["binance", "kraken", "coinbase"],
  "total_count": 3
}
```

---

## Analytics Tools

### `calculate_microstructure_features`

Calculate market microstructure indicators.

**Parameters:**
- `orderbook_json` (string): JSON orderbook data

**Returns:**
```json
{
  "ofi": 0.234,
  "obi": -0.123,
  "microprice": 88360.85,
  "vpin": 0.456,
  "spread_bps": 1.2
}
```

---

### `analyze_orderbook`

Comprehensive orderbook analysis.

**Parameters:**
- `orderbook_json` (string): JSON orderbook data

**Returns:**
```json
{
  "depth_imbalance": 0.15,
  "total_bid_volume": 1234.56,
  "total_ask_volume": 987.65,
  "weighted_mid_price": 88360.82,
  "liquidity_score": 8.5
}
```

---

## ML & Prediction Tools

### `predict_price_direction`

ML-based price direction prediction.

**Parameters:**
- `symbol` (string): Trading pair
- `exchange` (string, optional): Exchange

**Returns:**
```json
{
  "prediction": "buy",
  "confidence": 0.78,
  "features": {...},
  "model": "DeepLOB-Lite"
}
```

---

## Strategy Tools

### `get_trading_signal`

Aggregated trading signal from multiple sources.

**Parameters:**
- `symbol` (string): Trading pair
- `sentiment_score` (float): Market sentiment (-1 to 1)

**Returns:**
```json
{
  "signal": "BUY",
  "confidence": 0.85,
  "components": {
    "ml_signal": "buy",
    "sentiment": 0.7,
    "risk_reward": 3.5
  }
}
```

---

## Agent Tools

### `run_analysis_pipeline`

Execute full multi-agent analysis.

**Parameters:**
- `symbol` (string): Trading pair
- `sentiment_score` (float): Sentiment (-1 to 1)

**Returns:**
```json
{
  "final_decision": "BUY",
  "confidence": 0.82,
  "agents": {
    "research": {...},
    "risk": {...},
    "execution": {...}
  }
}
```

### `get_agent_status`

Check agent system status.

**Returns:**
```json
{
  "manager": "ready",
  "research": "ready",
  "risk": "ready",
  "execution": "ready",
  "auto_execute": false
}
```

---

## WebSocket Streaming Tools

### `subscribe_orderbook_stream`

Subscribe to real-time orderbook updates.

**Parameters:**
- `symbol` (string): Trading pair
- `exchange` (string, optional): Exchange

**Returns:**
```json
{
  "stream_id": "binance_btcusdt_orderbook",
  "status": "connected",
  "symbol": "BTC/USDT"
}
```

### `stop_stream`

Stop an active WebSocket stream.

**Parameters:**
- `stream_id` (string): Stream identifier

---

## Alert Tools

### `create_price_alert`

Create price alert notification.

**Parameters:**
- `symbol` (string): Trading pair
- `target_price` (float): Alert price
- `condition` (string): 'above' or 'below'

**Returns:**
```json
{
  "alert_id": "alert_123",
  "status": "active"
}
```

---

## Portfolio Tools

### `analyze_portfolio_risk`

Calculate portfolio risk metrics.

**Parameters:**
- `positions` (array): List of positions

**Returns:**
```json
{
  "concentration_risk": 0.45,
  "var_95": 1234.56,
  "volatility": 0.23
}
```

---

## Full Tool List

| Category | Tools |
|----------|-------|
| **Exchange** | fetch_orderbook, fetch_ticker, list_supported_exchanges |
| **Analytics** | calculate_microstructure_features, analyze_orderbook, analyze_spread |
| **ML & Prediction** | predict_price_direction |
| **Strategy** | get_trading_signal |
| **Trading** | execute_order, get_positions, get_balance |
| **Risk** | analyze_portfolio_risk, simulate_slippage |
| **Agents** | run_analysis_pipeline, get_agent_status, set_auto_execute |
| **Alerts** | create_price_alert, check_alerts, mark_alerts_read |
| **Sentiment** | get_fear_greed_index |
| **Anomaly** | detect_spoofing, detect_layering, classify_market_regime |
| **Streaming** | subscribe_orderbook_stream, subscribe_ticker_stream, stop_stream, list_active_streams, check_stream_health |

**Total:** 30+ tools across 11 categories
