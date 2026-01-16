"""
Market Microstructure Analytics Module

This module provides core market microstructure analysis functionality,
adapted from the Genesis2025 HFT platform for use with MCP.

Features:
- Order Flow Imbalance (OFI)
- Order Book Imbalance (OBI)
- Microprice calculation
- VPIN (Volume-Synchronized Probability of Informed Trading)
- Spread analysis
- Volatility metrics
- Market regime classification
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from collections import deque
import math


@dataclass
class OrderBookLevel:
    """Represents a single level in the order book."""
    price: float
    volume: float


@dataclass
class OrderBook:
    """Represents an L2 order book snapshot."""
    bids: List[OrderBookLevel]
    asks: List[OrderBookLevel]
    timestamp: Optional[datetime] = None
    
    @property
    def best_bid(self) -> Optional[OrderBookLevel]:
        """Get best bid (highest bid price)."""
        return self.bids[0] if self.bids else None
    
    @property
    def best_ask(self) -> Optional[OrderBookLevel]:
        """Get best ask (lowest ask price)."""
        return self.asks[0] if self.asks else None
    
    @property
    def mid_price(self) -> Optional[float]:
        """Calculate mid-price."""
        if self.best_bid and self.best_ask:
            return (self.best_bid.price + self.best_ask.price) / 2
        return None
    
    @property
    def spread(self) -> Optional[float]:
        """Calculate bid-ask spread."""
        if self.best_bid and self.best_ask:
            return self.best_ask.price - self.best_bid.price
        return None
    
    @property
    def spread_bps(self) -> Optional[float]:
        """Calculate spread in basis points."""
        if self.spread and self.mid_price:
            return (self.spread / self.mid_price) * 10000
        return None
    
    @classmethod
    def from_raw(cls, bids: List[List[float]], asks: List[List[float]], 
                 timestamp: Optional[datetime] = None) -> "OrderBook":
        """Create OrderBook from raw [price, volume] lists."""
        return cls(
            bids=[OrderBookLevel(price=b[0], volume=b[1]) for b in bids],
            asks=[OrderBookLevel(price=a[0], volume=a[1]) for a in asks],
            timestamp=timestamp
        )


@dataclass
class MicrostructureMetrics:
    """Container for calculated microstructure metrics."""
    mid_price: float
    spread: float
    spread_bps: float
    ofi: float  # Order Flow Imbalance
    obi: float  # Order Book Imbalance
    microprice: float
    microprice_divergence: float
    directional_probability: float  # Probability of price moving up (0-100%)
    total_bid_depth: float
    total_ask_depth: float
    depth_imbalance: float
    volatility: Optional[float] = None
    vpin: Optional[float] = None


class MicrostructureAnalyzer:
    """
    Analyzes market microstructure from order book data.
    
    Provides real-time calculation of:
    - Order Flow Imbalance (OFI): Measures aggressive buying/selling pressure
    - Order Book Imbalance (OBI): Volume-weighted bid/ask imbalance
    - Microprice: Volume-weighted fair price estimation
    - VPIN: Probability of informed trading
    
    Adapted from Genesis2025 HFT platform.
    """
    
    def __init__(
        self,
        ofi_window: int = 50,
        price_history_size: int = 100,
        vpin_bucket_size: float = 1000.0,
        decay_factor: float = 0.5
    ):
        """
        Initialize the analyzer.
        
        Args:
            ofi_window: Number of snapshots for OFI normalization
            price_history_size: Size of price history for volatility calculation
            vpin_bucket_size: Volume threshold for VPIN bucket completion
            decay_factor: Decay factor for OBI level weighting
        """
        self.ofi_window = ofi_window
        self.price_history_size = price_history_size
        self.vpin_bucket_size = vpin_bucket_size
        self.decay_factor = decay_factor
        
        # State for OFI calculation
        self._prev_best_bid: Optional[float] = None
        self._prev_best_ask: Optional[float] = None
        self._prev_bid_qty: float = 0
        self._prev_ask_qty: float = 0
        self._ofi_history: deque = deque(maxlen=ofi_window)
        
        # State for volatility
        self._price_history: deque = deque(maxlen=price_history_size)
        
        # State for VPIN
        self._current_bucket_volume: float = 0
        self._current_bucket_buys: float = 0
        self._current_bucket_sells: float = 0
        self._bucket_imbalances: deque = deque(maxlen=50)
    
    def analyze(self, book: OrderBook) -> MicrostructureMetrics:
        """
        Analyze an order book snapshot and return microstructure metrics.
        
        Args:
            book: OrderBook snapshot to analyze
            
        Returns:
            MicrostructureMetrics containing all calculated metrics
        """
        if not book.bids or not book.asks:
            raise ValueError("Order book must have at least one level on each side")
        
        best_bid = book.best_bid
        best_ask = book.best_ask
        mid_price = book.mid_price
        spread = book.spread
        
        # Calculate OFI
        ofi = self._calculate_ofi(best_bid, best_ask)
        
        # Calculate OBI (weighted by level distance)
        obi = self._calculate_obi(book)
        
        # Calculate Microprice
        microprice = self._calculate_microprice(best_bid, best_ask)
        
        # Calculate divergence and directional probability
        divergence = microprice - mid_price
        # Use tick size approximation for normalization
        tick_size = spread / 10 if spread > 0 else 0.01
        divergence_score = divergence / tick_size if tick_size > 0 else 0
        directional_prob = 100 / (1 + math.exp(-2 * divergence_score))
        
        # Calculate total depths
        total_bid_depth = sum(level.volume for level in book.bids)
        total_ask_depth = sum(level.volume for level in book.asks)
        depth_imbalance = (total_bid_depth - total_ask_depth) / (total_bid_depth + total_ask_depth) if (total_bid_depth + total_ask_depth) > 0 else 0
        
        # Update price history and calculate volatility
        self._price_history.append(mid_price)
        volatility = self._calculate_volatility()
        
        return MicrostructureMetrics(
            mid_price=round(mid_price, 6),
            spread=round(spread, 6),
            spread_bps=round(book.spread_bps, 2),
            ofi=round(ofi, 4),
            obi=round(obi, 4),
            microprice=round(microprice, 6),
            microprice_divergence=round(divergence, 6),
            directional_probability=round(directional_prob, 1),
            total_bid_depth=round(total_bid_depth, 2),
            total_ask_depth=round(total_ask_depth, 2),
            depth_imbalance=round(depth_imbalance, 4),
            volatility=round(volatility, 6) if volatility else None
        )
    
    def _calculate_ofi(self, best_bid: OrderBookLevel, best_ask: OrderBookLevel) -> float:
        """
        Calculate Order Flow Imbalance.
        
        OFI measures the net order flow based on changes in top-of-book.
        Positive OFI indicates buying pressure, negative indicates selling pressure.
        """
        ofi = 0.0
        
        if self._prev_best_bid is not None:
            # Bid side contribution
            if best_bid.price > self._prev_best_bid:
                ofi += best_bid.volume
            elif best_bid.price < self._prev_best_bid:
                ofi -= self._prev_bid_qty
            else:
                ofi += (best_bid.volume - self._prev_bid_qty)
            
            # Ask side contribution (inverted)
            if best_ask.price > self._prev_best_ask:
                ofi += self._prev_ask_qty
            elif best_ask.price < self._prev_best_ask:
                ofi -= best_ask.volume
            else:
                ofi -= (best_ask.volume - self._prev_ask_qty)
        
        # Update state
        self._prev_best_bid = best_bid.price
        self._prev_best_ask = best_ask.price
        self._prev_bid_qty = best_bid.volume
        self._prev_ask_qty = best_ask.volume
        
        # Track for normalization
        self._ofi_history.append(abs(ofi))
        
        # Normalize OFI to [-1, 1]
        if self._ofi_history:
            max_ofi = max(self._ofi_history) if self._ofi_history else 1
            if max_ofi > 0:
                ofi = max(-1, min(1, ofi / max_ofi))
        
        return ofi
    
    def _calculate_obi(self, book: OrderBook, levels: int = 5) -> float:
        """
        Calculate weighted Order Book Imbalance.
        
        Levels closer to the top of book are weighted more heavily.
        Returns value in range [-1, 1], where positive indicates bid-heavy book.
        """
        weighted_bid = 0.0
        weighted_ask = 0.0
        total_weight = 0.0
        
        num_levels = min(levels, len(book.bids), len(book.asks))
        
        for i in range(num_levels):
            weight = math.exp(-self.decay_factor * i)
            weighted_bid += book.bids[i].volume * weight
            weighted_ask += book.asks[i].volume * weight
            total_weight += (book.bids[i].volume + book.asks[i].volume) * weight
        
        if total_weight < 1e-9:
            return 0.0
        
        return (weighted_bid - weighted_ask) / total_weight
    
    def _calculate_microprice(self, best_bid: OrderBookLevel, best_ask: OrderBookLevel) -> float:
        """
        Calculate volume-weighted microprice.
        
        Microprice is the volume-weighted average of bid and ask prices,
        providing a more accurate estimate of fair value than mid-price.
        """
        total_volume = best_bid.volume + best_ask.volume
        
        if total_volume < 1e-9:
            return (best_bid.price + best_ask.price) / 2
        
        # Weight each price by the OTHER side's volume
        # (if more volume on bid, price is closer to ask)
        return (best_bid.volume * best_ask.price + best_ask.volume * best_bid.price) / total_volume
    
    def _calculate_volatility(self, window: int = 20) -> Optional[float]:
        """
        Calculate rolling volatility from price history.
        
        Returns annualized volatility estimate or None if insufficient data.
        """
        if len(self._price_history) < window:
            return None
        
        prices = list(self._price_history)[-window:]
        
        # Calculate log returns
        log_returns = []
        for i in range(1, len(prices)):
            if prices[i-1] > 0 and prices[i] > 0:
                log_returns.append(math.log(prices[i] / prices[i-1]))
        
        if not log_returns:
            return None
        
        # Standard deviation of log returns
        mean_return = sum(log_returns) / len(log_returns)
        variance = sum((r - mean_return) ** 2 for r in log_returns) / len(log_returns)
        std_dev = math.sqrt(variance)
        
        return std_dev
    
    def update_vpin(self, trade_volume: float, is_buy: bool) -> Optional[float]:
        """
        Update VPIN calculation with a new trade.
        
        Args:
            trade_volume: Volume of the trade
            is_buy: True if buyer-initiated, False if seller-initiated
            
        Returns:
            Current VPIN value if bucket completed, None otherwise
        """
        if is_buy:
            self._current_bucket_buys += trade_volume
        else:
            self._current_bucket_sells += trade_volume
        
        self._current_bucket_volume += trade_volume
        
        # Check if bucket is complete
        if self._current_bucket_volume >= self.vpin_bucket_size:
            total = self._current_bucket_buys + self._current_bucket_sells
            if total > 0:
                imbalance = abs(self._current_bucket_buys - self._current_bucket_sells) / total
                self._bucket_imbalances.append(imbalance)
            
            # Reset bucket
            self._current_bucket_volume = 0
            self._current_bucket_buys = 0
            self._current_bucket_sells = 0
        
        # Calculate VPIN as average of recent imbalances
        if len(self._bucket_imbalances) >= 10:
            return sum(self._bucket_imbalances) / len(self._bucket_imbalances)
        
        return None
    
    def reset(self) -> None:
        """Reset all internal state."""
        self._prev_best_bid = None
        self._prev_best_ask = None
        self._prev_bid_qty = 0
        self._prev_ask_qty = 0
        self._ofi_history.clear()
        self._price_history.clear()
        self._current_bucket_volume = 0
        self._current_bucket_buys = 0
        self._current_bucket_sells = 0
        self._bucket_imbalances.clear()


def analyze_spread(bid_price: float, ask_price: float) -> Dict:
    """
    Compute market microstructure metrics based on bid and ask prices.
    
    This is a standalone function for quick spread analysis without
    requiring an OrderBook object.
    
    Args:
        bid_price: The highest price a buyer is willing to pay
        ask_price: The lowest price a seller is willing to accept
        
    Returns:
        Dictionary containing spread metrics and liquidity classification
    """
    if bid_price >= ask_price:
        return {
            "error": "Bid price must be lower than ask price",
            "valid": False
        }
    
    spread = ask_price - bid_price
    mid_price = (ask_price + bid_price) / 2
    spread_bps = (spread / mid_price) * 10000
    
    # Classify liquidity
    if spread_bps < 5:
        liquidity = "High"
    elif spread_bps < 20:
        liquidity = "Medium"
    else:
        liquidity = "Low"
    
    return {
        "valid": True,
        "spread_absolute": round(spread, 6),
        "mid_price": round(mid_price, 6),
        "spread_basis_points": round(spread_bps, 2),
        "liquidity_classification": liquidity
    }
