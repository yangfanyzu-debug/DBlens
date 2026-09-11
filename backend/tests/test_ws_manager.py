import unittest
import sys
import types
from decimal import Decimal


class FakeWebSocket:
    def __init__(self):
        self.accepted = False
        self.sent = []

    async def accept(self):
        self.accepted = True

    async def send_text(self, text):
        self.sent.append(text)


class WSManagerTestCase(unittest.IsolatedAsyncioTestCase):
    async def test_decimal_query_result_is_json_serializable(self):
        if "fastapi" not in sys.modules:
            fake_fastapi = types.ModuleType("fastapi")
            fake_fastapi.WebSocket = object
            sys.modules["fastapi"] = fake_fastapi

        from app.ws.manager import WSManager

        manager = WSManager()
        websocket = FakeWebSocket()
        await manager.connect("query-1", websocket)
        await manager.send("query-1", {
            "type": "result",
            "query_id": "query-1",
            "status": "success",
            "statements": [{"rows": [[Decimal("10.20")]]}],
        })

        self.assertEqual(len(websocket.sent), 1)
        self.assertIn('"10.20"', websocket.sent[0])

    async def test_late_websocket_receives_cached_query_result(self):
        if "fastapi" not in sys.modules:
            fake_fastapi = types.ModuleType("fastapi")
            fake_fastapi.WebSocket = object
            sys.modules["fastapi"] = fake_fastapi

        from app.ws.manager import WSManager

        manager = WSManager()
        await manager.send("query-1", {"type": "result", "query_id": "query-1", "status": "success"})

        websocket = FakeWebSocket()
        await manager.connect("query-1", websocket)

        self.assertTrue(websocket.accepted)
        self.assertEqual(len(websocket.sent), 1)
        self.assertIn('"status": "success"', websocket.sent[0])


if __name__ == "__main__":
    unittest.main()
