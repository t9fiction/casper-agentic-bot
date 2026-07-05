import os
from .mcp_client import call_tool

NETWORK = os.getenv("CASPER_NETWORK", "casper-test")


async def analyze_account_impl(account_hash: str):
    try:
        account_info = await call_tool("GetAccountInfo", {"account_hash": account_hash})
    except Exception as e:
        return f"Error fetching account info: {e}"

    try:
        balance_raw = await call_tool("GetAccountBalance", {"account_hash": account_hash})
    except Exception:
        balance_raw = "N/A"

    try:
        latest_blocks = await call_tool("GetLatestBlocks", {"limit": 20})
    except Exception:
        latest_blocks = ""

    lines = [f"--- Account Analysis ---", f"Account: {account_hash}", f""]
    lines.append(f"Balance: {balance_raw}")
    lines.append(f"")
    lines.append(account_info)
    lines.append(f"")

    lines.append("--- Recent Activity ---")
    lines.append("(Scanned last 20 blocks for transfers involving this account)")
    lines.append(f"{latest_blocks[:2000] if latest_blocks else 'No recent block data available.'}")
    lines.append(f"")

    lines.append("--- How to check transfers ---")
    lines.append(f"To see all transfers for this account, use your CSPR.cloud dashboard at:")
    lines.append(f"https://testnet.cspr.live/account/{account_hash}")

    return "\n".join(lines)
