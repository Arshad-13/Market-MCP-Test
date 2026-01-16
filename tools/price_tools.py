"""
Price and Market Data Tools

MCP tools for fetching and analyzing cryptocurrency prices.
"""

import os
import json
from typing import Optional
from datetime import datetime, timedelta
from functools import lru_cache

import httpx
from cachetools import TTLCache
from tenacity import retry, stop_after_attempt, wait_exponential

from mcp.server.fastmcp import FastMCP


# API Configuration
COINGECKO_BASE_URL = "https://api.coingecko.com/api/v3"

# Cache for API responses (60 second TTL)
_price_cache: TTLCache = TTLCache(maxsize=100, ttl=60)
_coin_details_cache: TTLCache = TTLCache(maxsize=50, ttl=300)


def _get_headers() -> dict:
    """Get API headers with optional API key."""
    headers = {"accept": "application/json"}
    api_key = os.getenv("CRYPTO_API_KEY")
    if api_key:
        headers["x-cg-demo-api-key"] = api_key
    return headers


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10)
)
async def _fetch_with_retry(url: str, params: dict) -> dict:
    """Fetch data with retry logic for rate limits."""
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params, headers=_get_headers(), timeout=10.0)
        response.raise_for_status()
        return response.json()


def register_price_tools(mcp: FastMCP) -> None:
    """
    Register price-related MCP tools.
    
    Args:
        mcp: FastMCP server instance
    """
    
    @mcp.tool()
    async def get_crypto_price(
        asset_id: str,
        vs_currencies: str = "usd",
        include_market_cap: bool = True,
        include_24h_vol: bool = True,
        include_24h_change: bool = True
    ) -> str:
        """
        Fetch live cryptocurrency price with market data.
        
        Args:
            asset_id: The ID of the crypto asset (e.g., 'bitcoin', 'ethereum')
            vs_currencies: Comma-separated target currencies (default: 'usd')
            include_market_cap: Include market capitalization
            include_24h_vol: Include 24-hour trading volume
            include_24h_change: Include 24-hour price change percentage
            
        Returns:
            JSON string with price data and market metrics
        """
        cache_key = f"{asset_id}_{vs_currencies}"
        
        # Check cache first
        if cache_key in _price_cache:
            cached = _price_cache[cache_key]
            cached["cached"] = True
            return json.dumps(cached)
        
        url = f"{COINGECKO_BASE_URL}/simple/price"
        params = {
            "ids": asset_id,
            "vs_currencies": vs_currencies,
            "include_market_cap": str(include_market_cap).lower(),
            "include_24hr_vol": str(include_24h_vol).lower(),
            "include_24hr_change": str(include_24h_change).lower()
        }
        
        try:
            data = await _fetch_with_retry(url, params)
            data["cached"] = False
            data["timestamp"] = datetime.now().isoformat()
            _price_cache[cache_key] = data
            return json.dumps(data)
        except httpx.HTTPError as e:
            return f'{{"error": "Failed to fetch price", "details": "{str(e)}"}}'
    
    @mcp.tool()
    async def get_coin_details(asset_id: str) -> str:
        """
        Get detailed information about a cryptocurrency.
        
        Includes: description, market data, community stats, developer stats.
        
        Args:
            asset_id: The ID of the crypto asset (e.g., 'bitcoin', 'ethereum')
            
        Returns:
            JSON string with comprehensive coin information
        """
        if asset_id in _coin_details_cache:
            return json.dumps({**_coin_details_cache[asset_id], "cached": True})
        
        url = f"{COINGECKO_BASE_URL}/coins/{asset_id}"
        params = {
            "localization": "false",
            "tickers": "false",
            "market_data": "true",
            "community_data": "true",
            "developer_data": "true"
        }
        
        try:
            data = await _fetch_with_retry(url, params)
            
            # Extract relevant fields
            result = {
                "id": data.get("id"),
                "symbol": data.get("symbol"),
                "name": data.get("name"),
                "description": data.get("description", {}).get("en", "")[:500],
                "market_data": {
                    "current_price": data.get("market_data", {}).get("current_price", {}),
                    "market_cap": data.get("market_data", {}).get("market_cap", {}),
                    "total_volume": data.get("market_data", {}).get("total_volume", {}),
                    "price_change_24h": data.get("market_data", {}).get("price_change_percentage_24h"),
                    "price_change_7d": data.get("market_data", {}).get("price_change_percentage_7d"),
                    "ath": data.get("market_data", {}).get("ath", {}),
                    "atl": data.get("market_data", {}).get("atl", {}),
                    "circulating_supply": data.get("market_data", {}).get("circulating_supply"),
                    "total_supply": data.get("market_data", {}).get("total_supply"),
                    "max_supply": data.get("market_data", {}).get("max_supply"),
                    "fdv": data.get("market_data", {}).get("fully_diluted_valuation", {})
                },
                "links": {
                    "homepage": data.get("links", {}).get("homepage", []),
                    "twitter": data.get("links", {}).get("twitter_screen_name"),
                    "github": data.get("links", {}).get("repos_url", {}).get("github", [])
                },
                "cached": False,
                "timestamp": datetime.now().isoformat()
            }
            
            _coin_details_cache[asset_id] = result
            return json.dumps(result)
            
        except httpx.HTTPError as e:
            return f'{{"error": "Failed to fetch coin details", "details": "{str(e)}"}}'
    
    @mcp.tool()
    async def get_historical_prices(
        asset_id: str,
        days: int = 7,
        vs_currency: str = "usd",
        interval: str = "daily"
    ) -> str:
        """
        Get historical price data for a cryptocurrency.
        
        Args:
            asset_id: The ID of the crypto asset (e.g., 'bitcoin')
            days: Number of days of historical data (1-365)
            vs_currency: Target currency (default: 'usd')
            interval: Data interval - 'daily' or 'hourly' (hourly only for <= 90 days)
            
        Returns:
            JSON string with historical prices, market caps, and volumes
        """
        url = f"{COINGECKO_BASE_URL}/coins/{asset_id}/market_chart"
        params = {
            "vs_currency": vs_currency,
            "days": min(days, 365),
            "interval": interval if days <= 90 else "daily"
        }
        
        try:
            data = await _fetch_with_retry(url, params)
            
            # Format data for easier consumption
            prices = data.get("prices", [])
            result = {
                "asset_id": asset_id,
                "vs_currency": vs_currency,
                "days": days,
                "data_points": len(prices),
                "prices": [
                    {
                        "timestamp": datetime.fromtimestamp(p[0] / 1000).isoformat(),
                        "price": p[1]
                    }
                    for p in prices
                ],
                "summary": {
                    "start_price": prices[0][1] if prices else None,
                    "end_price": prices[-1][1] if prices else None,
                    "min_price": min(p[1] for p in prices) if prices else None,
                    "max_price": max(p[1] for p in prices) if prices else None,
                    "price_change_pct": ((prices[-1][1] - prices[0][1]) / prices[0][1] * 100) if prices else None
                },
                "timestamp": datetime.now().isoformat()
            }
            
            return str(result)
            
        except httpx.HTTPError as e:
            return f'{{"error": "Failed to fetch historical data", "details": "{str(e)}"}}'
    
    @mcp.tool()
    async def get_trending_coins() -> str:
        """
        Get the top 7 trending coins on CoinGecko.
        
        Based on search popularity in the last 24 hours.
        
        Returns:
            JSON string with list of trending coins and their details
        """
        url = f"{COINGECKO_BASE_URL}/search/trending"
        
        try:
            data = await _fetch_with_retry(url, {})
            
            coins = []
            for item in data.get("coins", []):
                coin = item.get("item", {})
                coins.append({
                    "id": coin.get("id"),
                    "symbol": coin.get("symbol"),
                    "name": coin.get("name"),
                    "market_cap_rank": coin.get("market_cap_rank"),
                    "price_btc": coin.get("price_btc"),
                    "score": coin.get("score")
                })
            
            return json.dumps({
                "trending_coins": coins,
                "count": len(coins),
                "timestamp": datetime.now().isoformat()
            })
            
        except httpx.HTTPError as e:
            return f'{{"error": "Failed to fetch trending coins", "details": "{str(e)}"}}'
    
    @mcp.tool()
    async def get_global_market_data() -> str:
        """
        Get global cryptocurrency market data.
        
        Includes: total market cap, BTC dominance, total volume, active coins.
        
        Returns:
            JSON string with global market metrics
        """
        url = f"{COINGECKO_BASE_URL}/global"
        
        try:
            data = await _fetch_with_retry(url, {})
            market_data = data.get("data", {})
            
            result = {
                "total_market_cap_usd": market_data.get("total_market_cap", {}).get("usd"),
                "total_volume_24h_usd": market_data.get("total_volume", {}).get("usd"),
                "btc_dominance": market_data.get("market_cap_percentage", {}).get("btc"),
                "eth_dominance": market_data.get("market_cap_percentage", {}).get("eth"),
                "active_cryptocurrencies": market_data.get("active_cryptocurrencies"),
                "markets": market_data.get("markets"),
                "market_cap_change_24h_pct": market_data.get("market_cap_change_percentage_24h_usd"),
                "timestamp": datetime.now().isoformat()
            }
            
            return str(result)
            
        except httpx.HTTPError as e:
            return f'{{"error": "Failed to fetch global market data", "details": "{str(e)}"}}'
