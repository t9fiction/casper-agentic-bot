import os, json, re
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .agent import run_agent
from .mcp_client import call_tool
from .portfolio_cache import get_cache

load_dotenv()

app = FastAPI(title="Casper Agentic Bot")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

NETWORK = os.getenv("CASPER_NETWORK", "testnet")


class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"  # Optional session ID for conversation history


@app.get("/")
async def index():
    return FileResponse(Path(__file__).parent / "public" / "index.html")


@app.get("/portfolio")
async def portfolio_page():
    return FileResponse(Path(__file__).parent / "public" / "portfolio.html")

@app.get("/admin")
async def admin_page():
    return FileResponse(Path(__file__).parent / "public" / "admin.html")

@app.get("/debug")
async def debug_page():
    return FileResponse(Path(__file__).parent / "public" / "debug.html")


@app.post("/api/chat")
async def chat(req: ChatRequest):
    if not req.message.strip():
        return JSONResponse({"error": "Message is required"}, status_code=400)
    try:
        reply = await run_agent(req.message, session_id=req.session_id)
        return {"reply": reply}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.get("/api/conversation/{session_id}")
async def get_conversation(session_id: str):
    """Get conversation history for a session."""
    from .conversation import get_conversation
    conv = get_conversation(session_id)
    return {
        "session_id": session_id,
        "messages": [m.to_dict() for m in conv.messages],
        "summary": conv.summary(),
    }


@app.post("/api/conversation/{session_id}/clear")
async def clear_conversation(session_id: str):
    """Clear conversation history for a session."""
    from .conversation import get_conversation
    conv = get_conversation(session_id)
    conv.clear()
    return {"status": "cleared", "session_id": session_id}


@app.get("/api/conversations")
async def list_conversations():
    """List all active conversation sessions."""
    from .conversation import list_conversations
    sessions = list_conversations()
    return {"sessions": sessions, "count": len(sessions)}


def _strip_hash_prefix(h: str) -> str:
    return h.removeprefix("account-hash-").removeprefix("hash-")

async def _mcp_call(name: str, args: dict = None):
    try:
        return await call_tool(name, args or {})
    except Exception as e:
        return None

def _parse_nums(text: str) -> str:
    match = re.search(r"([\d,.-]+)\s*CSPR", text or "")
    if match:
        return match.group(1).replace(",", "")
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
    # IMPORTANT: get_account_contract_packages requires publicKey (not accountIdentifier!)
    # Derive public key from wallet connection or env var
    # If user provided a public_key param, use it; otherwise fall back to env var
    pk_from_env = os.getenv("PUBLIC_KEY", "")
    public_key = public_key or pk_from_env
    if not public_key:
        # Derive from account hash by trying both formats
        raw = _strip_hash_prefix(wallet_hash)
        public_key = raw  # Use the raw hash as fallback
    raw_pkgs = await _mcp_call("get_account_contract_packages", {"publicKey": public_key})
    contracts_count = 0
    deployed_contracts = []

    if raw_pkgs:
        try:
            # MCP returns markdown format, not JSON
            # Example: "## Account Contract Packages (Page 1, 6 total)\n---\n- **Package Hash:** 2a829bcdb3..."
            # Parse markdown to extract contract hashes
            pkgs = []

            if isinstance(raw_pkgs, str):
                # Look for "Package Hash:" lines in markdown
                lines = raw_pkgs.split('\n')
                current_pkg = {}

                for line in lines:
                    line = line.strip()

                    # Extract package hash
                    if line.startswith('- **Package Hash:**') or 'Package Hash:' in line:
                        if current_pkg:
                            pkgs.append(current_pkg)
                        # Extract hash value - remove markdown formatting
                        hash_val = line.split('Package Hash:')[-1].strip()
                        # Clean up any markdown artifacts like "** "
                        hash_val = hash_val.replace('**', '').strip()
                        current_pkg = {
                            "contract_package": f"hash-{hash_val}" if hash_val and not hash_val.startswith('hash-') else hash_val,
                            "package_hash": hash_val,
                            "version": 0,
                            "timestamp": "",
                            "type": "contract"
                        }

                    # Extract created timestamp
                    elif 'Created:' in line:
                        created = line.split('Created:')[-1].strip()
                        if current_pkg:
                            current_pkg["timestamp"] = created

                # Add last package
                if current_pkg:
                    pkgs.append(current_pkg)

                # Extract total count from header
                for line in lines:
                    if 'total' in line.lower():
                        match = re.search(r'(\d+)\s+total', line)
                        if match:
                            contracts_count = int(match.group(1))
                            break
            else:
                pkgs = raw_pkgs if isinstance(raw_pkgs, list) else []

            # Build enriched contracts list
            for pkg in pkgs[:20]:
                if isinstance(pkg, dict):
                    deployed_contracts.append({
                        "contract_package": pkg.get("contract_package", pkg.get("package_hash", "")),
                        "version": pkg.get("version", 0),
                        "timestamp": pkg.get("timestamp", ""),
                        "type": pkg.get("type", "contract"),
                    })
        except (ValueError, TypeError, AttributeError, KeyError) as e:
            contracts_count = 0

    custom_cache = get_cache()

    # Merge blockchain contracts with cache metadata
    # Strategy: Show ALL blockchain contracts, use cache to add metadata
    enriched_contracts = []

    # Create a map of contract hashes to cached metadata for quick lookup
    cached_by_package = {}
    for token in custom_cache.get("tokens", []):
        # Try to match by naming convention or explicit package
        key = token.get("name", "").lower()
        cached_by_package[key] = {
            "type": "token",
            "name": token.get("name", ""),
            "symbol": token.get("symbol", ""),
            "decimals": token.get("decimals", ""),
            "total_supply": token.get("total_supply", ""),
            "metadata_source": "cache"
        }

    for collection in custom_cache.get("collections", []):
        key = collection.get("name", "").lower()
        cached_by_package[key] = {
            "type": "collection",
            "name": collection.get("name", ""),
            "symbol": collection.get("symbol", ""),
            "base_uri": collection.get("base_uri", ""),
            "mint_price": collection.get("mint_price", ""),
            "metadata_source": "cache"
        }

    # Process all blockchain-discovered contracts
    for contract in deployed_contracts:
        pkg_hash = contract.get("contract_package", "")

        # Try to find matching metadata in cache
        metadata = None
        for cached_key, cached_meta in cached_by_package.items():
            # Check if this contract has cached metadata
            # First try exact hash match, then try name match
            if pkg_hash.endswith(cached_key) or cached_key in pkg_hash.lower():
                metadata = cached_meta
                break

        # Build enriched contract object
        enriched_contract = {
            "contract_package": pkg_hash,
            "version": contract.get("version", ""),
            "timestamp": contract.get("timestamp", ""),
            "type": contract.get("type", ""),
            # Metadata fields (can be empty/null if not in cache)
            "metadata": metadata or {
                "name": None,
                "symbol": None,
                "type": None,
                "description": None,
                "metadata_source": "blockchain"
            }
        }
        enriched_contracts.append(enriched_contract)

    return {
        "wallet": wallet_hash,
        "cspr_balance": cspr_balance,
        "tokens": cep18_tokens,
        "nfts": nfts,
        "recent_deploys": recent_deploys,
        "deployed_contracts": enriched_contracts,  # Now includes metadata where available
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
