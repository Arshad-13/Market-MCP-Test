"""
Microstructure Analysis Tools

MCP tools for order book microstructure analysis.
Provides OFI, OBI, microprice, and spread metrics.
"""

from typing import List, Optional
import json
from datetime import datetime

from mcp.server.fastmcp import FastMCP

from core.analytics import (
    MicrostructureAnalyzer,
    OrderBook,
    OrderBookLevel,
    MicrostructureMetrics,
    analyze_spread
)
from core.data_validator import DataValidator, validate_order_book


# Global analyzer instance (stateful for OFI calculations)
_analyzer: Optional[MicrostructureAnalyzer] = None


def _get_analyzer() -> MicrostructureAnalyzer:
    """Get or create the global analyzer instance."""
    global _analyzer
    if _analyzer is None:
        _analyzer = MicrostructureAnalyzer()
    return _analyzer


def register_microstructure_tools(mcp: FastMCP) -> None:
    """
    Register microstructure analysis MCP tools.
    
    Args:
        mcp: FastMCP server instance
    """
    
    @mcp.tool()
    def analyze_orderbook(
        bids: List[List[float]],
        asks: List[List[float]],
        symbol: str = "UNKNOWN"
    ) -> str:
        """
        Analyze order book microstructure and calculate key metrics.
        
        Calculates:
        - Order Flow Imbalance (OFI): Measures buying/selling pressure
        - Order Book Imbalance (OBI): Volume-weighted bid/ask imbalance
        - Microprice: Volume-weighted fair price estimate
        - Spread metrics: Absolute and basis points
        - Depth analysis: Total depth and imbalance
        
        Args:
            bids: List of [price, volume] pairs for bids (highest first)
            asks: List of [price, volume] pairs for asks (lowest first)
            symbol: Optional symbol name for reference
            
        Returns:
            JSON string with comprehensive microstructure metrics
        """
        # Validate input
        is_valid, errors = validate_order_book(bids, asks)
        if not is_valid:
            return json.dumps({
                "error": "Invalid order book data",
                "details": errors,
                "valid": False
            })
        
        # Create OrderBook
        book = OrderBook.from_raw(bids, asks, datetime.now())
        
        # Analyze
        analyzer = _get_analyzer()
        metrics = analyzer.analyze(book)
        
        return json.dumps({
            "valid": True,
            "symbol": symbol,
            "metrics": {
                "mid_price": metrics.mid_price,
                "spread": metrics.spread,
                "spread_bps": metrics.spread_bps,
                "ofi": metrics.ofi,
                "obi": metrics.obi,
                "microprice": metrics.microprice,
                "microprice_divergence": metrics.microprice_divergence,
                "directional_probability": metrics.directional_probability,
                "total_bid_depth": metrics.total_bid_depth,
                "total_ask_depth": metrics.total_ask_depth,
                "depth_imbalance": metrics.depth_imbalance,
                "volatility": metrics.volatility
            },
            "interpretation": {
                "ofi_signal": "bullish" if metrics.ofi > 0.2 else "bearish" if metrics.ofi < -0.2 else "neutral",
                "obi_signal": "bid-heavy" if metrics.obi > 0.3 else "ask-heavy" if metrics.obi < -0.3 else "balanced",
                "price_pressure": "upward" if metrics.directional_probability > 55 else "downward" if metrics.directional_probability < 45 else "neutral"
            },
            "timestamp": datetime.now().isoformat()
        })
    
    @mcp.tool()
    def analyze_bid_ask_spread(bid_price: float, ask_price: float) -> str:
        """
        Compute spread metrics and liquidity classification.
        
        A simple tool for quick spread analysis without needing full order book.
        
        Args:
            bid_price: The highest price a buyer is willing to pay
            ask_price: The lowest price a seller is willing to accept
            
        Returns:
            JSON string with spread analysis and liquidity classification
        """
        result = analyze_spread(bid_price, ask_price)
        result["timestamp"] = datetime.now().isoformat()
        return json.dumps(result)
    
    @mcp.tool()
    def calculate_microprice(
        bid_price: float,
        bid_volume: float,
        ask_price: float,
        ask_volume: float
    ) -> str:
        """
        Calculate the volume-weighted microprice.
        
        Microprice provides a more accurate fair value estimate than simple
        mid-price by weighting each price by the OTHER side's volume.
        
        If there's more volume on the bid side, the microprice will be
        closer to the ask (price is likely to move up).
        
        Args:
            bid_price: Best bid price
            bid_volume: Best bid volume
            ask_price: Best ask price
            ask_volume: Best ask volume
            
        Returns:
            JSON string with microprice and related metrics
        """
        if bid_price >= ask_price:
            return json.dumps({
                "error": "Bid price must be less than ask price",
                "valid": False
            })
        
        total_volume = bid_volume + ask_volume
        if total_volume <= 0:
            return json.dumps({
                "error": "Volumes must be positive",
                "valid": False
            })
        
        mid_price = (bid_price + ask_price) / 2
        microprice = (bid_volume * ask_price + ask_volume * bid_price) / total_volume
        divergence = microprice - mid_price
        
        # Directional signal
        if divergence > 0:
            direction = "Price likely to move UP (more bid volume)"
        elif divergence < 0:
            direction = "Price likely to move DOWN (more ask volume)"
        else:
            direction = "Balanced (no directional bias)"
        
        return json.dumps({
            "valid": True,
            "mid_price": round(mid_price, 6),
            "microprice": round(microprice, 6),
            "divergence": round(divergence, 6),
            "divergence_bps": round((divergence / mid_price) * 10000, 2),
            "direction_signal": direction,
            "volume_ratio": round(bid_volume / ask_volume, 2) if ask_volume > 0 else None,
            "timestamp": datetime.now().isoformat()
        })
    
    @mcp.tool()
    def reset_analyzer() -> str:
        """
        Reset the microstructure analyzer state.
        
        Clears all historical data used for OFI calculation and volatility.
        Use this when switching between different trading pairs.
        
        Returns:
            Confirmation message
        """
        global _analyzer
        if _analyzer:
            _analyzer.reset()
        _analyzer = MicrostructureAnalyzer()
        
        return json.dumps({
            "status": "success",
            "message": "Analyzer state reset. OFI and volatility history cleared.",
            "timestamp": datetime.now().isoformat()
        })
