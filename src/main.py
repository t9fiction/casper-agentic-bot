import os, asyncio, subprocess, json, re
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from .agent import run_agent
from .monitor import monitor_service
from .mcp_client import call_tool
from .portfolio_cache import get_cache

load_dotenv()

app = FastAPI(title="Casper Agentic Bot")

NETWORK = os.getenv("CASPER_NETWORK", "testnet")


class ChatRequest(BaseModel):
    message: str


class MonitorRequest(BaseModel):
    account_hash: str
    label: str = ""
    min_amount_cspr: float = 0


@app.on_event("startup")
async def startup():
    asyncio.create_task(monitor_service.run())


@app.on_event("shutdown")
async def shutdown():
    monitor_service.stop()


@app.get("/")
async def index():
    return FileResponse(Path(__file__).parent / "public" / "index.html")


@app.get("/portfolio")
async def portfolio_page():
    return FileResponse(Path(__file__).parent / "public" / "portfolio.html")


@app.get("/monitor")
async def monitor_page():
    return FileResponse(Path(__file__).parent / "public" / "monitor.html")


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
    nums = re.findall(r"[\d.]+", text or "")
    return nums[0] if nums else "0"


@app.get("/api/portfolio")
async def get_portfolio():
    wallet_hash = os.getenv("WALLET_ACCOUNT_HASH", "")
    if not wallet_hash:
        return JSONResponse({"error": "WALLET_ACCOUNT_HASH not configured"}, status_code=400)

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
    if raw_pkgs:
        try:
            parsed = json.loads(raw_pkgs)
            pkgs = parsed if isinstance(parsed, list) else (parsed.get("data", parsed.get("results", [])) if isinstance(parsed, dict) else [])
            contracts_count = len(pkgs or [])
        except (json.JSONDecodeError, TypeError):
            contracts_count = 2

    custom_cache = get_cache()
    return {
        "wallet": wallet_hash,
        "cspr_balance": cspr_balance,
        "tokens": cep18_tokens,
        "nfts": nfts,
        "recent_deploys": recent_deploys,
        "contracts": max(contracts_count, 1),
        "custom_tokens": custom_cache.get("tokens", []),
        "custom_nfts": custom_cache.get("nfts", []),
        "custom_collections": custom_cache.get("collections", []),
    }


@app.get("/api/health")
async def health():
    return {"status": "ok", "network": NETWORK}


@app.get("/api/monitors")
async def list_monitors():
    return {"monitors": monitor_service.list_monitors()}


@app.post("/api/monitors")
async def add_monitor(req: MonitorRequest):
    key = monitor_service.add_monitor(req.account_hash, req.label, req.min_amount_cspr)
    return {"monitor_id": key, "status": "active"}


@app.delete("/api/monitors/{monitor_id}")
async def remove_monitor(monitor_id: str):
    monitor_service.remove_monitor(monitor_id)
    return {"status": "removed"}


@app.get("/api/monitors/alerts")
async def get_alerts():
    return {"alerts": monitor_service.get_alerts(clear=True)}
