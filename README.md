# Market Intelligence MCP Server

A comprehensive market analysis server merging advanced HFT analytics from Genesis2025 with broad market intelligence tools.

This MCP server provides a suite of tools for **crypto price tracking, market sentiment analysis, DeFi statistics, and professional-grade order book microstructure analysis** (OFI, Microprice, Spoofing Detection).

## Features

### 1. Core Market Data
- **Prices**: Real-time crypto prices, market cap, and volume (`get_crypto_price`).
- **Details**: Comprehensive asset metadata and links (`get_coin_details`).
- **History**: Historical OHLC price data (`get_historical_prices`).
- **Trends**: Top 7 trending coins on CoinGecko (`get_trending_coins`).
- **Global**: Global market cap and dominance metrics (`get_global_market_data`).

### 2. Microstructure Analytics (HFT)
*Adapted from Genesis2025 Engine*
- **Order Book Analysis**: Calculate Order Flow Imbalance (OFI) and Order Book Imbalance (OBI) (`analyze_orderbook`).
- **Microprice**: Compute volume-weighted fair price (`calculate_microprice`).
- **Spread Analysis**: Analyze bid-ask spread and liquidity (`analyze_bid_ask_spread`).

### 3. Anomaly Detection & Surveillance
*Professional Grade Market Surveillance*
- **Spoofing Detection**: Identify potential spoofing/layering attempts (`detect_spoofing`).
- **Liquidity Gaps**: Detect dangerous thin liquidity levels (`detect_liquidity_gaps`).
- **Market Regime**: Classify market state (Calm, Stressed, Manipulation Suspected) (`get_market_regime`).
- **Full Scan**: Comprehensive anomaly scan (`detect_anomalies`).

### 4. External Intelligence
- **Sentiment**: Crypto Fear & Greed Index (`get_fear_and_greed_index`).
- **DeFi**: Total Value Locked (TVL) and protocol stats (`get_defi_global_stats`, `get_protocol_tvl`).
- **On-Chain**: Ethereum gas tracking (`get_gas_price`).

### 5. Exchange & AI (New)
- **Live Data**: Fetch real-time order books/tickers from Binance/Kraken (`fetch_orderbook`, `fetch_ticker`).
- **AI Prediction**: Predict price direction using DeepLOB logic (`predict_price_direction`).
- **Volatility**: Analyze volatility regimes (`analyze_volatility_regime`).

### 6. Portfolio Intelligence (New)
- **Risk Analysis**: Score portfolios on concentration and volatility (`analyze_portfolio_risk`).
- **Execution Simulator**: Estimate slippage for large trades (`simulate_slippage`).

### 7. Smart Notifications (New)
- **Background Monitor**: Light-weight service checking market conditions.
- **Alerts**: Create and check alerts (`create_price_alert`, `check_alerts`).

## Prerequisites

- Python 3.10+
- **CoinGecko API Key** (Demo/Free key works).
- **Etherscan API Key** (Optional, for live gas tracking).

## Setup

1. **Create Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment**:
   Create a `.env` file in the project root:
   ```env
   CRYPTO_API_KEY=your_coingecko_key
   ETHERSCAN_API_KEY=your_etherscan_key  # Optional
   ```

## Configuration for Claude Desktop

Add to `%APPDATA%\Claude\claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "market-intelligence": {
      "command": "python",
      "args": ["S:\\Market-MCP\\Market-MCP-Test\\market_server.py"],
      "env": {
        "CRYPTO_API_KEY": "your_key_here",
        "ETHERSCAN_API_KEY": "optional_key_here"
      }
    }
  }
}
```

## Running Manually

```bash
python market_server.py
```

## Testing

Run the verification suite:
```bash
# Test Core Analysis Logic
python tests/test_phase1_2.py

# Test External APIs (Mocked)
python tests/test_phase4.py

# Test Full Integration
python tests/test_integration.py
```
