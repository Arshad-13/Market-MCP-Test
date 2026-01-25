"""
Deep CCXT Investigation - Why is exchangeInfo still being called?
"""

import ccxt.async_support as ccxt
import asyncio

async def test_ccxt_initialization_methods():
    """Test different ways to prevent CCXT from calling exchangeInfo"""
    
    print("="*60)
    print("CCXT Initialization Tests")
    print("="*60)
    print()
    
    # Test 1: Default (will call exchangeInfo)
    print("Test 1: Default initialization")
    try:
        exchange = ccxt.binance()
        print(f"✅ Initialized: {exchange}")
        await exchange.close()
    except Exception as e:
        print(f"❌ Failed: {type(e).__name__}: {e}")
    print()
    
    # Test 2: With fetchMarkets: False
    print("Test 2: fetchMarkets: False in options")
    try:
        exchange = ccxt.binance({
            'enableRateLimit': True,
            'timeout': 30000,
            'options': {
                'fetchMarkets': False,
            }
        })
        print(f"✅ Initialized: {exchange}")
        print(f"   markets loaded: {len(exchange.markets) if exchange.markets else 0}")
        await exchange.close()
    except Exception as e:
        print(f"❌ Failed: {type(e).__name__}: {e}")
    print()
    
    # Test 3: Try to fetch orderbook without loading markets
    print("Test 3: Fetch orderbook without loading markets")
    try:
        exchange = ccxt.binance({
            'enableRateLimit': True,
            'timeout': 30000,
        })
        
        print(f"   Attempting fetch_order_book...")
        # This WILL try to load markets because CCXT validates symbols
        ob = await exchange.fetch_order_book('BTC/USDT', 5)
        print(f"✅ Got orderbook: {len(ob['bids'])} bids")
        await exchange.close()
    except Exception as e:
        print(f"❌ Failed: {type(e).__name__}: {e}")
    print()
    
    # Test 4: Use raw API call instead of CCXT helper
    print("Test 4: Raw HTTP request (bypass CCXT)")
    try:
        import httpx
        
        url = "https://api.binance.com/api/v3/depth"
        params = {"symbol": "BTCUSDT", "limit": 5}
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=10.0)
            data = response.json()
            print(f"✅ Raw API call successful!")
            print(f"   Status: {response.status_code}")
            print(f"   Bids: {len(data.get('bids', []))}")
            print(f"   Asks: {len(data.get('asks', []))}")
    except Exception as e:
        print(f"❌ Failed: {type(e).__name__}: {e}")
    print()
    
    # Test 5: Check if it's a proxy/SSL issue
    print("Test 5: Check SSL/TLS connection")
    try:
        import ssl
        import socket
        
        context = ssl.create_default_context()
        with socket.create_connection(("api.binance.com", 443), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname="api.binance.com") as ssock:
                print(f"✅ SSL connection successful!")
                print(f"   Protocol: {ssock.version()}")
                print(f"   Cipher: {ssock.cipher()}")
    except Exception as e:
        print(f"❌ Failed: {type(e).__name__}: {e}")
    print()

if __name__ == "__main__":
    asyncio.run(test_ccxt_initialization_methods())
