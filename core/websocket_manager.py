"""
WebSocket Manager for Real-Time Market Data Streaming

Provides async WebSocket connections to crypto exchanges with:
- Connection pooling and management
- Auto-reconnection with exponential backoff
- Message parsing and normalization
- Event-based callbacks for data broadcasting
"""

import asyncio
import json
import logging
from typing import Dict, Optional, Callable, Any
from datetime import datetime
from dataclasses import dataclass
import websockets
from websockets.exceptions import ConnectionClosed

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class StreamSubscription:
    """Represents an active WebSocket stream subscription"""
    stream_id: str
    symbol: str
    exchange: str
    stream_type: str  # 'orderbook' or 'ticker'
    websocket: Optional[websockets.WebSocketClientProtocol]
    is_connected: bool
    reconnect_attempts: int
    last_message_time: Optional[datetime]


class WebSocketManager:
    """
    Manages WebSocket connections to cryptocurrency exchanges.
    
    Features:
    - Concurrent multi-symbol streaming
    - Auto-reconnection with exponential backoff
    - Message parsing and normalization
    - Thread-safe subscription management
    """
    
    def __init__(self, max_reconnect_attempts: int = 5):
        self.subscriptions: Dict[str, StreamSubscription] = {}
        self.callbacks: Dict[str, Callable] = {}
        self.max_reconnect_attempts = max_reconnect_attempts
        self.is_running = False
        
    async def subscribe_binance_orderbook(
        self,
        symbol: str,
        callback: Callable[[Dict[str, Any]], None],
        depth: int = 20
    ) -> str:
        """
        Subscribe to Binance orderbook WebSocket stream.
        
        Args:
            symbol: Trading pair (e.g., 'BTC/USDT')
            callback: Function to call with orderbook updates
            depth: Order book depth (5, 10, or 20)
            
        Returns:
            stream_id: Unique identifier for this subscription
        """
        # Convert symbol format: BTC/USDT -> btcusdt
        binance_symbol = symbol.replace('/', '').lower()
        stream_id = f"binance_{binance_symbol}_orderbook"
        
        # Binance WebSocket URL
        ws_url = f"wss://stream.binance.com:9443/ws/{binance_symbol}@depth{depth}"
        
        # Create subscription
        subscription = StreamSubscription(
            stream_id=stream_id,
            symbol=symbol,
            exchange="binance",
            stream_type="orderbook",
            websocket=None,
            is_connected=False,
            reconnect_attempts=0,
            last_message_time=None
        )
        
        self.subscriptions[stream_id] = subscription
        self.callbacks[stream_id] = callback
        
        # Start connection task
        asyncio.create_task(self._maintain_connection(stream_id, ws_url))
        
        logger.info(f"Subscribed to Binance orderbook: {symbol} (stream_id: {stream_id})")
        return stream_id
    
    async def subscribe_binance_ticker(
        self,
        symbol: str,
        callback: Callable[[Dict[str, Any]], None]
    ) -> str:
        """
        Subscribe to Binance ticker WebSocket stream.
        
        Args:
            symbol: Trading pair (e.g., 'BTC/USDT')
            callback: Function to call with ticker updates
            
        Returns:
            stream_id: Unique identifier for this subscription
        """
        binance_symbol = symbol.replace('/', '').lower()
        stream_id = f"binance_{binance_symbol}_ticker"
        
        ws_url = f"wss://stream.binance.com:9443/ws/{binance_symbol}@ticker"
        
        subscription = StreamSubscription(
            stream_id=stream_id,
            symbol=symbol,
            exchange="binance",
            stream_type="ticker",
            websocket=None,
            is_connected=False,
            reconnect_attempts=0,
            last_message_time=None
        )
        
        self.subscriptions[stream_id] = subscription
        self.callbacks[stream_id] = callback
        
        asyncio.create_task(self._maintain_connection(stream_id, ws_url))
        
        logger.info(f"Subscribed to Binance ticker: {symbol} (stream_id: {stream_id})")
        return stream_id
    
    async def _maintain_connection(self, stream_id: str, ws_url: str):
        """
        Maintain WebSocket connection with auto-reconnection.
        
        Args:
            stream_id: Subscription identifier
            ws_url: WebSocket URL
        """
        subscription = self.subscriptions.get(stream_id)
        if not subscription:
            return
        
        while subscription.reconnect_attempts < self.max_reconnect_attempts:
            try:
                async with websockets.connect(ws_url) as websocket:
                    subscription.websocket = websocket
                    subscription.is_connected = True
                    subscription.reconnect_attempts = 0
                    
                    logger.info(f"Connected to {stream_id}")
                    
                    # Message receiving loop
                    async for message in websocket:
                        try:
                            data = json.loads(message)
                            normalized = self._normalize_message(data, subscription)
                            
                            # Update last message time
                            subscription.last_message_time = datetime.now()
                            
                            # Call callback
                            if stream_id in self.callbacks:
                                self.callbacks[stream_id](normalized)
                                
                        except json.JSONDecodeError as e:
                            logger.error(f"JSON decode error in {stream_id}: {e}")
                        except Exception as e:
                            logger.error(f"Callback error in {stream_id}: {e}")
                            
            except ConnectionClosed:
                subscription.is_connected = False
                subscription.reconnect_attempts += 1
                
                # Exponential backoff
                backoff = min(2 ** subscription.reconnect_attempts, 32)
                logger.warning(
                    f"Connection closed for {stream_id}. "
                    f"Reconnecting in {backoff}s (attempt {subscription.reconnect_attempts})"
                )
                await asyncio.sleep(backoff)
                
            except Exception as e:
                subscription.is_connected = False
                subscription.reconnect_attempts += 1
                logger.error(f"Error in {stream_id}: {e}")
                await asyncio.sleep(5)
        
        logger.error(f"Max reconnect attempts reached for {stream_id}")
        subscription.is_connected = False
    
    def _normalize_message(
        self,
        data: Dict[str, Any],
        subscription: StreamSubscription
    ) -> Dict[str, Any]:
        """
        Normalize exchange-specific message format to unified format.
        
        Args:
            data: Raw WebSocket message
            subscription: Stream subscription info
            
        Returns:
            Normalized message dictionary
        """
        if subscription.exchange == "binance":
            if subscription.stream_type == "orderbook":
                # Binance depth update format
                return {
                    "type": "orderbook",
                    "symbol": subscription.symbol,
                    "exchange": "binance",
                    "bids": [[float(p), float(q)] for p, q in data.get("b", [])],
                    "asks": [[float(p), float(q)] for p, q in data.get("a", [])],
                    "timestamp": data.get("E", int(datetime.now().timestamp() * 1000)),
                    "raw": data
                }
            elif subscription.stream_type == "ticker":
                # Binance ticker format
                return {
                    "type": "ticker",
                    "symbol": subscription.symbol,
                    "exchange": "binance",
                    "last_price": float(data.get("c", 0)),
                    "volume_24h": float(data.get("v", 0)),
                    "price_change_24h_percent": float(data.get("P", 0)),
                    "high_24h": float(data.get("h", 0)),
                    "low_24h": float(data.get("l", 0)),
                    "timestamp": data.get("E", int(datetime.now().timestamp() * 1000))
                }
        
        # Fallback: return raw data
        return {
            "type": "unknown",
            "symbol": subscription.symbol,
            "exchange": subscription.exchange,
            "raw": data
        }
    
    async def unsubscribe(self, stream_id: str):
        """
        Unsubscribe from a WebSocket stream.
        
        Args:
            stream_id: Stream identifier to close
        """
        subscription = self.subscriptions.get(stream_id)
        if not subscription:
            logger.warning(f"Stream {stream_id} not found")
            return
        
        if subscription.websocket and subscription.is_connected:
            await subscription.websocket.close()
        
        del self.subscriptions[stream_id]
        if stream_id in self.callbacks:
            del self.callbacks[stream_id]
        
        logger.info(f"Unsubscribed from {stream_id}")
    
    def get_active_streams(self) -> Dict[str, Dict[str, Any]]:
        """
        Get status of all active WebSocket streams.
        
        Returns:
            Dictionary of stream statuses
        """
        return {
            stream_id: {
                "symbol": sub.symbol,
                "exchange": sub.exchange,
                "type": sub.stream_type,
                "connected": sub.is_connected,
                "reconnect_attempts": sub.reconnect_attempts,
                "last_message": sub.last_message_time.isoformat() if sub.last_message_time else None
            }
            for stream_id, sub in self.subscriptions.items()
        }
    
    def get_stream_status(self, stream_id: str) -> Optional[Dict[str, Any]]:
        """
        Get status of a specific stream.
        
        Args:
            stream_id: Stream identifier
            
        Returns:
            Stream status dictionary or None if not found
        """
        subscription = self.subscriptions.get(stream_id)
        if not subscription:
            return None
        
        return {
            "stream_id": stream_id,
            "symbol": subscription.symbol,
            "exchange": subscription.exchange,
            "type": subscription.stream_type,
            "connected": subscription.is_connected,
            "reconnect_attempts": subscription.reconnect_attempts,
            "last_message_time": subscription.last_message_time.isoformat() 
                if subscription.last_message_time else None
        }


# Global WebSocket manager instance
ws_manager = WebSocketManager()
