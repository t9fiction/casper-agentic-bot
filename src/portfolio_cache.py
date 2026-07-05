import json, os, fcntl
from pathlib import Path
from datetime import datetime, timezone

CACHE_FILE = Path(__file__).parent.parent / "portfolio_cache.json"


def _init_file():
    if not CACHE_FILE.exists():
        CACHE_FILE.write_text(json.dumps({"tokens": [], "nfts": [], "collections": []}))


class _LockedCache:
    def __enter__(self):
        _init_file()
        self.f = open(CACHE_FILE, "r+")
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
            return {"tokens": [], "nfts": [], "collections": []}

    def _write(self, cache: dict):
        self.f.seek(0)
        self.f.truncate()
        self.f.write(json.dumps(cache, indent=2))
        self.f.flush()

    def _append(self, key: str, entry: dict):
        cache = self._read()
        cache[key].append(entry)
        self._write(cache)
        return entry

    def _update_by_tx(self, key: str, tx_hash: str, updates: dict):
        cache = self._read()
        for item in cache[key]:
            if item.get("tx_hash") == tx_hash:
                item.update(updates)
                self._write(cache)
                return item
        return None


def log_token_deploy(name, symbol, decimals, total_supply, tx_hash, contract_name=None, recipient=None):
    entry = {
        "name": name,
        "symbol": symbol,
        "decimals": decimals,
        "total_supply": total_supply,
        "tx_hash": tx_hash,
        "contract_name": contract_name or "token_factory",
        "recipient": recipient or "",
        "status": "pending",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    with _LockedCache() as lc:
        return lc._append("tokens", entry)


def log_nft_mint(token_id=None, metadata_uri=None, collection=None, contract_name=None, recipient=None, tx_hash=None):
    entry = {
        "token_id": token_id or "",
        "metadata_uri": metadata_uri or "",
        "collection": collection or "",
        "contract_name": contract_name or "",
        "recipient": recipient or "",
        "tx_hash": tx_hash or "",
        "status": "pending",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    with _LockedCache() as lc:
        return lc._append("nfts", entry)


def log_collection_create(name, symbol, base_uri, mint_price, tx_hash, contract_name="collections", collection_id=None, creator=None):
    entry = {
        "name": name,
        "symbol": symbol,
        "base_uri": base_uri,
        "mint_price": mint_price,
        "collection_id": collection_id or "",
        "contract_name": contract_name,
        "creator": creator or "",
        "tx_hash": tx_hash,
        "status": "pending",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    with _LockedCache() as lc:
        return lc._append("collections", entry)


def update_status(tx_hash: str, status: str, updates: dict = None):
    merged = {"status": status, **(updates or {})}
    with _LockedCache() as lc:
        for key in ("tokens", "nfts", "collections"):
            result = lc._update_by_tx(key, tx_hash, merged)
            if result:
                return result
    return None


def get_cache():
    _init_file()
    with _LockedCache() as lc:
        return lc._read()


def get_tokens_for_wallet(wallet_hash: str):
    with _LockedCache() as lc:
        cache = lc._read()
    if not wallet_hash:
        return cache["tokens"]
    return [t for t in cache["tokens"] if t.get("recipient") == wallet_hash]


def get_nfts_for_wallet(wallet_hash: str):
    with _LockedCache() as lc:
        cache = lc._read()
    if not wallet_hash:
        return cache["nfts"]
    return [n for n in cache["nfts"] if n.get("recipient") == wallet_hash]
