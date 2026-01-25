# Dashboard Guide - Market Intelligence MCP Server

## Overview

The interactive Streamlit dashboard provides a real-time UI for market analysis, agent monitoring, and risk management.

![Dashboard Preview](https://via.placeholder.com/800x400?text=Dashboard+Preview)

---

## Launching the Dashboard

```bash
cd Market-MCP-Test
streamlit run dashboard.py
```

**Access:** http://localhost:8501

---

## Dashboard Tabs

### 1. 📊 Market Intel

**Features:**
- **Live Price Display**: Current BTC/USDT price
- **24h Change**: Price movement percentage
- **Orderbook Depth Chart**: Bid/ask visualization
- **Volume Analysis**: 24h trading volume

**Data Source:** Direct Binance API (real-time)

**Refresh:** Auto-updates every 30 seconds

---

### 2. 🧠 Deep Brain

**Purpose:** ML predictions and market microstructure analysis

**Displays:**
- **ML Signal**: DeepLOB-Lite buy/sell/hold prediction
- **Confidence Score**: Model confidence (0-1)
- **Agent Reasoning**: Research agent analysis breakdown
- **Microstructure Features**:
  - Order Flow Imbalance (OFI)
  - Order Book Imbalance (OBI)
  - Microprice
  - VPIN score
  - Spread (basis points)

**Use Case:** Understanding WHY the model recommends an action

---

### 3. ⚡ Execution & Risk

**Components:**

**Portfolio Balance:**
- Total USDT balance
- Buying power
- Locked funds

**Active Positions:**
- Symbol, size, entry price
- Current P&L
- Position age

**Risk Limits:**
- Max trade size
- Daily loss limit
- Position concentration

**Purpose:** Monitor paper trading and risk exposure

---

### 4. 🔔 Alerts

**Alert History:**
- Alert type (price above/below)
- Target price
- Triggered timestamp
- Status (active/triggered/read)

**Actions:**
- Mark alerts as read
- View alert details
- Filter by status

---

## Customization

### Changing Refresh Rate

Edit `dashboard.py`:
```python
st_autorefresh(interval=30000, key="datarefresh")  # 30 seconds
```

Change `30000` to desired milliseconds

### Adding Custom Metrics

```python
# In dashboard.py
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Custom Metric", value, delta)
```

### Switching Symbols

Currently hardcoded to BTC/USDT. To change:

```python
# Line ~50 in dashboard.py
symbol = "ETH/USDT"  # Change from BTC/USDT
```

---

## Troubleshooting

### Dashboard won't start

**Error:** `ModuleNotFoundError: No module named 'streamlit'`

**Fix:**
```bash
pip install -r requirements.txt
```

### No data showing

**Error:** "Failed to fetch orderbook"

**Fix:**
1. Check internet connection
2. Verify exchange API is reachable:
   ```bash
   curl https://api.binance.com/api/v3/depth?symbol=BTCUSDT&limit=5
   ```
3. Try fallback exchange (edit `dashboard.py` Line ~52)

### Slow performance

**Solution:**
```bash
streamlit cache clear
```

Then restart dashboard

---

## Advanced Usage

### Running on Custom Port

```bash
streamlit run dashboard.py --server.port 8080
```

### Headless Mode (No Browser)

```bash
streamlit run dashboard.py --server.headless true
```

### Public Access (LAN)

```bash
streamlit run dashboard.py --server.address 0.0.0.0
```

Access from other devices: `http://<your-ip>:8501`

---

## Dashboard Architecture

```
Dashboard (Streamlit)
  ├─ Tab 1: Market Intel
  │    ├─ fetch_orderbook()
  │    ├─ fetch_ticker()
  │    └─ Plotly depth chart
  │
  ├─ Tab 2: Deep Brain
  │    ├─ predict_price_direction()
  │    ├─ calculate_microstructure_features()
  │    └─ Agent pipeline display
  │
  ├─ Tab 3: Execution & Risk
  │    ├─ get_balance()
  │    ├─ get_positions()
  │    └─ Risk limit display
  │
  └─ Tab 4: Alerts
       ├─ fetch_alerts()
       └─ mark_alerts_read()
```

**All functions** come from `tools/` and `core/` modules (shared with MCP)

---

## Screenshots

### Market Intel Tab
- Live orderbook visualization
- Candlestick charts (Plotly)
- Volume bars

### Deep Brain Tab
- ML prediction confidence meter
- Feature importance chart
- Agent decision breakdown

### Execution Tab
- Position table
- Balance pie chart
- Risk gauge

---

## Future Enhancements

**Planned:**
- Multi-symbol support (dropdown)
- Historical backtesting UI
- Custom strategy builder
- Alert creation form
- WebSocket live streaming toggle

---

## Integration with Claude Desktop

The dashboard and Claude Desktop **share the same codebase**.

**Tools used in dashboard:**
- `fetch_orderbook()`
- `fetch_ticker()`
- `predict_price_direction()`
- `get_trading_signal()`

**Same tools available in Claude:**
```
"Show me the orderbook for BTC/USDT"
"Predict price direction for ETH/USDT"
"Get a trading signal for BTC/USDT with sentiment 0.7"
```

**Benefit:** Test features visually in dashboard, then use in Claude workflows!
