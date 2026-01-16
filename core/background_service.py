"""
Background Service for Market Intelligence
Runs a lightweight loop to monitor market conditions and generate alerts.
"""

import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

# Simple in-memory alert store
_ALERTS: List[Dict[str, Any]] = []
_WATCHLIST: List[str] = ["BTC", "ETH", "SOL"]

class MarketMonitor:
    def __init__(self):
        self._running = False
        self._task = None
        self.logger = logging.getLogger("MarketMonitor")
        
    async def start(self):
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._monitor_loop())
        self.logger.info("Market Monitor started.")

    async def stop(self):
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        self.logger.info("Market Monitor stopped.")

    async def _monitor_loop(self):
        """
        Main loop to check market conditions periodically.
        """
        while self._running:
            try:
                # In a real app, we would fetch prices here.
                # To avoid rate limits/spamming in this MCP demo, we keep it simple or strictly throttled.
                # For now, we just log a heartbeat or check a shared state if updated by tools.
                
                # Placeholder: If we had a mechanism to 'subscribe' to tools, we'd trigger them here.
                # For this Phase 10 demo, we'll demonstrate the ARCHITECTURE of a background service
                # that can be expanded.
                
                # Example check: Time-based alerts (just to prove it runs)
                now = datetime.now()
                if now.minute == 0 and now.second < 10:
                    self.add_alert("SYSTEM", "Hourly heartbeat check.")
                
                await asyncio.sleep(60) # FAST REFRESH FOR DEMO? No, 60s is safer.
                
            except Exception as e:
                self.logger.error(f"Error in monitor loop: {e}")
                await asyncio.sleep(60)

    def add_alert(self, symbol: str, message: str, severity: str = "INFO"):
        """
        Add an alert to the system.
        """
        alert = {
            "timestamp": datetime.now().isoformat(),
            "symbol": symbol,
            "message": message,
            "severity": severity,
            "read": False
        }
        _ALERTS.insert(0, alert)
        # Keep size manageable
        if len(_ALERTS) > 100:
            _ALERTS.pop()
            
    def get_alerts(self, unread_only: bool = False) -> List[Dict[str, Any]]:
        if unread_only:
            return [a for a in _ALERTS if not a["read"]]
        return _ALERTS

    def mark_all_read(self):
        for a in _ALERTS:
            a["read"] = True

# Global instance
monitor = MarketMonitor()
