import json, os
from pathlib import Path
from datetime import datetime

CACHE_FILE = Path(__file__).parent.parent / "portfolio_cache.json"


def _load():
    if not CACHE_FILE.exists():
        return {"tokens": [], "nfts": [], "collections": []}
    try:
        return json.loads(CACHE_FILE.read_text())
    except (json.JSONDecodeError, OSError):
        return {"tokens": [], "nfts": [], "collections": []}


def _save(cache: dict):
    CACHE_FILE.write_text(json.dumps(cache, indent=2))


def log_token_deploy(
    name: str,
    symbol: str,
    decimals: int,
    total_supply: str,
    tx_hash: str,
    contract_name: str = None,
    recipient: str = None,
):
    cache = _load()
    cache["tokens"].append({
        "name": name,
        "symbol": symbol,
        "decimals": decimals,
        "total_supply": total_supply,
        "tx_hash": tx_hash,
        "contract_name": contract_name or "token_factory",
        "recipient": recipient or "",
        "status": "pending",
        "timestamp": datetime.utcnow().isoformat(),
    })
    _save(cache)


def log_nft_mint(
    token_id: str = None,
    metadata_uri: str = None,
    collection: str = None,
    contract_name: str = None,
    recipient: str = None,
    tx_hash: str = None,
):
    cache = _load()
    cache["nfts"].append({
        "token_id": token_id or "",
        "metadata_uri": metadata_uri or "",
        "collection": collection or "",
        "contract_name": contract_name or "",
        "recipient": recipient or "",
        "tx_hash": tx_hash or "",
        "status": "pending",
        "timestamp": datetime.utcnow().isoformat(),
    })
    _save(cache)


def log_collection_create(
    name: str,
    symbol: str,
    base_uri: str,
    mint_price: str,
    tx_hash: str,
    contract_name: str = "collections",
    collection_id: str = None,
    creator: str = None,
):
    cache = _load()
    cache["collections"].append({
        "name": name,
        "symbol": symbol,
        "base_uri": base_uri,
        "mint_price": mint_price,
        "collection_id": collection_id or "",
        "contract_name": contract_name,
        "creator": creator or "",
        "tx_hash": tx_hash,
        "status": "pending",
        "timestamp": datetime.utcnow().isoformat(),
    })
    _save(cache)


def get_cache():
    return _load()


def get_tokens_for_wallet(wallet_hash: str):
    cache = _load()
    return [t for t in cache["tokens"] if t.get("recipient") == wallet_hash or not wallet_hash]


def get_nfts_for_wallet(wallet_hash: str):
    cache = _load()
    return [n for n in cache["nfts"] if n.get("recipient") == wallet_hash or not wallet_hash]
