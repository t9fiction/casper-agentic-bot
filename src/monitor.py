import asyncio, json, os, time, logging
from datetime import datetime
from pathlib import Path
from .mcp_client import call_tool

logger = logging.getLogger(__name__)

MONITOR_FILE = Path(__file__).parent.parent / "monitors.json"
POLL_INTERVAL = 30  # seconds


class MonitorService:
    def __init__(self):
        self.tasks = {}
        self._load_tasks()
        self._running = False
        self._alerts = []

    def _load_tasks(self):
        if MONITOR_FILE.exists():
            try:
                data = json.loads(MONITOR_FILE.read_text())
                self.tasks = {k: v for k, v in data.items() if v.get("active", True)}
            except Exception:
                self.tasks = {}

    def _save_tasks(self):
        MONITOR_FILE.write_text(json.dumps(self.tasks, indent=2))

    def add_monitor(self, account_hash: str, label: str = "", min_amount_cspr: float = 0):
        key = f"{account_hash}_{int(time.time())}"
        self.tasks[key] = {
            "account_hash": account_hash,
            "label": label or account_hash[:20],
            "min_amount_motes": int(min_amount_cspr * 1_000_000_000),
            "last_check_block": 0,
            "active": True,
            "created_at": datetime.utcnow().isoformat(),
        }
        self._save_tasks()
        return key

    def remove_monitor(self, key: str):
        self.tasks.pop(key, None)
        self._save_tasks()

    def list_monitors(self):
        return [
            {
                "id": k,
                "account": v["account_hash"],
                "label": v["label"],
                "min_cspr": v["min_amount_motes"] / 1_000_000_000,
                "active": v["active"],
            }
            for k, v in self.tasks.items()
        ]

    def get_alerts(self, clear: bool = False):
        alerts = list(self._alerts)
        if clear:
            self._alerts.clear()
        return alerts

    async def _check_account(self, key: str, config: dict):
        try:
            result = await call_tool("GetAccountInfo", {"account_hash": config["account_hash"]})
            self._alerts.append({
                "type": "account_check",
                "monitor_key": key,
                "account": config["account_hash"],
                "label": config["label"],
                "timestamp": datetime.utcnow().isoformat(),
                "data": result[:500],
            })
        except Exception as e:
            logger.warning(f"Monitor check failed for {config['account_hash']}: {e}")

    async def run(self):
        self._running = True
        while self._running:
            for key, config in list(self.tasks.items()):
                if config.get("active"):
                    await self._check_account(key, config)
            await asyncio.sleep(POLL_INTERVAL)

    def stop(self):
        self._running = False


monitor_service = MonitorService()
