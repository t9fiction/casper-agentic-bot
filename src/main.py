import os, json, re
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from .agent import run_agent
from .mcp_client import call_tool
from .portfolio_cache import get_cache

load_dotenv()

app = FastAPI(title="Casper Agentic Bot")

NETWORK = os.getenv("CASPER_NETWORK", "testnet")


class ChatRequest(BaseModel):
    message: str


@app.get("/")
async def index():
    return FileResponse(Path(__file__).parent / "public" / "index.html")


@app.get("/portfolio")
async def portfolio_page():
    return FileResponse(Path(__file__).parent / "public" / "portfolio.html")

@app.get("/admin")
async def admin_page():
    return FileResponse(Path(__file__).parent / "public" / "admin.html")


@app.post("/api/chat")
async def chat(req: ChatRequest):
    if not req.message.strip():
        return JSONResponse({"error": "Message is required"}, status_code=400)
    try:
        reply = await run_agent(req.message)
        return {"reply": reply}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


def _strip_hash_prefix(h: str) -> str:
    return h.removeprefix("account-hash-").removeprefix("hash-")

async def _mcp_call(name: str, args: dict = None):
    try:
        return await call_tool(name, args or {})
    except Exception as e:
        return None

def _parse_nums(text: str) -> str:
    match = re.search(r"([\d.]+)\s*CSPR", text or "")
    if match:
        return match.group(1)
    nums = re.findall(r"[\d.]+", text or "")
    return nums[0] if nums else "0"


@app.get("/api/portfolio")
async def get_portfolio(public_key: str = None):
    wallet_hash = public_key or os.getenv("WALLET_ACCOUNT_HASH", "")
    if not wallet_hash:
        return JSONResponse({"error": "WALLET_ACCOUNT_HASH not configured and no public_key provided"}, status_code=400)

    raw_hash = _strip_hash_prefix(wallet_hash)

    # CSPR balance via MCP (lowercase tool name, accountIdentifier param, raw hex)
    balance_text = await _mcp_call("get_account_balance", {"accountIdentifier": raw_hash})
    cspr_balance = _parse_nums(balance_text)

    # Standard CEP-18 token balances via MCP (if any)
    raw_fts = await _mcp_call("get_account_ft_balances", {"accountIdentifier": raw_hash})
    cep18_tokens = []
    if raw_fts and "No fungible token balances" not in raw_fts:
        try:
            parsed = json.loads(raw_fts) if isinstance(raw_fts, str) else raw_fts
            items = parsed if isinstance(parsed, list) else []
            for ft in items[:20]:
                if isinstance(ft, dict):
                    cep18_tokens.append({
                        "name": ft.get("token_name") or ft.get("name", ""),
                        "symbol": ft.get("token_symbol") or ft.get("symbol", ""),
                        "balance": str(ft.get("balance", ft.get("total_balance", "0"))),
                        "contract_package": ft.get("contract_package", ""),
                    })
        except (json.JSONDecodeError, TypeError):
            pass

    # NFTs via MCP (works once NFT contract is deployed)
    raw_nfts = await _mcp_call("get_account_nfts", {"accountIdentifier": raw_hash})
    nfts = []
    if raw_nfts and "No NFTs found" not in raw_nfts:
        try:
            parsed = json.loads(raw_nfts) if isinstance(raw_nfts, str) else raw_nfts
            items = parsed if isinstance(parsed, list) else (parsed if isinstance(parsed, dict) else [])
            if isinstance(items, dict):
                items = items.get("data", items.get("results", []))
            for nft in (items or [])[:30]:
                if isinstance(nft, dict):
                    nfts.append({
                        "token_id": nft.get("token_id", nft.get("id", "")),
                        "metadata_uri": nft.get("metadata_uri", nft.get("metadata", "")),
                        "collection": nft.get("collection_name", nft.get("contract_package", "")),
                    })
        except (json.JSONDecodeError, TypeError):
            pass

    # Recent deploys for activity feed
    recent_deploys = []
    raw_deploys = await _mcp_call("get_account_deploys", {"accountIdentifier": raw_hash, "page": 1, "pageSize": 5})
    if raw_deploys:
        try:
            parsed = json.loads(raw_deploys) if isinstance(raw_deploys, str) else raw_deploys
            deploys = parsed if isinstance(parsed, list) else (parsed.get("data", parsed.get("results", [])) if isinstance(parsed, dict) else [])
            for d in (deploys or [])[:5]:
                if isinstance(d, dict):
                    recent_deploys.append({
                        "hash": d.get("deploy_hash", d.get("hash", ""))[:16],
                        "type": d.get("action", d.get("entry_point", d.get("deploy_type", "transfer"))),
                        "timestamp": d.get("timestamp", d.get("block_timestamp", "")),
                    })
        except (json.JSONDecodeError, TypeError):
            pass

    # Contract packages count for context
    raw_pkgs = await _mcp_call("get_account_contract_packages", {"accountIdentifier": raw_hash})
    contracts_count = 0
    deployed_contracts = []

    import sys
    print(f"DEBUG: raw_pkgs type = {type(raw_pkgs)}, value = {raw_pkgs!r}", file=sys.stderr)

    if raw_pkgs:
        try:
            # Try to parse as JSON string
            if isinstance(raw_pkgs, str):
                parsed = json.loads(raw_pkgs)
            else:
                parsed = raw_pkgs

            # Extract package list from various response formats
            if isinstance(parsed, list):
                pkgs = parsed
            elif isinstance(parsed, dict):
                pkgs = parsed.get("data", parsed.get("results", parsed.get("deployed_contracts", [])))
            else:
                pkgs = []

            print(f"DEBUG: parsed packages count = {len(pkgs or [])}", file=sys.stderr)

            contracts_count = len(pkgs or [])
            # Also include contract details in response
            for pkg in (pkgs or [])[:20]:
                if isinstance(pkg, dict):
                    deployed_contracts.append({
                        "contract_package": pkg.get("contract_package", pkg.get("package_hash", pkg.get("hash", ""))),
                        "version": pkg.get("version", pkg.get("contract_version", 0)),
                        "timestamp": pkg.get("timestamp", ""),
                        "type": pkg.get("type", pkg.get("contract_type", "contract")),
                    })
            print(f"DEBUG: deployed_contracts count = {len(deployed_contracts)}", file=sys.stderr)
        except (json.JSONDecodeError, TypeError, AttributeError) as e:
            print(f"DEBUG: Error parsing packages: {e}", file=sys.stderr)
            contracts_count = 0

    custom_cache = get_cache()

    # Add logging to help debug
    print(f"DEBUG: recent_deploys = {recent_deploys}", file=sys.stderr)
    print(f"DEBUG: cep18_tokens count = {len(cep18_tokens)}", file=sys.stderr)
    print(f"DEBUG: nfts count = {len(nfts)}", file=sys.stderr)
    print(f"DEBUG: custom_cache = {custom_cache}", file=sys.stderr)
    print(f"DEBUG: deployed_contracts = {deployed_contracts}", file=sys.stderr)

    return {
        "wallet": wallet_hash,
        "cspr_balance": cspr_balance,
        "tokens": cep18_tokens,
        "nfts": nfts,
        "recent_deploys": recent_deploys,
        "deployed_contracts": deployed_contracts,
        "contracts": max(contracts_count, 1),
        "custom_tokens": custom_cache.get("tokens", []),
        "custom_nfts": custom_cache.get("nfts", []),
        "custom_collections": custom_cache.get("collections", []),
    }


@app.post("/api/admin/log-token")
async def log_token_manual(name: str, symbol: str, decimals: int = 8, total_supply: str = "0", tx_hash: str = ""):
    """Manual endpoint to add a token to the portfolio cache"""
    from .portfolio_cache import log_token_deploy
    log_token_deploy(
        name=name,
        symbol=symbol,
        decimals=decimals,
        total_supply=total_supply,
        tx_hash=tx_hash,
        recipient=os.getenv("WALLET_ACCOUNT_HASH", ""),
    )
    return {"status": "token logged", "name": name}

@app.post("/api/admin/log-nft")
async def log_nft_manual(token_id: str, metadata_uri: str, recipient: str = "", collection: str = "custom", tx_hash: str = ""):
    """Manual endpoint to add an NFT to the portfolio cache"""
    from .portfolio_cache import log_nft_mint
    log_nft_mint(
        token_id=token_id,
        metadata_uri=metadata_uri,
        recipient=recipient or os.getenv("WALLET_ACCOUNT_HASH", ""),
        contract_name=collection,
        tx_hash=tx_hash,
        collection=collection,
    )
    return {"status": "nft logged", "token_id": token_id}

@app.post("/api/admin/log-collection")
async def log_collection_manual(name: str, symbol: str, base_uri: str, mint_price: str = "0", tx_hash: str = ""):
    """Manual endpoint to add a collection to the portfolio cache"""
    from .portfolio_cache import log_collection_create
    log_collection_create(
        name=name,
        symbol=symbol,
        base_uri=base_uri,
        mint_price=mint_price,
        tx_hash=tx_hash,
        collection_id="",
    )
    return {"status": "collection logged", "name": name}

@app.get("/api/health")
async def health():
    return {"status": "ok", "network": NETWORK}
