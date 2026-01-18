"""
Background Service for Market Intelligence
Runs a lightweight loop to monitor market conditions and generate alerts.
"""

import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

from core.database import db

# Simple in-memory alert store REMOVED in favor of SQLite
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
                    await self.add_alert("SYSTEM", "Hourly heartbeat check.")
                
                await asyncio.sleep(60) # FAST REFRESH FOR DEMO? No, 60s is safer.
                
            except Exception as e:
                self.logger.error(f"Error in monitor loop: {e}")
                await asyncio.sleep(60)

    async def add_alert(self, symbol: str, message: str, severity: str = "INFO"):
        """
        Add an alert to the system (Persistent).
        """
        try:
            await db.add_alert(symbol, message, severity)
        except Exception as e:
            self.logger.error(f"Failed to persist alert: {e}")

    # get_alerts and mark_all_read Removed from Monitor to decouple.
    # Tools should access DB directly or via this service wrapper if preferred.
    # To keep tools simple, we will keep wrappers but delegate to DB.
    
    async def get_alerts(self, unread_only: bool = False) -> List[Dict[str, Any]]:
        return await db.get_alerts(unread_only)

    async def mark_all_read(self):
        await db.mark_all_read()

# Global instance
monitor = MarketMonitor()
