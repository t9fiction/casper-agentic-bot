import os, re
from .mcp_client import call_tool

NETWORK = os.getenv("CASPER_NETWORK", "casper-test")
_EXPLORER = "testnet.cspr.live" if NETWORK in ("casper-test", "testnet") else "cspr.live"


async def analyze_account_impl(account_hash: str):
    if not account_hash or not account_hash.startswith("account-hash-"):
        return "Error: invalid account hash. Must start with 'account-hash-'."

    try:
        account_info = await call_tool("GetAccountInfo", {"account_hash": account_hash})
    except Exception as e:
        account_info = f"Error fetching account info: {e}"

    try:
        balance_raw = await call_tool("GetAccountBalance", {"account_hash": account_hash})
    except Exception:
        balance_raw = "N/A"

    # Extract balance number
    balance_match = re.search(r"([\d.]+)", str(balance_raw))
    balance_str = balance_match.group(1) if balance_match else balance_raw

    # Scan recent transfers via get_account_deploys
    try:
        deploys_raw = await call_tool("GetAccountDeploys", {"account_hash": account_hash, "page": 1, "pageSize": 20})
    except Exception:
        deploys_raw = ""

    # Parse deploy list for transfer amounts
    transfers_found = []
    if deploys_raw:
        for line in deploys_raw.split("\n"):
            amount_match = re.search(r"amount[:\s]*([\d.]+)", line, re.IGNORECASE)
            if amount_match:
                transfers_found.append(line.strip())

    lines = [
        f"--- Account Analysis ---",
        f"Account: {account_hash}",
        f"Balance: {balance_str} CSPR",
        f"",
        account_info,
    ]

    if transfers_found:
        lines.append("")
        lines.append("--- Recent Transfers ---")
        for t in transfers_found[:10]:
            lines.append(f"  {t}")

    lines.append("")
    lines.append(f"--- Full Explorer ---")
    lines.append(f"https://{_EXPLORER}/account/{account_hash}")

    return "\n".join(lines)
