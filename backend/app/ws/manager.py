from fastapi import WebSocket
from typing import Dict
import json
from datetime import date, datetime


def _default_json(obj):
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


class WSManager:
    def __init__(self):
        self.active: Dict[str, WebSocket] = {}
        self.latest: Dict[str, dict] = {}

    async def connect(self, query_id: str, ws: WebSocket):
        await ws.accept()
        self.active[query_id] = ws
        print(f"[WSManager] Registered: {query_id}, total: {len(self.active)}")
        latest = self.latest.get(query_id)
        if latest:
            await ws.send_text(json.dumps(latest, default=_default_json))
            print(f"[WSManager] Replayed to {query_id}: type={latest.get('type')}, status={latest.get('status')}")
            if latest.get("status") in {"success", "error", "killed"}:
                self.latest.pop(query_id, None)

    async def send(self, query_id: str, data: dict):
        self.latest[query_id] = data
        ws = self.active.get(query_id)
        if not ws:
            print(f"[WSManager] No ws for {query_id}")
            return
        try:
            text = json.dumps(data, default=_default_json)
            await ws.send_text(text)
            print(f"[WSManager] Sent to {query_id}: type={data.get('type')}, status={data.get('status')}")
        except Exception as e:
            print(f"[WSManager] Send failed to {query_id}: {e}")
            self.disconnect(query_id)

    def disconnect(self, query_id: str):
        self.active.pop(query_id, None)
        print(f"[WSManager] Disconnected: {query_id}")


ws_manager = WSManager()
