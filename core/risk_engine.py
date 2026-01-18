"""
Risk Management Engine

Acts as a safety layer before any trade execution.
Enforces limits on trade size, daily loss, and restricted assets.
"""

import logging
from typing import Tuple, Optional

logger = logging.getLogger("RiskEngine")

class RiskEngine:
    def __init__(self):
        # Configuration (Could be loaded from env/db)
        self.MAX_TRADE_SIZE_USD = 100000.0
        self.MAX_DAILY_LOSS_USD = 5000.0
        self.RESTRICTED_ASSETS = ["USDT", "USDC"] # Don't trade stablecoins as speculative assets
        
        # State (In-memory for now, ideally DB backed)
        self.daily_loss_current = 0.0

    def check_order(self, symbol: str, side: str, quantity: float, price: float) -> Tuple[bool, str]:
        """
        Validate an order against risk rules.
        
        Returns:
            (Allowed: bool, Reason: str)
        """
        if symbol in self.RESTRICTED_ASSETS:
            return False, f"Trading restricted for asset: {symbol}"
            
        trade_value = quantity * price
        
        if trade_value > self.MAX_TRADE_SIZE_USD:
            return False, f"Trade value ${trade_value:.2f} exceeds limit ${self.MAX_TRADE_SIZE_USD}"
            
        if self.daily_loss_current >= self.MAX_DAILY_LOSS_USD:
            return False, "Daily loss limit reached. Trading halted."
            
        # Additional checks (e.g. max position size) could go here
        
        return True, "Risk checks passed"

    def record_loss(self, loss_amount: float):
        """Update daily loss metric."""
        self.daily_loss_current += loss_amount
        if self.daily_loss_current >= self.MAX_DAILY_LOSS_USD:
            logger.warning("Daily loss limit breached!")

risk_engine = RiskEngine()
