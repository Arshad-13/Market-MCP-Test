import asyncio
import json
from tools.exchange_tools import fetch_orderbook

async def test():
    result = await fetch_orderbook('BTC/USDT', 'binance', 5)
    data = json.loads(result)
    
    if 'bids' in data:
        print(f"✅ SUCCESS! Exchange: {data['exchange']}")
        print(f"   Top bid: ${data['bids'][0][0]}")
        print(f"   Top ask: ${data['asks'][0][0]}")
        print(f"   Fallback used: {data['fallback_used']}")
    else:
        print(f"❌ ERROR: {data.get('error')}")
        print(f"   Details: {data.get('last_error')}")

asyncio.run(test())
