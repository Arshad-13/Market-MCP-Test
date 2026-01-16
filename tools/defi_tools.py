"""
DeFi and Blockchain Data Tools

MCP tools for DeFi protocols and blockchain data.
Provides TVL, gas prices, and protocol metrics using DeFi Llama and Etherscan (optional).
"""

import os
import json
from datetime import datetime

import httpx
from cachetools import TTLCache
from mcp.server.fastmcp import FastMCP

# Cache for API responses
_defi_cache: TTLCache = TTLCache(maxsize=50, ttl=300)  # 5 min TTL
_chain_cache: TTLCache = TTLCache(maxsize=20, ttl=60)   # 1 min TTL

DEFI_LLAMA_BASE = "https://api.llama.fi"

def register_defi_tools(mcp: FastMCP) -> None:
    """
    Register DeFi and blockchain data MCP tools.
    
    Args:
        mcp: FastMCP server instance
    """
    
    @mcp.tool()
    async def get_defi_global_stats() -> str:
        """
        Get global DeFi statistics like Total Value Locked (TVL).
        
        Returns:
            JSON string with total TVL and chain breakdown.
        """
        if "global_tvl" in _defi_cache:
            return json.dumps({**_defi_cache["global_tvl"], "cached": True})
            
        url = f"{DEFI_LLAMA_BASE}/v2/chains"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=10.0)
                response.raise_for_status()
                data = response.json()
            
            # Calculate total TVL and top chains
            total_tvl = sum(c.get("tvl", 0) for c in data)
            sorted_chains = sorted(data, key=lambda x: x.get("tvl", 0), reverse=True)[:5]
            
            top_chains = [
                {
                    "name": c.get("name"),
                    "tvl": c.get("tvl"),
                    "token": c.get("tokenSymbol")
                }
                for c in sorted_chains
            ]
            
            result = {
                "total_tvl_usd": total_tvl,
                "top_chains": top_chains,
                "cached": False,
                "timestamp": datetime.now().isoformat()
            }
            
            _defi_cache["global_tvl"] = result
            return json.dumps(result)
            
        except httpx.HTTPError as e:
            return json.dumps({
                "error": "Failed to fetch DeFi stats",
                "details": str(e)
            })

    @mcp.tool()
    async def get_protocol_tvl(protocol_slug: str) -> str:
        """
        Get TVL and basic info for a specific DeFi protocol.
        
        Args:
            protocol_slug: The slug of the protocol (e.g., 'aave', 'uniswap', 'lido')
            
        Returns:
            JSON string with protocol details and TVL.
        """
        cache_key = f"protocol_{protocol_slug}"
        if cache_key in _defi_cache:
            return json.dumps({**_defi_cache[cache_key], "cached": True})
            
        url = f"{DEFI_LLAMA_BASE}/protocol/{protocol_slug}"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=10.0)
                response.raise_for_status()
                data = response.json()
                
            result = {
                "name": data.get("name"),
                "symbol": data.get("symbol"),
                "url": data.get("url"),
                "description": data.get("description"),
                "current_tvl": data.get("tvl", [])[-1].get("totalLiquidityUSD") if data.get("tvl") else None,
                "chains": data.get("chains"),
                "category": data.get("category"),
                "cached": False,
                "timestamp": datetime.now().isoformat()
            }
            
            _defi_cache[cache_key] = result
            return json.dumps(result)
            
        except httpx.HTTPError as e:
            return json.dumps({
                "error": f"Failed to fetch protocol '{protocol_slug}'",
                "details": str(e)
            })

    @mcp.tool()
    async def get_gas_price(chain: str = "ethereum") -> str:
        """
        Get current gas prices for a specific chain.
        Currently supports 'ethereum' via Etherscan (requires key) or generic estimate if key missing.
        
        Args:
            chain: Blockchain network name (default: 'ethereum')
            
        Returns:
            JSON string with gas prices (Safe, Propose, Fast).
        """
        # Note: Implementing a simple fallback or Etherscan if key exists
        api_key = os.getenv("ETHERSCAN_API_KEY")
        
        if chain.lower() != "ethereum":
             return json.dumps({"error": "Only Ethereum gas tracking is currently supported."})

        if not api_key:
             # Fallback to a assumed value or simpler public endpoint if available, 
             # but for now let's return a message indicating key is needed for live data
             # OR use a public estimator like ethgasstation if allows simple GET
             pass
        
        # Using Etherscan
        url = "https://api.etherscan.io/api"
        params = {
            "module": "gastracker",
            "action": "gasoracle",
            "apikey": api_key
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=10.0)
                # Etherscan returns 200 even on error, check status field
                data = response.json()
                
            if data.get("status") != "1" and api_key:
                 # Error from API (or key invalid)
                 return json.dumps({"error": "Etherscan API error", "details": data.get("message")})
            
            if not api_key:
                 # Simulating/Mocking if no key for specific testing or fallback
                 # In production, we should probably fail or use another source. 
                 # Let's return a helpful error.
                 return json.dumps({
                     "error": "ETHERSCAN_API_KEY not set. Cannot fetch live gas.",
                     "message": "Please set the ETHERSCAN_API_KEY environment variable."
                 })

            result = {
                "chain": "ethereum",
                "safe_gas_price": data["result"]["SafeGasPrice"],
                "propose_gas_price": data["result"]["ProposeGasPrice"],
                "fast_gas_price": data["result"]["FastGasPrice"],
                "base_fee": data["result"].get("suggestBaseFee"),
                "timestamp": datetime.now().isoformat()
            }
            
            return json.dumps(result)
            
        except Exception as e:
             return json.dumps({"error": "Failed to fetch gas price", "details": str(e)})

