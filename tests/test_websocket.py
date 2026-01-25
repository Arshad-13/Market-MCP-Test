"""
Tests for WebSocket Streaming Functionality (Phase 16)

Tests the WebSocket Manager and streaming tools without requiring live connections.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import asyncio
import json
from unittest.mock import Mock, AsyncMock, patch, MagicMock


def test_stream_subscription_dataclass():
    """Test StreamSubscription dataclass creation"""
    from core.websocket_manager import StreamSubscription
    
    sub = StreamSubscription(
        stream_id="test_stream",
        symbol="BTC/USDT",
        exchange="binance",
        stream_type="orderbook",
        websocket=None,
        is_connected=False,
        reconnect_attempts=0,
        last_message_time=None
    )
    
    assert sub.stream_id == "test_stream"
    assert sub.symbol == "BTC/USDT"
    assert sub.exchange == "binance"
    assert sub.is_connected is False
    print("✅ StreamSubscription dataclass: PASS")


def test_websocket_manager_initialization():
    """Test WebSocketManager initialization"""
    from core.websocket_manager import WebSocketManager
    
    manager = WebSocketManager(max_reconnect_attempts=3)
    
    assert manager.max_reconnect_attempts == 3
    assert len(manager.subscriptions) == 0
    assert len(manager.callbacks) == 0
    print("✅ WebSocketManager initialization: PASS")


@pytest.mark.asyncio
async def test_stream_subscription_lifecycle():
    """Test subscribing and unsubscribing from streams"""
    from core.websocket_manager import WebSocketManager
    
    manager = WebSocketManager()
    
    # Mock callback
    callback = Mock()
    
    # Mock websockets.connect to avoid actual connection
    with patch('core.websocket_manager.websockets.connect') as mock_connect:
        # Don't actually connect for this test
        mock_connect.side_effect = Exception("Test: Skip connection")
        
        # Subscribe (will fail to connect but still create subscription)
        stream_id = await manager.subscribe_binance_orderbook("BTC/USDT", callback)
        
        # Verify subscription was created
        assert stream_id in manager.subscriptions
        assert stream_id in manager.callbacks
        assert manager.subscriptions[stream_id].symbol == "BTC/USDT"
        
        print(f"✅ Stream subscription created: {stream_id}")
    
    # Unsubscribe
    await manager.unsubscribe(stream_id)
    assert stream_id not in manager.subscriptions
    assert stream_id not in manager.callbacks
    print("✅ Stream unsubscription: PASS")


def test_message_normalization_binance_orderbook():
    """Test Binance orderbook message normalization"""
    from core.websocket_manager import WebSocketManager, StreamSubscription
    
    manager = WebSocketManager()
    
    subscription = StreamSubscription(
        stream_id="test",
        symbol="BTC/USDT",
        exchange="binance",
        stream_type="orderbook",
        websocket=None,
        is_connected=True,
        reconnect_attempts=0,
        last_message_time=None
    )
    
    # Binance depth update message
    raw_message = {
        "e": "depthUpdate",
        "E": 1234567890,
        "s": "BTCUSDT",
        "b": [["50000.00", "0.1"], ["49999.00", "0.2"]],
        "a": [["50100.00", "0.15"], ["50101.00", "0.25"]]
    }
    
    normalized = manager._normalize_message(raw_message, subscription)
    
    assert normalized["type"] == "orderbook"
    assert normalized["symbol"] == "BTC/USDT"
    assert normalized["exchange"] == "binance"
    assert len(normalized["bids"]) == 2
    assert len(normalized["asks"]) == 2
    assert normalized["bids"][0] == [50000.0, 0.1]
    assert normalized["asks"][0] == [50100.0, 0.15]
    print("✅ Binance orderbook normalization: PASS")


def test_message_normalization_binance_ticker():
    """Test Binance ticker message normalization"""
    from core.websocket_manager import WebSocketManager, StreamSubscription
    
    manager = WebSocketManager()
    
    subscription = StreamSubscription(
        stream_id="test",
        symbol="BTC/USDT",
        exchange="binance",
        stream_type="ticker",
        websocket=None,
        is_connected=True,
        reconnect_attempts=0,
        last_message_time=None
    )
    
    # Binance ticker message
    raw_message = {
        "e": "24hrTicker",
        "E": 1234567890,
        "s": "BTCUSDT",
        "c": "50000.00",  # Last price
        "v": "1000.5",    # Volume
        "P": "2.5",       # Price change %
        "h": "51000.00",  # High
        "l": "49000.00"   # Low
    }
    
    normalized = manager._normalize_message(raw_message, subscription)
    
    assert normalized["type"] == "ticker"
    assert normalized["last_price"] == 50000.0
    assert normalized["volume_24h"] == 1000.5
    assert normalized["price_change_24h_percent"] == 2.5
    assert normalized["high_24h"] == 51000.0
    assert normalized["low_24h"] == 49000.0
    print("✅ Binance ticker normalization: PASS")


def test_get_active_streams():
    """Test getting active stream statuses"""
    from core.websocket_manager import WebSocketManager, StreamSubscription
    from datetime import datetime
    
    manager = WebSocketManager()
    
    # Add mock subscriptions
    manager.subscriptions["stream1"] = StreamSubscription(
        stream_id="stream1",
        symbol="BTC/USDT",
        exchange="binance",
        stream_type="orderbook",
        websocket=None,
        is_connected=True,
        reconnect_attempts=0,
        last_message_time=datetime.now()
    )
    
    manager.subscriptions["stream2"] = StreamSubscription(
        stream_id="stream2",
        symbol="ETH/USDT",
        exchange="binance",
        stream_type="ticker",
        websocket=None,
        is_connected=False,
        reconnect_attempts=2,
        last_message_time=None
    )
    
    statuses = manager.get_active_streams()
    
    assert len(statuses) == 2
    assert "stream1" in statuses
    assert "stream2" in statuses
    assert statuses["stream1"]["connected"] is True
    assert statuses["stream2"]["connected"] is False
    assert statuses["stream2"]["reconnect_attempts"] == 2
    print("✅ Get active streams: PASS")


def test_get_stream_status():
    """Test getting specific stream status"""
    from core.websocket_manager import WebSocketManager, StreamSubscription
    
    manager = WebSocketManager()
    
    manager.subscriptions["test_stream"] = StreamSubscription(
        stream_id="test_stream",
        symbol="BTC/USDT",
        exchange="binance",
        stream_type="orderbook",
        websocket=None,
        is_connected=True,
        reconnect_attempts=0,
        last_message_time=None
    )
    
    status = manager.get_stream_status("test_stream")
    
    assert status is not None
    assert status["stream_id"] == "test_stream"
    assert status["symbol"] == "BTC/USDT"
    assert status["connected"] is True
    
    # Test non-existent stream
    status_none = manager.get_stream_status("nonexistent")
    assert status_none is None
    print("✅ Get stream status: PASS")


@pytest.mark.asyncio
async def test_streaming_tools_subscribe():
    """Test streaming tools subscribe function"""
    from tools.streaming_tools import subscribe_stream
    
    with patch('core.websocket_manager.ws_manager') as mock_manager:
        mock_manager.subscribe_binance_orderbook = AsyncMock(return_value="test_stream_id")
        
        result = await subscribe_stream("BTC/USDT", "orderbook", "binance")
        result_dict = json.loads(result)
        
        assert result_dict["status"] == "subscribed"
        assert result_dict["stream_id"] == "test_stream_id"
        assert result_dict["symbol"] == "BTC/USDT"
        print("✅ Streaming tools subscribe: PASS")


@pytest.mark.asyncio
async def test_streaming_tools_unsubscribe():
    """Test streaming tools unsubscribe function"""
    from tools.streaming_tools import unsubscribe_stream
    
    with patch('core.websocket_manager.ws_manager') as mock_manager:
        mock_manager.unsubscribe = AsyncMock()
        
        result = await unsubscribe_stream("test_stream_id")
        result_dict = json.loads(result)
        
        assert result_dict["status"] == "unsubscribed"
        assert result_dict["stream_id"] == "test_stream_id"
        print("✅ Streaming tools unsubscribe: PASS")


def test_streaming_tools_get_active_streams():
    """Test streaming tools get active streams function"""
    from tools.streaming_tools import get_active_streams
    
    with patch('core.websocket_manager.ws_manager') as mock_manager:
        mock_manager.get_active_streams.return_value = {
            "stream1": {"symbol": "BTC/USDT", "connected": True}
        }
        
        result = get_active_streams()
        result_dict = json.loads(result)
        
        assert result_dict["total_count"] == 1
        assert "stream1" in result_dict["active_streams"]
        print("✅ Streaming tools get active streams: PASS")


if __name__ == "__main__":
    """Run tests without pytest"""
    print("\\n" + "="*60)
    print("Phase 16: WebSocket Streaming Tests")
    print("="*60 + "\\n")
    
    # Sync tests
    test_stream_subscription_dataclass()
    test_websocket_manager_initialization()
    test_message_normalization_binance_orderbook()
    test_message_normalization_binance_ticker()
    test_get_active_streams()
    test_get_stream_status()
    test_streaming_tools_get_active_streams()
    
    # Async tests (run with asyncio)
    asyncio.run(test_stream_subscription_lifecycle())
    asyncio.run(test_streaming_tools_subscribe())
    asyncio.run(test_streaming_tools_unsubscribe())
    
    print("\\n" + "="*60)
    print("✅ All Phase 16 Tests Passed!")
    print("="*60)
