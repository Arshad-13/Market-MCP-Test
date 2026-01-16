# Market Intelligence MCP Server - Strategic Roadmap (2026)

## Current Standing
We have successfully built a **Professional-Grade Analytics Engine**.
- **Strengths**: Unique features like "Spoofing Detection", "Microprice", and "Fear & Greed" set this server apart from simple price-fetchers.
- **Weaknesses**: The HFT tools (`analyze_orderbook`, `detect_anomalies`) currently require the user/LLM to provide raw bid/ask arrays. **Geting this data into the prompt is difficult**, making these powerful tools hard to use in a real chat workflow.

To become "Unique and Best-in-Class", we must bridge the gap between our *Analytics Engine* and *Real-World Data*.

---

## Phase 7: Real-Time Exchange Connectivity (The "Fuel" Phase) ✅
*Enable the HFT tools to work autonomously by fetching live L2 order book data.*

- [x] **Integration**: Add `ccxt` library for universal exchange support (Binance, Kraken, Coinbase).
- [x] **New Tools**:
    - `fetch_orderbook(symbol, exchange, depth)`: Returns processed book ready for `analyze_orderbook`.
    - `fetch_ticker_batch(symbols)`: Efficient multi-asset monitoring.
- **Outcome**: User says *"Check BTC for spoofing"* -> Server fetches book -> Server analyzes book -> Server reports result. (Currently: User must paste book data).

---

## Phase 8: AI & Machine Learning Integration (The "Brain" Phase) ✅
*Deploy Genesis2025's DeepLOB model for predictive intelligence.*

- [x] **Model Porting**: Convert Genesis PyTorch/ONNX models for lightweight inference.
- [x] **New Tools**:
    - `predict_price_direction(symbol)`: Uses order book shape to predict short-term moves (Up/Down/Neutral).
    - `analyze_volatility_regime(history)`: ML-based clustering of volatility states.
- **Outcome**: True "Agentic" capability where the server predicts movements, not just reports past data.

---

## Phase 9: Portfolio & Risk Intelligence (The "Personal" Phase) ✅
*Make the insights actionable for the specific user.*

- [x] **New Tools**:
    - `analyze_portfolio_risk(holdings)`: Calculates risk score based on concentration and volatility.
    - `simulate_slippage(size, symbol)`: Estimates execution cost for large trades.

---

## Phase 10: Smart Notifications & Background Services
*Proactive intelligence.*

- [ ] **Alerts**: Resources that update on specific triggers (e.g., "Whale Alert", "Spoofing Detected").
- [ ] **Background Loop**: A simplified background thread that scans top assets periodically.

---

## Recommendation
**Prioritize Phase 7 immediately.** Without live order book fetching, the advanced analytics we built in Phase 2 & 3 are "engines without fuel." Phase 7 unlocks their true potential.
