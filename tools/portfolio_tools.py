"""
Portfolio & Risk Intelligence Tools

MCP tools for portfolio analysis, risk scoring, and execution simulation.
"""

import json
from typing import List, Dict, Any, Optional
from datetime import datetime

from mcp.server.fastmcp import FastMCP

# Simple VaR assumptions for now (since we don't have full historical covariance matrix engine yet)
# In a real system, this would call a risk engine.
DEFAULT_CONFIDENCE_LEVEL = 0.95

def register_portfolio_tools(mcp: FastMCP) -> None:
    """
    Register Portfolio Intelligence MCP tools.
    
    Args:
        mcp: FastMCP server instance
    """
    
    @mcp.tool()
    def analyze_portfolio_risk(
        holdings: List[Dict[str, Any]]
    ) -> str:
        """
        Analyze the risk profile of a cryptocurrency portfolio.
        
        Calculates distinct risk scores based on asset allocation, concentration,
        and estimated volatility.
        
        Args:
            holdings: List of dicts, e.g., [{"symbol": "BTC", "amount": 0.5, "price_usd": 50000}, ...]
            
        Returns:
            JSON string with risk assessment (Scores 0-100, where 100 is Max Risk).
        """
        total_value = 0.0
        weighted_vol_sum = 0.0
        
        # Volatility heuristics (annualized std dev estimates) if real data missing
        # In Phase 10 we might fetch this live.
        BASE_VOLATILITIES = {
            "BTC": 0.60,
            "ETH": 0.80,
            "SOL": 0.95,
            "STABLE": 0.01  # USDC, USDT
        }
        DEFAULT_VOL = 1.00 # High vol for unknown alts
        
        for asset in holdings:
            sym = asset.get("symbol", "UNKNOWN").upper()
            amt = float(asset.get("amount", 0))
            price = float(asset.get("price_usd", 0))
            
            val = amt * price
            total_value += val
            
            # Determine vol estimate
            if "USD" in sym and ("T" in sym or "C" in sym):
                 vol = BASE_VOLATILITIES["STABLE"]
            else:
                 vol = BASE_VOLATILITIES.get(sym, DEFAULT_VOL)
            
            weighted_vol_sum += (val * vol)

        if total_value <= 0:
            return json.dumps({"error": "Total portfolio value is zero or negative"})

        # 1. Concentration Risk (HHI Index concept simplified)
        # If 100% in one asset -> Risk 100.
        concentration_score = 0.0
        for asset in holdings:
            val = float(asset.get("amount", 0)) * float(asset.get("price_usd", 0))
            weight = val / total_value
            concentration_score += (weight ** 2)
        
        concentration_risk = min(100, concentration_score * 100)
        
        # 2. Volatility Risk (Weighted Average Volatility scaled)
        # Scale: 0.0 - 1.5 => 0 - 100
        avg_vol = weighted_vol_sum / total_value
        volatility_risk = min(100, (avg_vol / 1.5) * 100)
        
        # 3. Overall Risk Score
        overall_score = (concentration_risk * 0.4) + (volatility_risk * 0.6)
        
        risk_level = "Low" if overall_score < 30 else "Medium" if overall_score < 60 else "High" if overall_score < 85 else "Extreme"
        
        return json.dumps({
            "total_value_usd": round(total_value, 2),
            "risk_score_0_to_100": round(overall_score, 1),
            "risk_level": risk_level,
            "components": {
                "concentration_risk": round(concentration_risk, 1),
                "volatility_risk": round(volatility_risk, 1)
            },
            "estimated_annual_volatility": round(avg_vol, 2),
            "timestamp": datetime.now().isoformat()
        })

    @mcp.tool()
    def simulate_slippage(
        symbol: str,
        trade_size_usd: float,
        current_liquidity_usd: float = 100000.0, # Approximate depth +/- 2%
    ) -> str:
        """
        Estimate price impact (slippage) for a large trade.
        
        Uses a square-root market impact model.
        
        Args:
            symbol: Asset symbol.
            trade_size_usd: Size of the trade in USD.
            current_liquidity_usd: Estimated available liquidity (depth) at 2% range.
                                   If unknown, start with $100k or fetch via orderbook tools.
        
        Returns:
            JSON string with estimated slippage percentage and cost.
        """
        # Impact ~= k * sqrt(Trade Size / Liquidity)
        # We assume k=1 for this simplified model normalized to 2% depth
        # If Trade Size == Liquidity, we expect significant impact (~2% or more)
        
        ratio = trade_size_usd / current_liquidity_usd
        
        # Heuristic model
        # small trades: linear
        # large trades: exponential decay of price
        
        if ratio < 0.01:
            slippage_pct = 0.01 # Almost zero
        else:
            slippage_pct = 0.5 * (ratio ** 0.6) # Simplified impact curve
            
        estimated_price_change = min(99.0, slippage_pct) # Cap at 99%
        slippage_cost = trade_size_usd * (estimated_price_change / 100)
        
        # Warning levels
        warning = "Safe"
        if estimated_price_change > 1.0: warning = "Moderate Slippage"
        if estimated_price_change > 5.0: warning = "High Impact - Do not execute"
        
        return json.dumps({
            "symbol": symbol,
            "trade_size_usd": trade_size_usd,
            "estimated_slippage_pct": round(estimated_price_change, 3),
            "estimated_cost_usd": round(slippage_cost, 2),
            "warning_level": warning,
            "market_impact_score": round(min(10, estimated_price_change), 1),
            "timestamp": datetime.now().isoformat()
        })
