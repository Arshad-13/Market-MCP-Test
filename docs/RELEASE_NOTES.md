# Update CHANGELOG with recent features
# Version 1.27.0 - 2026-01-25

## [1.27.0] - 2026-01-25 - PUBLIC RELEASE

### Added - Autonomous Trading & Capital Management
- **Autonomous Trade Execution**: `autonomous_trade(symbol, sentiment, position_size)`
  - One-command market analysis + execution
  - Multi-agent pipeline (Research, Risk, Execution)
  - Confidence threshold (70%) before execution
  - Full audit trail with analysis breakdown
- **Capital Management Tools**: 4 new MCP tools
  - `get_balance()`: Current balance with P&L summary
  - `reset_balance()`: Reset to $1M, clear positions
  - `set_balance(amount)`: Set custom starting capital
  - `get_pnl_report()`: Comprehensive profit/loss analysis

### Changed - Production Ready
- **Direct HTTP APIs**: Complete CCXT removal
  - Faster initialization (no market loading)
  - More reliable (fewer dependencies)
  - Works in all environments
- **Comprehensive Documentation**: 1,500+ lines
  - Professional README with badges
  - Installation, API, Architecture guides
  - Dashboard usage documentation
  - Contributing guidelines

### Fixed
- Async event loop error in autonomous_trade
- Dashboard ticker fetch error (removed CCXT dependency)
- MCP server print statements breaking JSON-RPC

### Security
- Paper trading only (safe for testing)
- Risk limits enforced
- No real money integration

---
