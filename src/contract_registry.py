import json, os
from pathlib import Path
from datetime import datetime

REGISTRY_FILE = Path(__file__).parent.parent / "contracts_registry.json"


def _load():
    if not REGISTRY_FILE.exists():
        return {}
    try:
        return json.loads(REGISTRY_FILE.read_text())
    except (json.JSONDecodeError, OSError):
        return {}


def _save(registry: dict):
    REGISTRY_FILE.write_text(json.dumps(registry, indent=2))


def register_deploy(contract_name: str, wasm_name: str, tx_hash: str, named_key: str, status: str = "pending"):
    registry = _load()
    registry[contract_name] = {
        "contract_name": contract_name,
        "wasm_name": wasm_name,
        "named_key": named_key,
        "tx_hash": tx_hash,
        "package_hash": "",
        "contract_hash": "",
        "status": status,
        "deployed_at": datetime.utcnow().isoformat(),
    }
    _save(registry)
    return registry[contract_name]


def update_contract(contract_name: str, package_hash: str = None, contract_hash: str = None, status: str = None):
    registry = _load()
    entry = registry.get(contract_name)
    if not entry:
        return None
    if package_hash:
        entry["package_hash"] = package_hash
    if contract_hash:
        entry["contract_hash"] = contract_hash
    if status:
        entry["status"] = status
    _save(registry)
    return entry


def get_contract(contract_name: str) -> dict:
    return _load().get(contract_name)


def list_contracts() -> dict:
    return _load()


def get_active_contract(wasm_name: str = None) -> dict:
    """Get the most recently deployed active contract, optionally filtered by wasm_name."""
    registry = _load()
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
