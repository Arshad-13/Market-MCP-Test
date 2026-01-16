"""
Market Analysis Prompts

Defines MCP prompts for common market intelligence tasks.
"""

from mcp.server.fastmcp import FastMCP

def register_prompts(mcp: FastMCP) -> None:
    """
    Register market analysis prompts.
    
    Args:
        mcp: FastMCP server instance
    """
    
    @mcp.prompt()
    def daily_briefing(symbol: str = "bitcoin") -> str:
        """
        Generate a daily market briefing for a specific asset.
        """
        return f"""
        Please provide a comprehensive daily briefing for {symbol}.
        
        1. Use 'get_coin_details' and 'get_crypto_price' to fetch the latest data.
        2. Use 'get_fear_and_greed_index' to gauge market sentiment.
        3. Use 'get_global_market_data' to understand the broader context.
        4. If order book data is available (via user upload or context), use 'detect_anomalies' and 'analyze_orderbook'.
        
        Structure the report as follows:
        - **Executive Summary**: Key price action and dominant sentiment.
        - **Market Metrics**: Price, Volume, Market Cap, 24h Change.
        - **Sentiment Analysis**: Fear & Greed Index and its implication.
        - **Market Context**: How {symbol} is performing relative to the global market.
        - **Key Risks**: Any anomalies or unusual metrics if detected.
        """
    
    @mcp.prompt()
    def analyze_liquidity(symbol: str, price_level: float = 0.0) -> str:
        """
        Analyze liquidity conditions and potential slippage.
        """
        return f"""
        Perform a deep dive into the liquidity conditions for {symbol}.
        
        1. Use 'get_crypto_price' to get the current price.
        2. If you have order book data, use 'analyze_orderbook' and 'detect_liquidity_gaps'.
        3. Use 'analyze_bid_ask_spread' if only BBO is available.
        
        Assess:
        - Spread tightness (basis points).
        - Depth of market (if visible).
        - Presence of liquidity gaps near {price_level if price_level > 0 else "current price"}.
        - Overall market regime (Calm, Stressed, etc.).
        """
    
    @mcp.prompt()
    def hunt_anomalies(symbol: str) -> str:
        """
        Scan for market manipulation and anomalies.
        """
        return f"""
        Act as a Market Surveillance Officer scanning {symbol} for manipulation.
        
        REQUIRED DATA: You need an order book snapshot (bids/asks).
        
        1. Run 'detect_anomalies' to find spoofing, layering, or regime shifts.
        2. Run 'detect_spoofing' with strict thresholds if volume is high.
        3. Run 'calculate_microprice' to check for price divergence.
        
        Report on:
        - Detected anomalies (Severity & Confidence).
        - Market Regime (Is it manipulation-suspected?).
        - Order Flow Imbalance (OFI) direction.
        - Immediate risk to trading.
        """

