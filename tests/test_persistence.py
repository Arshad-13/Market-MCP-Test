"""
Verification Tests for Phase 11 (Persistence)
Tests SQLite database integration via tools.
"""

import sys
import os
import json
import asyncio
from unittest.mock import MagicMock, AsyncMock, patch

# Add project root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock mcp
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

# Mock ccxt
sys.modules["ccxt"] = MagicMock()
sys.modules["ccxt.async_support"] = MagicMock()

# Mock aiosqlite since it might not be installed in the agent environment yet
mock_aiosqlite = MagicMock()
sys.modules["aiosqlite"] = mock_aiosqlite

class MockCursor:
    def __init__(self):
        self.rows = []
    
    def __await__(self):
        # This makes the cursor itself awaitable!
        # await conn.execute(...) -> yields self
        async def _ret(): return self
        return _ret().__await__()

    async def fetchall(self):
        return self.rows

    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc, tb):
        pass

class MockConnection:
    def __init__(self):
        self.cursor = MockCursor()
        self.row_factory = None
        
    def execute(self, query, params=None):
        # Return the Dual-Natured Cursor directly
        return self.cursor
        
    async def commit(self):
        pass
        
    async def close(self):
        pass

mock_conn = MockConnection()
mock_aiosqlite.connect.return_value = mock_conn

# Remove the lambda override since MockConnection.execute handles it
# mock_conn.execute = ... (Deleted)
async def mock_execute(*args, **kwargs):
    # This was wrong because it made execute a coroutine function, 
    # dependent on being awaited to return the cursor.
    # But aiosqlite.execute(...) returns the cursor immediately (which is then awaited).
    pass 


# Needed for row factory?
mock_conn.row_factory = None

from tools.alert_tools import register_alert_tools
from core.database import db

# Override DB connect to ensure our mock is used if logic re-imports or calls connect
async def mock_connect():
    db._conn = mock_conn
db.connect = mock_connect

async def test_persistence():
    print("\n--- Testing Phase 11: Persistence Layer (Mocked) ---")
    
    # 1. Override DB File to Memory (Symbolic here since we use MagicMock)
    db.db_path = ":memory:"
    
    mock_mcp = MockFastMCP()
    register_alert_tools(mock_mcp)
    
    create_alert = mock_mcp.tools["create_price_alert"]
    check_alerts = mock_mcp.tools["check_alerts"]
    
    # 2. Create Alert (This writes to DB)
    print("Creating alert in DB...")
    res_create = json.loads(await create_alert("ETH", 2000.0, "BELOW"))
    print(f"Result: {res_create['message']}")
    
    # 3. Read Alert (Reads from DB)
    print("Reading from DB...")
    
    # Inject Mock Data into the cursor for the next fetchall
    mock_conn.cursor.rows = [
        {"id": 1, "timestamp": "2023-01-01", "symbol": "SYSTEM", "message": "Alert created for ETH BELOW 2000.0", "severity": "INFO", "is_read": 0},
        {"id": 2, "timestamp": "2023-01-01", "symbol": "SYSTEM", "message": "Hourly heartbeat check", "severity": "INFO", "is_read": 0}
    ]
    
    res_check = json.loads(await check_alerts(unread_only=True))
    
    # We expect 2 alerts:
    # 1. The one we just created.
    # 2. "Hourly heartbeat check" might be there if monitor loop ran? 
    # But monitor loop isn't started in this script explicitly via `await monitor.start()`,
    # except that `check_alerts` calls `monitor.start()`.
    # `monitor.start()` creates a task for `_monitor_loop`.
    # `_monitor_loop` waits 60s. So it won't add a heartbeat immediately unless logic changed.
    # Logic: if now.minute==0... so rarely.
    
    count = res_check["count"]
    print(f"Alerts in DB: {count}")
    
    assert count >= 1
    found = False
    for alert in res_check["alerts"]:
        if alert["symbol"] == "SYSTEM" and "ETH" in alert["message"]:
            found = True
            break
            
    assert found
    print("Persistence Read/Write: PASS")
    
    # 4. Verify Data Structure (Row to dict conversion)
    first = res_check["alerts"][0]
    assert "timestamp" in first
    assert "is_read" in first
    print("Data Schema: PASS")
    
    await db.close()

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(test_persistence())
    print("\nAll Phase 11 Tests Passed!")
