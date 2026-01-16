"""
Sentiment Analysis Tools

MCP tools for market sentiment analysis.
Provides Fear & Greed Index and social sentiment metrics.
"""

import json
from datetime import datetime
from typing import Optional

import httpx
from cachetools import TTLCache
from mcp.server.fastmcp import FastMCP

# Cache for API responses
_sentiment_cache: TTLCache = TTLCache(maxsize=10, ttl=3600)  # 1 hour TTL for F&G

def register_sentiment_tools(mcp: FastMCP) -> None:
    """
    Register sentiment analysis MCP tools.
    
    Args:
        mcp: FastMCP server instance
    """
    
    @mcp.tool()
    async def get_fear_and_greed_index() -> str:
        """
        Get the current Crypto Fear & Greed Index.
        
        The index ranges from 0 (Extreme Fear) to 100 (Extreme Greed).
        Useful for gauging overall market sentiment.
        
        Returns:
            JSON string with index value, classification, and update time.
        """
        if "fng" in _sentiment_cache:
            return json.dumps({**_sentiment_cache["fng"], "cached": True})
            
        url = "https://api.alternative.me/fng/"
        params = {"limit": "1", "format": "json"}
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=10.0)
                response.raise_for_status()
                data = response.json()
                
            item = data.get("data", [{}])[0]
            value = int(item.get("value", 50))
            classification = item.get("value_classification", "Neutral")
            timestamp = item.get("timestamp")
            
            # Add interpretation
            interpretation = "Market is fearful. Potential buying opportunity?" if value < 25 else \
                             "Market is greedy. Potential correction ahead?" if value > 75 else \
                             "Market sentiment is neutral."
                             
            result = {
                "value": value,
                "classification": classification,
                "interpretation": interpretation,
                "last_updated": datetime.fromtimestamp(int(timestamp)).isoformat() if timestamp else None,
                "cached": False,
                "timestamp": datetime.now().isoformat()
            }
            
            _sentiment_cache["fng"] = result
            return json.dumps(result)
            
        except httpx.HTTPError as e:
            return json.dumps({
                "error": "Failed to fetch Fear & Greed Index",
                "details": str(e)
            })

