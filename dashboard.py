"""
Market Intelligence Dashboard (Phase 14)

A Streamlit-based UI for the Market Intelligence Agent.
Visualizes:
1. Market Data (Price, Orderbook, OFI)
2. Strategy Internals (ML Confidence, Signals)
3. Execution & Risk (Positions, Limits)
4. Alert History

Run with: streamlit run dashboard.py
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import asyncio
import json
from datetime import datetime
import time

# Import Core Logic (Shared Library)
# Note: These are now module-level functions we can import directly!
from tools.exchange_tools import fetch_ticker, fetch_orderbook
from tools.strategy_tools import get_trading_signal
from tools.trading_tools import get_positions
from tools.alert_tools import check_alerts
from core.risk_engine import risk_engine

# Page Config
st.set_page_config(
    page_title="Market Intelligence Agent",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern look
st.markdown("""
<style>
    .metric-card {
        background-color: #0e1117;
        border-radius: 10px;
        padding: 20px;
        border: 1px solid #30333d;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 4px 4px 0px 0px;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Utils
def run_async(coro):
    """Helper to run async tools in Streamlit."""
    return asyncio.run(coro)

# --- Sidebar ---
st.sidebar.title("🧠 Agent Controls")
symbol = st.sidebar.text_input("Symbol", value="BTC/USDT").upper()
refresh_rate = st.sidebar.slider("Refresh Rate (s)", 5, 60, 10, key="refresh")
auto_refresh = st.sidebar.checkbox("Auto-Refresh", value=False)

if auto_refresh:
    time.sleep(refresh_rate)
    st.rerun()

if st.sidebar.button("Manual Refresh"):
    st.rerun()

st.sidebar.markdown("---")
# Status Indicators
st.sidebar.success("Agent: **ONLINE**")
st.sidebar.info("Mode: **PAPER TRADING**")
st.sidebar.warning("Risk Engine: **ACTIVE**")

# --- Main Layout ---
col_head_1, col_head_2 = st.columns([3, 1])

# Fetch Data Wrapper
try:
    # 1. Ticker
    ticker_json = run_async(fetch_ticker(symbol))
    ticker = json.loads(ticker_json)
    if "error" in ticker:
        st.error(f"Error: {ticker['details']}")
        st.stop()
        
    price = float(ticker.get("last_price", 0))
    change = float(ticker.get("percentage_change", 0))
    
    with col_head_1:
        st.title(f"{symbol} · ${price:,.2f}")
    with col_head_2:
        st.metric("24h Change", f"{change:.2f}%", delta=f"{change:.2f}%")

    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Market Intel", "🧠 Deep Brain", "🛡️ Execution & Risk", "🔔 Alerts"])

    # --- Tab 1: Market Intel ---
    with tab1:
        st.subheader("Microstructure Analysis")
        
        # Orderbook Data
        ob_json = run_async(fetch_orderbook(symbol))
        ob = json.loads(ob_json)
        bids = ob.get("bids", [])
        asks = ob.get("asks", [])
        
        # Calculate OFI/Metrics (We need logic here or call a tool)
        # Using MicrostructureAnalyzer directly from core?
        # Ideally dashboard should be dumb. 
        # But for visual, let's just plot the book.
        
        col_chart_1, col_chart_2 = st.columns(2)
        
        with col_chart_1:
            st.markdown("#### Order Book Depth")
            # Simple Bid/Ask Plot
            if bids and asks:
                bid_prices = [p[0] for p in bids[:20]]
                bid_sizes = [p[1] for p in bids[:20]]
                ask_prices = [p[0] for p in asks[:20]]
                ask_sizes = [p[1] for p in asks[:20]]
                
                fig = go.Figure()
                fig.add_trace(go.Bar(x=bid_prices, y=bid_sizes, name='Bids', marker_color='green'))
                fig.add_trace(go.Bar(x=ask_prices, y=ask_sizes, name='Asks', marker_color='red'))
                fig.update_layout(title="Depth (Top 20)", barmode='overlay', height=400)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No Orderbook Data")

        with col_chart_2:
            st.markdown("#### Exchange Data")
            st.json(ticker) # Raw view for verification

    # --- Tab 2: Strategy ---
    with tab2:
        st.subheader("Agent Reasoning")
        
        # Get Signal
        sentiment_score = 50.0 # Placeholder or fetch from somewhere
        signal_json = get_trading_signal(symbol, bids, asks, sentiment_score) # This is sync now?
        # Wait, strategy_tools uses `strategy_engine.generate_signal` which is sync.
        # So `get_trading_signal` is sync.
        signal = json.loads(signal_json)
        
        # Display Signal
        col_sig, col_conf = st.columns(2)
        
        with col_sig:
            action = signal["action"] # BUY, SELL, HOLD
            color = "green" if action == "BUY" else "red" if action == "SELL" else "gray"
            st.markdown(f"<h1 style='text-align: center; color: {color};'>{action}</h1>", unsafe_allow_html=True)
            st.caption(f"Reason: {signal['reason']}")
            
        with col_conf:
            conf = signal["confidence"]
            st.metric("Model Confidence", f"{conf*100:.1f}%")
            st.progress(conf)
            
        st.markdown("---")
        st.markdown("#### ML Features (DeepLOB Lite)")
        
        ml_res = signal.get("ml_signal", {})
        features = ml_res.get("features", {})
        probs = ml_res.get("probabilities", {})
        
        c1, c2, c3 = st.columns(3)
        c1.metric("OFI", f"{features.get('ofi', 0):.4f}")
        c2.metric("OBI", f"{features.get('obi', 0):.4f}")
        c3.metric("Microprice Div", f"{features.get('microprice_div', 0):.6f}")
        
        # Probabilities Chart
        probs_df = pd.DataFrame([probs]).T
        probs_df.columns = ["Probability"]
        st.bar_chart(probs_df)

    # --- Tab 3: Execution ---
    with tab3:
        st.subheader("Paper Trading Portfolio")
        
        pos_json = get_positions()
        pos_data = json.loads(pos_json)
        
        st.metric("Paper Balance", f"${pos_data.get('balance_usd', 0):,.2f}")
        
        positions = pos_data.get("positions", {})
        if positions:
            st.table(pd.DataFrame(list(positions.items()), columns=["Asset", "Quantity"]))
        else:
            st.info("No active positions.")
            
        st.markdown("---")
        st.subheader("Risk Engine Limits")
        st.write(f"**Max Trade Size:** ${risk_engine.MAX_TRADE_SIZE_USD:,.0f}")
        st.write(f"**Max Daily Loss:** ${risk_engine.MAX_DAILY_LOSS_USD:,.0f}")
        st.write(f"**Restricted Assets:** {', '.join(risk_engine.RESTRICTED_ASSETS)}")

    # --- Tab 4: Alerts ---
    with tab4:
        st.subheader("System Alerts")
        
        alerts_json = run_async(check_alerts(unread_only=False))
        alerts_data = json.loads(alerts_json)
        alerts_list = alerts_data.get("alerts", [])
        
        if alerts_list:
            df = pd.DataFrame(alerts_list)
            # Reorder columns
            if not df.empty and "timestamp" in df.columns:
                df = df[["timestamp", "severity", "symbol", "message", "is_read"]]
                st.dataframe(df.style.applymap(lambda v: "color: red;" if v == "CRITICAL" else None, subset=["severity"]))
        else:
            st.info("No alerts found.")

except Exception as e:
    st.error(f"Dashboard Error: {e}")
    # Print traceback in expaneder
    import traceback
    st.expander("Traceback").code(traceback.format_exc())

