import json, os, fcntl
from pathlib import Path
from datetime import datetime, timezone

REGISTRY_FILE = Path(__file__).parent.parent / "contracts_registry.json"


class _LockedRegistry:
    def __enter__(self):
        self.f = open(REGISTRY_FILE, "a+")
        fcntl.flock(self.f, fcntl.LOCK_EX)
        return self

    def __exit__(self, *args):
        fcntl.flock(self.f, fcntl.LOCK_UN)
        self.f.close()

    def _read(self):
        self.f.seek(0)
        try:
            return json.loads(self.f.read())
        except (json.JSONDecodeError, OSError):
            return {}

    def _write(self, registry: dict):
        self.f.seek(0)
        self.f.truncate()
        self.f.write(json.dumps(registry, indent=2))
        self.f.flush()


def register_deploy(contract_name: str, wasm_name: str, tx_hash: str, named_key: str, status: str = "pending"):
    with _LockedRegistry() as lr:
        registry = lr._read()
        registry[contract_name] = {
            "contract_name": contract_name,
            "wasm_name": wasm_name,
            "named_key": named_key,
            "tx_hash": tx_hash,
            "package_hash": "",
            "contract_hash": "",
            "status": status,
            "deployed_at": datetime.now(timezone.utc).isoformat(),
        }
        lr._write(registry)
    return registry[contract_name]


def update_contract(contract_name: str, package_hash: str = None, contract_hash: str = None, status: str = None):
    with _LockedRegistry() as lr:
        registry = lr._read()
        entry = registry.get(contract_name)
        if not entry:
            return None
        if package_hash:
            entry["package_hash"] = package_hash
        if contract_hash:
            entry["contract_hash"] = contract_hash
        if status:
            entry["status"] = status
        lr._write(registry)
    return entry


def get_contract(contract_name: str) -> dict:
    with _LockedRegistry() as lr:
        return lr._read().get(contract_name)


def list_contracts() -> dict:
    with _LockedRegistry() as lr:
        return lr._read()


def get_active_contract(wasm_name: str = None) -> dict:
    with _LockedRegistry() as lr:
        registry = lr._read()
    candidates = []
    for name, info in registry.items():
        if info.get("status") == "active":
            if wasm_name and info.get("wasm_name") != wasm_name:
                continue
            candidates.append((info["deployed_at"], info))
    if not candidates:
        return None
    candidates.sort(key=lambda x: x[0], reverse=True)
    return candidates[0][1]
