"""
Test Multi-Exchange Fallback Functionality
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import asyncio
import json
from unittest.mock import AsyncMock, patch


@pytest.mark.asyncio
async def test_fallback_success_on_first_exchange():
    """Test that fallback returns immediately if first exchange works"""
    from tools.exchange_tools import fetch_orderbook
    
    # Mock successful response from Binance
    with patch('tools.exchange_tools._get_exchange') as mock_get_exchange:
        mock_exchange = AsyncMock()
        mock_exchange.fetch_order_book = AsyncMock(return_value={
            "bids": [[50000, 0.1], [49999, 0.2]],
            "asks": [[50100, 0.15], [50101, 0.25]],
            "nonce": 12345
        })
        mock_exchange.close = AsyncMock()
        mock_get_exchange.return_value = mock_exchange
        
        result = await fetch_orderbook("BTC/USDT", "binance", 20, fallback=True)
        result_dict = json.loads(result)
        
        assert result_dict["exchange"] == "binance"
        assert result_dict["fallback_used"] is False
        assert len(result_dict["bids"]) == 2
        print("✅ Fallback SUCCESS on first exchange: PASS")


@pytest.mark.asyncio
async def test_fallback_to_second_exchange():
    """Test that fallback tries second exchange if first fails"""
    from tools.exchange_tools import fetch_orderbook
    
    call_count = 0
    
    async def mock_get_exchange(exchange_id):
        nonlocal call_count
        call_count += 1
        
        mock_exchange = AsyncMock()
        mock_exchange.close = AsyncMock()
        
        if call_count == 1:
            # First exchange (Binance) fails
            mock_exchange.fetch_order_book = AsyncMock(
                side_effect=Exception("ExchangeNotAvailable")
            )
        else:
            # Second exchange (Kraken) succeeds
            mock_exchange.fetch_order_book = AsyncMock(return_value={
                "bids": [[50000, 0.1]],
                "asks": [[50100, 0.15]],
                "nonce": 67890
            })
        
        return mock_exchange
    
    with patch('tools.exchange_tools._get_exchange', side_effect=mock_get_exchange):
        result = await fetch_orderbook("BTC/USDT", "binance", 20, fallback=True)
        result_dict = json.loads(result)
        
        assert result_dict["exchange"] == "kraken"  # Should use Kraken
        assert result_dict["requested_exchange"] == "binance"
        assert result_dict["fallback_used"] is True
        print("✅ Fallback to second exchange (Kraken): PASS")


@pytest.mark.asyncio
async def test_fallback_all_exchanges_fail():
    """Test error response when all exchanges fail"""
    from tools.exchange_tools import fetch_orderbook
    
    async def mock_get_exchange(exchange_id):
        mock_exchange = AsyncMock()
        mock_exchange.fetch_order_book = AsyncMock(
            side_effect=Exception("NetworkError")
        )
        mock_exchange.close = AsyncMock()
        return mock_exchange
    
    with patch('tools.exchange_tools._get_exchange', side_effect=mock_get_exchange):
        result = await fetch_orderbook("BTC/USDT", "binance", 20, fallback=True)
        result_dict = json.loads(result)
        
        assert "error" in result_dict
        assert "all exchanges" in result_dict["error"].lower()
        assert "attempted_exchanges" in result_dict
        assert len(result_dict["attempted_exchanges"]) > 1  # Tried multiple
        print("✅ All exchanges fail gracefully: PASS")


@pytest.mark.asyncio
async def test_fallback_disabled():
    """Test that fallback can be disabled"""
    from tools.exchange_tools import fetch_orderbook
    
    call_count = 0
    
    async def mock_get_exchange(exchange_id):
        nonlocal call_count
        call_count += 1
        
        mock_exchange = AsyncMock()
        mock_exchange.fetch_order_book = AsyncMock(
            side_effect=Exception("ExchangeNotAvailable")
        )
        mock_exchange.close = AsyncMock()
        return mock_exchange
    
    with patch('tools.exchange_tools._get_exchange', side_effect=mock_get_exchange):
        result = await fetch_orderbook("BTC/USDT", "binance", 20, fallback=False)
        result_dict = json.loads(result)
        
        # Should only try Binance once
        assert call_count == 1
        assert "error" in result_dict
        print("✅ Fallback disabled works: PASS")


def test_exchange_fallback_order():
    """Test that EXCHANGE_FALLBACK_ORDER is correctly defined"""
    from tools.exchange_tools import EXCHANGE_FALLBACK_ORDER
    
    assert len(EXCHANGE_FALLBACK_ORDER) == 5
    assert EXCHANGE_FALLBACK_ORDER[0] == "binance"
    assert "kraken" in EXCHANGE_FALLBACK_ORDER
    assert "coinbase" in EXCHANGE_FALLBACK_ORDER
    print("✅ Exchange fallback order correct: PASS")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("Multi-Exchange Fallback Tests")
    print("="*60 + "\n")
    
    # Sync test
    test_exchange_fallback_order()
    
    # Async tests
    asyncio.run(test_fallback_success_on_first_exchange())
    asyncio.run(test_fallback_to_second_exchange())
    asyncio.run(test_fallback_all_exchanges_fail())
    asyncio.run(test_fallback_disabled())
    
    print("\n" + "="*60)
    print("✅ All Fallback Tests Passed!")
    print("="*60)
