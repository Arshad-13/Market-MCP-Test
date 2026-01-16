"""
Anomaly Detection Tools

MCP tools for market manipulation and anomaly detection.
Provides spoofing, layering, and liquidity gap detection.
"""

from typing import List, Optional
import json
from datetime import datetime

from mcp.server.fastmcp import FastMCP

from core.analytics import OrderBook
from core.anomaly_detection import (
    AnomalyDetector,
    MarketState,
    MarketRegime,
    AnomalyType
)
from core.data_validator import validate_order_book


# Global detector instance
_detector: Optional[AnomalyDetector] = None


def _get_detector() -> AnomalyDetector:
    """Get or create the global detector instance."""
    global _detector
    if _detector is None:
        _detector = AnomalyDetector()
    return _detector


def register_anomaly_tools(mcp: FastMCP) -> None:
    """
    Register anomaly detection MCP tools.
    
    Args:
        mcp: FastMCP server instance
    """
    
    @mcp.tool()
    def detect_anomalies(
        bids: List[List[float]],
        asks: List[List[float]],
        symbol: str = "UNKNOWN"
    ) -> str:
        """
        Analyze order book for market anomalies and manipulation.
        
        Detects:
        - Spoofing: Large fake orders to manipulate price
        - Layering: Multiple fake orders at different levels
        - Liquidity gaps: Price levels with thin volume
        - Heavy imbalance: Extreme bid/ask volume skew
        - Spread shocks: Sudden spread widening
        
        Args:
            bids: List of [price, volume] pairs for bids
            asks: List of [price, volume] pairs for asks
            symbol: Optional symbol name for reference
            
        Returns:
            JSON string with detected anomalies and market regime
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
        detector = _get_detector()
        state = detector.analyze(book)
        
        return json.dumps({
            "valid": True,
            "symbol": symbol,
            "market_regime": state.regime.value,
            "regime_description": _get_regime_description(state.regime),
            "risk_scores": {
                "overall": state.overall_risk_score,
                "spoofing": state.spoofing_risk,
                "liquidity": state.liquidity_score
            },
            "anomalies": [a.to_dict() for a in state.anomalies],
            "anomaly_count": len(state.anomalies),
            "has_critical_anomalies": any(
                a.severity.value == "critical" for a in state.anomalies
            ),
            "timestamp": datetime.now().isoformat()
        })
    
    @mcp.tool()
    def detect_spoofing(
        bids: List[List[float]],
        asks: List[List[float]],
        volume_threshold_multiplier: float = 5.0
    ) -> str:
        """
        Specifically detect potential spoofing in order book.
        
        Spoofing involves placing large orders with no intention of executing,
        to create false impression of demand/supply.
        
        Args:
            bids: List of [price, volume] pairs for bids
            asks: List of [price, volume] pairs for asks
            volume_threshold_multiplier: How many times avg volume = suspicious
            
        Returns:
            JSON string with spoofing analysis
        """
        is_valid, errors = validate_order_book(bids, asks)
        if not is_valid:
            return json.dumps({"error": "Invalid data", "details": errors})
        
        detector = _get_detector()
        
        # Get rolling average volume
        avg_volume = detector._avg_l1_volume or 100.0
        threshold = avg_volume * volume_threshold_multiplier
        
        suspects = []
        
        for side, levels in [("BID", bids), ("ASK", asks)]:
            for i, level in enumerate(levels[:5]):
                price, volume = level
                if volume > threshold:
                    risk_score = min(100, (volume / threshold) * 50)
                    suspects.append({
                        "side": side,
                        "level": i + 1,
                        "price": price,
                        "volume": volume,
                        "avg_volume": round(avg_volume, 2),
                        "multiplier": round(volume / avg_volume, 1),
                        "risk_score": round(risk_score, 1)
                    })
        
        return json.dumps({
            "spoofing_detected": len(suspects) > 0,
            "suspicious_orders": suspects,
            "count": len(suspects),
            "threshold_used": round(threshold, 2),
            "avg_volume": round(avg_volume, 2),
            "timestamp": datetime.now().isoformat()
        })
    
    @mcp.tool()
    def detect_liquidity_gaps(
        bids: List[List[float]],
        asks: List[List[float]],
        min_volume_threshold: float = 50.0
    ) -> str:
        """
        Detect price levels with insufficient liquidity.
        
        Liquidity gaps can cause slippage and are often exploited by HFT.
        
        Args:
            bids: List of [price, volume] pairs for bids
            asks: List of [price, volume] pairs for asks
            min_volume_threshold: Minimum volume for adequate liquidity
            
        Returns:
            JSON string with identified liquidity gaps
        """
        is_valid, errors = validate_order_book(bids, asks)
        if not is_valid:
            return json.dumps({"error": "Invalid data", "details": errors})
        
        gaps = []
        total_gap_severity = 0
        
        for side, levels in [("bid", bids), ("ask", asks)]:
            for i, level in enumerate(levels[:10]):
                price, volume = level
                if volume < min_volume_threshold:
                    severity = (10 - i) * (min_volume_threshold - volume) / min_volume_threshold
                    total_gap_severity += severity
                    
                    gaps.append({
                        "side": side,
                        "level": i + 1,
                        "price": price,
                        "volume": volume,
                        "deficit": round(min_volume_threshold - volume, 2),
                        "severity": round(severity * 10, 1)
                    })
        
        # Overall score (lower = better liquidity)
        liquidity_score = max(0, 100 - total_gap_severity * 5)
        
        return json.dumps({
            "gaps_found": len(gaps),
            "gaps": gaps[:10],  # Top 10 most severe
            "total_gap_severity": round(total_gap_severity, 2),
            "liquidity_score": round(liquidity_score, 1),
            "liquidity_rating": "Good" if liquidity_score > 70 else "Fair" if liquidity_score > 40 else "Poor",
            "timestamp": datetime.now().isoformat()
        })
    
    @mcp.tool()
    def get_market_regime(
        bids: List[List[float]],
        asks: List[List[float]]
    ) -> str:
        """
        Classify current market regime based on order book analysis.
        
        Regimes:
        - Calm: Low volatility, tight spreads, balanced book
        - Stressed: High volatility, wide spreads, imbalanced book
        - Execution Hot: Large orders, aggressive trading
        - Manipulation Suspected: Multiple anomalies detected
        
        Args:
            bids: List of [price, volume] pairs for bids
            asks: List of [price, volume] pairs for asks
            
        Returns:
            JSON string with market regime classification
        """
        is_valid, errors = validate_order_book(bids, asks)
        if not is_valid:
            return json.dumps({"error": "Invalid data", "details": errors})
        
        book = OrderBook.from_raw(bids, asks, datetime.now())
        detector = _get_detector()
        state = detector.analyze(book)
        
        return json.dumps({
            "regime": state.regime.value,
            "description": _get_regime_description(state.regime),
            "risk_level": _get_risk_level(state.overall_risk_score),
            "risk_score": round(state.overall_risk_score, 1),
            "metrics": {
                "spoofing_risk": round(state.spoofing_risk, 1),
                "liquidity_score": round(state.liquidity_score, 1),
                "anomaly_count": len(state.anomalies)
            },
            "recommendation": _get_recommendation(state.regime),
            "timestamp": datetime.now().isoformat()
        })
    
    @mcp.tool()
    def reset_detector() -> str:
        """
        Reset the anomaly detector state.
        
        Clears all historical data used for anomaly detection.
        Use when switching trading pairs.
        
        Returns:
            Confirmation message
        """
        global _detector
        if _detector:
            _detector.reset()
        _detector = AnomalyDetector()
        
        return json.dumps({
            "status": "success",
            "message": "Anomaly detector reset. All historical baselines cleared.",
            "timestamp": datetime.now().isoformat()
        })


def _get_regime_description(regime: MarketRegime) -> str:
    """Get human-readable description of market regime."""
    descriptions = {
        MarketRegime.CALM: "Market is stable with normal trading activity",
        MarketRegime.STRESSED: "Elevated volatility and potential instability",
        MarketRegime.EXECUTION_HOT: "High trading activity with large order flow",
        MarketRegime.MANIPULATION_SUSPECTED: "Warning: Potential market manipulation detected"
    }
    return descriptions.get(regime, "Unknown regime")


def _get_risk_level(score: float) -> str:
    """Convert risk score to level."""
    if score < 25:
        return "Low"
    elif score < 50:
        return "Medium"
    elif score < 75:
        return "High"
    else:
        return "Critical"


def _get_recommendation(regime: MarketRegime) -> str:
    """Get trading recommendation based on regime."""
    recommendations = {
        MarketRegime.CALM: "Normal trading conditions - standard execution",
        MarketRegime.STRESSED: "Exercise caution - consider reducing position size",
        MarketRegime.EXECUTION_HOT: "Use limit orders - expect slippage on market orders",
        MarketRegime.MANIPULATION_SUSPECTED: "Avoid trading - wait for market to stabilize"
    }
    return recommendations.get(regime, "Proceed with caution")
