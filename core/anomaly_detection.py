"""
Market Anomaly Detection Module

This module provides market manipulation and anomaly detection,
adapted from the Genesis2025 HFT platform for use with MCP.

Detection capabilities:
- Spoofing: Large fake orders intended to move price
- Layering: Multiple fake orders at different price levels
- Liquidity gaps: Price levels with insufficient volume
- Market regime classification: Calm, Stressed, Execution Hot
- Heavy imbalance detection
- Spread shock detection
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from enum import Enum
from collections import deque
import math

from .analytics import OrderBook, OrderBookLevel


class AnomalySeverity(Enum):
    """Severity levels for detected anomalies."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AnomalyType(Enum):
    """Types of market anomalies."""
    SPOOFING = "SPOOFING"
    LAYERING = "LAYERING"
    LIQUIDITY_GAP = "LIQUIDITY_GAP"
    HEAVY_IMBALANCE = "HEAVY_IMBALANCE"
    SPREAD_SHOCK = "SPREAD_SHOCK"
    QUOTE_STUFFING = "QUOTE_STUFFING"
    MOMENTUM_IGNITION = "MOMENTUM_IGNITION"
    WASH_TRADING = "WASH_TRADING"


class MarketRegime(Enum):
    """Market regime classifications."""
    CALM = "Calm"
    STRESSED = "Stressed"
    EXECUTION_HOT = "Execution Hot"
    MANIPULATION_SUSPECTED = "Manipulation Suspected"


@dataclass
class Anomaly:
    """Represents a detected market anomaly."""
    type: AnomalyType
    severity: AnomalySeverity
    message: str
    timestamp: datetime = field(default_factory=datetime.now)
    risk_score: float = 0.0
    details: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "type": self.type.value,
            "severity": self.severity.value,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
            "risk_score": round(self.risk_score, 1),
            **self.details
        }


@dataclass
class MarketState:
    """Current market state assessment."""
    regime: MarketRegime
    anomalies: List[Anomaly]
    overall_risk_score: float
    spoofing_risk: float
    liquidity_score: float
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "regime": self.regime.value,
            "anomalies": [a.to_dict() for a in self.anomalies],
            "overall_risk_score": round(self.overall_risk_score, 1),
            "spoofing_risk": round(self.spoofing_risk, 1),
            "liquidity_score": round(self.liquidity_score, 1)
        }


class AnomalyDetector:
    """
    Detects market anomalies and manipulation patterns.
    
    This detector identifies:
    - Spoofing: Large orders that appear/disappear rapidly
    - Layering: Multiple large orders stacked on one side
    - Liquidity gaps: Price levels with insufficient volume
    - Heavy imbalance: Extreme bid/ask volume skew
    - Spread shocks: Sudden spread widening
    
    Adapted from Genesis2025 HFT platform.
    """
    
    def __init__(
        self,
        spoofing_volume_threshold: float = 5.0,
        liquidity_gap_threshold: float = 50.0,
        imbalance_threshold: float = 0.7,
        spread_shock_multiplier: float = 3.0,
        ewma_alpha: float = 0.05
    ):
        """
        Initialize the detector.
        
        Args:
            spoofing_volume_threshold: Multiplier of avg volume for spoofing detection
            liquidity_gap_threshold: Minimum volume for adequate liquidity
            imbalance_threshold: OBI threshold for heavy imbalance alert
            spread_shock_multiplier: Multiplier of avg spread for shock detection
            ewma_alpha: Smoothing factor for rolling averages
        """
        self.spoofing_volume_threshold = spoofing_volume_threshold
        self.liquidity_gap_threshold = liquidity_gap_threshold
        self.imbalance_threshold = imbalance_threshold
        self.spread_shock_multiplier = spread_shock_multiplier
        self.ewma_alpha = ewma_alpha
        
        # Rolling statistics
        self._avg_spread: float = 0.0
        self._avg_spread_sq: float = 0.0
        self._avg_l1_volume: float = 100.0
        
        # State tracking
        self._prev_book: Optional[OrderBook] = None
        self._order_timestamps: deque = deque(maxlen=100)
        self._price_history: deque = deque(maxlen=50)
        self._spoofing_events: int = 0
        
    def analyze(self, book: OrderBook) -> MarketState:
        """
        Analyze order book for anomalies and determine market regime.
        
        Args:
            book: OrderBook snapshot to analyze
            
        Returns:
            MarketState containing regime and detected anomalies
        """
        if not book.bids or not book.asks:
            return MarketState(
                regime=MarketRegime.CALM,
                anomalies=[],
                overall_risk_score=0,
                spoofing_risk=0,
                liquidity_score=100
            )
        
        anomalies: List[Anomaly] = []
        current_time = book.timestamp or datetime.now()
        
        # Update rolling statistics
        self._update_statistics(book)
        
        # Store price for momentum detection
        if book.mid_price:
            self._price_history.append(book.mid_price)
        
        # Run detectors
        spoofing_anomaly = self._detect_spoofing(book, current_time)
        if spoofing_anomaly:
            anomalies.append(spoofing_anomaly)
        
        layering_anomaly = self._detect_layering(book, current_time)
        if layering_anomaly:
            anomalies.append(layering_anomaly)
        
        gap_anomalies = self._detect_liquidity_gaps(book, current_time)
        anomalies.extend(gap_anomalies)
        
        imbalance_anomaly = self._detect_heavy_imbalance(book, current_time)
        if imbalance_anomaly:
            anomalies.append(imbalance_anomaly)
        
        spread_anomaly = self._detect_spread_shock(book, current_time)
        if spread_anomaly:
            anomalies.append(spread_anomaly)
        
        # Calculate risk scores
        spoofing_risk = self._calculate_spoofing_risk(book)
        liquidity_score = self._calculate_liquidity_score(book)
        overall_risk = self._calculate_overall_risk(anomalies, spoofing_risk, liquidity_score)
        
        # Determine regime
        regime = self._classify_regime(anomalies, overall_risk)
        
        # Update state
        self._prev_book = book
        
        return MarketState(
            regime=regime,
            anomalies=anomalies,
            overall_risk_score=overall_risk,
            spoofing_risk=spoofing_risk,
            liquidity_score=liquidity_score
        )
    
    def _update_statistics(self, book: OrderBook) -> None:
        """Update rolling EWMA statistics."""
        spread = book.spread or 0
        l1_volume = (book.bids[0].volume + book.asks[0].volume) / 2
        
        self._avg_spread = (1 - self.ewma_alpha) * self._avg_spread + self.ewma_alpha * spread
        self._avg_spread_sq = (1 - self.ewma_alpha) * self._avg_spread_sq + self.ewma_alpha * (spread ** 2)
        self._avg_l1_volume = (1 - self.ewma_alpha) * self._avg_l1_volume + self.ewma_alpha * l1_volume
    
    def _detect_spoofing(self, book: OrderBook, timestamp: datetime) -> Optional[Anomaly]:
        """
        Detect spoofing - large orders significantly larger than normal.
        
        Real spoofing involves orders that are placed and cancelled quickly,
        but we can still flag unusually large orders as potential spoofing.
        """
        threshold = self._avg_l1_volume * self.spoofing_volume_threshold
        
        for side, levels in [("BID", book.bids), ("ASK", book.asks)]:
            for i, level in enumerate(levels[:5]):
                if level.volume > threshold:
                    risk_score = min(100, (level.volume / threshold) * 50)
                    self._spoofing_events += 1
                    
                    return Anomaly(
                        type=AnomalyType.SPOOFING,
                        severity=AnomalySeverity.HIGH if risk_score > 70 else AnomalySeverity.MEDIUM,
                        message=f"Large {side.lower()} order at level {i+1}: {level.volume:.0f} (avg: {self._avg_l1_volume:.0f})",
                        timestamp=timestamp,
                        risk_score=risk_score,
                        details={
                            "side": side,
                            "level": i + 1,
                            "price": level.price,
                            "volume": level.volume,
                            "avg_volume": self._avg_l1_volume
                        }
                    )
        
        return None
    
    def _detect_layering(self, book: OrderBook, timestamp: datetime) -> Optional[Anomaly]:
        """Detect layering - multiple large orders stacked on one side."""
        threshold = self._avg_l1_volume * 2
        
        bid_large_count = sum(1 for b in book.bids[:5] if b.volume > threshold)
        ask_large_count = sum(1 for a in book.asks[:5] if a.volume > threshold)
        
        # Layering requires imbalance in large order count
        if bid_large_count >= 3 and bid_large_count > ask_large_count + 2:
            score = min(100, bid_large_count * 20)
            return Anomaly(
                type=AnomalyType.LAYERING,
                severity=AnomalySeverity.CRITICAL if score > 70 else AnomalySeverity.HIGH,
                message=f"Layering detected: {bid_large_count} large orders on BID side",
                timestamp=timestamp,
                risk_score=score,
                details={"side": "BID", "large_order_count": bid_large_count}
            )
        
        if ask_large_count >= 3 and ask_large_count > bid_large_count + 2:
            score = min(100, ask_large_count * 20)
            return Anomaly(
                type=AnomalyType.LAYERING,
                severity=AnomalySeverity.CRITICAL if score > 70 else AnomalySeverity.HIGH,
                message=f"Layering detected: {ask_large_count} large orders on ASK side",
                timestamp=timestamp,
                risk_score=score,
                details={"side": "ASK", "large_order_count": ask_large_count}
            )
        
        return None
    
    def _detect_liquidity_gaps(self, book: OrderBook, timestamp: datetime) -> List[Anomaly]:
        """Detect price levels with insufficient liquidity."""
        anomalies = []
        
        for side, levels in [("bid", book.bids), ("ask", book.asks)]:
            for i, level in enumerate(levels[:10]):
                if level.volume < self.liquidity_gap_threshold:
                    risk_score = min(100, (10 - i) * 15 + (self.liquidity_gap_threshold - level.volume) * 2)
                    
                    anomalies.append(Anomaly(
                        type=AnomalyType.LIQUIDITY_GAP,
                        severity=AnomalySeverity.MEDIUM if i > 3 else AnomalySeverity.HIGH,
                        message=f"Liquidity gap at {side} level {i+1}: {level.volume:.0f}",
                        timestamp=timestamp,
                        risk_score=risk_score,
                        details={
                            "side": side,
                            "level": i + 1,
                            "price": level.price,
                            "volume": level.volume
                        }
                    ))
        
        return anomalies[:5]  # Limit to top 5 gaps
    
    def _detect_heavy_imbalance(self, book: OrderBook, timestamp: datetime) -> Optional[Anomaly]:
        """Detect extreme order book imbalance."""
        total_bid = sum(b.volume for b in book.bids[:5])
        total_ask = sum(a.volume for a in book.asks[:5])
        total = total_bid + total_ask
        
        if total < 1e-9:
            return None
        
        imbalance = (total_bid - total_ask) / total
        
        if abs(imbalance) > self.imbalance_threshold:
            side = "BID" if imbalance > 0 else "ASK"
            risk_score = min(100, abs(imbalance) * 100)
            
            return Anomaly(
                type=AnomalyType.HEAVY_IMBALANCE,
                severity=AnomalySeverity.HIGH,
                message=f"Heavy {side.lower()} imbalance: {imbalance:.1%}",
                timestamp=timestamp,
                risk_score=risk_score,
                details={
                    "side": side,
                    "imbalance": imbalance,
                    "bid_depth": total_bid,
                    "ask_depth": total_ask
                }
            )
        
        return None
    
    def _detect_spread_shock(self, book: OrderBook, timestamp: datetime) -> Optional[Anomaly]:
        """Detect sudden spread widening."""
        spread = book.spread or 0
        
        # Calculate spread standard deviation
        std_spread = math.sqrt(max(0, self._avg_spread_sq - self._avg_spread ** 2))
        
        if std_spread > 0:
            z_score = (spread - self._avg_spread) / std_spread
            
            if z_score > self.spread_shock_multiplier:
                risk_score = min(100, z_score * 20)
                
                return Anomaly(
                    type=AnomalyType.SPREAD_SHOCK,
                    severity=AnomalySeverity.HIGH if z_score > 5 else AnomalySeverity.MEDIUM,
                    message=f"Spread shock: {spread:.4f} (z-score: {z_score:.1f})",
                    timestamp=timestamp,
                    risk_score=risk_score,
                    details={
                        "current_spread": spread,
                        "avg_spread": self._avg_spread,
                        "z_score": z_score
                    }
                )
        
        return None
    
    def _calculate_spoofing_risk(self, book: OrderBook) -> float:
        """Calculate overall spoofing risk score (0-100)."""
        max_bid_vol = max(b.volume for b in book.bids[:5]) if book.bids else 0
        max_ask_vol = max(a.volume for a in book.asks[:5]) if book.asks else 0
        max_vol = max(max_bid_vol, max_ask_vol)
        
        if self._avg_l1_volume > 0:
            ratio = max_vol / self._avg_l1_volume
            return min(100, (ratio - 1) * 25) if ratio > 1 else 0
        
        return 0
    
    def _calculate_liquidity_score(self, book: OrderBook) -> float:
        """Calculate liquidity score (0-100, higher is better)."""
        total_depth = sum(b.volume for b in book.bids[:5]) + sum(a.volume for a in book.asks[:5])
        spread_bps = book.spread_bps or 100
        
        # Score based on depth and spread
        depth_score = min(50, total_depth / 100)
        spread_score = max(0, 50 - spread_bps)
        
        return depth_score + spread_score
    
    def _calculate_overall_risk(self, anomalies: List[Anomaly], 
                                 spoofing_risk: float, liquidity_score: float) -> float:
        """Calculate overall market risk score."""
        base_risk = 100 - liquidity_score
        
        anomaly_risk = sum(a.risk_score for a in anomalies) / 5  # Normalize
        
        return min(100, base_risk * 0.3 + anomaly_risk * 0.4 + spoofing_risk * 0.3)
    
    def _classify_regime(self, anomalies: List[Anomaly], overall_risk: float) -> MarketRegime:
        """Classify current market regime based on analysis."""
        critical_count = sum(1 for a in anomalies if a.severity == AnomalySeverity.CRITICAL)
        high_count = sum(1 for a in anomalies if a.severity == AnomalySeverity.HIGH)
        
        if critical_count >= 2 or any(a.type in [AnomalyType.SPOOFING, AnomalyType.LAYERING] for a in anomalies):
            return MarketRegime.MANIPULATION_SUSPECTED
        
        if overall_risk > 70 or high_count >= 3:
            return MarketRegime.STRESSED
        
        if overall_risk > 40:
            return MarketRegime.EXECUTION_HOT
        
        return MarketRegime.CALM
    
    def reset(self) -> None:
        """Reset all internal state."""
        self._avg_spread = 0.0
        self._avg_spread_sq = 0.0
        self._avg_l1_volume = 100.0
        self._prev_book = None
        self._order_timestamps.clear()
        self._price_history.clear()
        self._spoofing_events = 0
