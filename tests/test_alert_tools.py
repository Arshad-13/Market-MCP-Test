"""
Verification Tests for Phase 10 (Smart Notifications)
Tests background monitor and alert tools.
"""

import sys
import os
import json
import asyncio
from unittest.mock import MagicMock

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock mcp module
sys.modules["mcp"] = MagicMock()
sys.modules["mcp.server"] = MagicMock()
sys.modules["mcp.server.fastmcp"] = MagicMock()

class MockFastMCP:
    def __init__(self):
        self.tools = {}
    
    def tool(self):
        def decorator(func):
            self.tools[func.__name__] = func
            return func
        return decorator

sys.modules["mcp.server.fastmcp"].FastMCP = MockFastMCP

# Mock ccxt to prevent ImportError from tools/__init__.py
mock_ccxt = MagicMock()
sys.modules["ccxt"] = mock_ccxt
sys.modules["ccxt.async_support"] = mock_ccxt

from tools.alert_tools import register_alert_tools
from core.background_service import monitor

async def test_phase10():
    print("\n--- Testing Phase 10: Smart Notifications ---")
    mock_mcp = MockFastMCP()
    register_alert_tools(mock_mcp)
    
    check_alerts = mock_mcp.tools["check_alerts"]
    create_alert = mock_mcp.tools["create_price_alert"]
    mark_read = mock_mcp.tools["mark_alerts_read"]
    
    # 1. Create an Alert
    print("Testing create_price_alert...")
    res_create = json.loads(create_alert("BTC", 100000.0, "ABOVE"))
    print(f"Creation Result: {res_create['message']}")
    assert res_create["status"] == "created"
    print("Create Alert: PASS")
    
    # 2. Check Alerts (and verify lazy start)
    print("\nTesting check_alerts...")
    # This should trigger monitor.start()
    res_check_json = await check_alerts(unread_only=True)
    res_check = json.loads(res_check_json)
    
    print(f"Alerts Found: {res_check['count']}")
    
    # We expect at least the one we just created (create_price_alert mock logic adds to system alerts)
    # create_price_alert implementation: monitor.add_alert(...)
    assert res_check["count"] >= 1
    assert res_check["alerts"][0]["symbol"] == "SYSTEM" # The mock tool logs it as SYSTEM
    print("Check Alerts: PASS")
    
    # 3. Mark Read
    print("\nTesting mark_alerts_read...")
    mark_read()
    
    # Check again (should be 0 unread)
    res_check_again = json.loads(await check_alerts(unread_only=True))
    print(f"Unread after marking: {res_check_again['count']}")
    
    assert res_check_again["count"] == 0
    print("Mark Read: PASS")
    
    # 4. Stop Monitor
    await monitor.stop()
    print("Monitor Stopped: PASS")

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(test_phase10())
    print("\nAll Phase 10 Tests Passed!")
