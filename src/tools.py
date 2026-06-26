import json, os, subprocess
from pathlib import Path
from langchain_core.tools import tool
from .mcp_client import list_tools, call_tool

_TOOLS_DESCRIPTION_CACHE = None


async def _get_tools_description():
    global _TOOLS_DESCRIPTION_CACHE
    if _TOOLS_DESCRIPTION_CACHE is None:
        tools = await list_tools()
        lines = []
        for t in tools:
            name = t.name
            desc = (t.description or "No description").split("\n")[0][:120]
            props = list((t.inputSchema or {}).get("properties") or {}.keys())
            lines.append(f"  - {name}: {desc}")
            if props:
                lines.append(f"    args: {', '.join(props)}")
        lines.append("")
        lines.append("  - send_cspr_transfer: Send CSPR tokens to another account")
        lines.append("    args: recipient (account hash), amount_in_cspr (number), transfer_id (optional number)")
        lines.append("")
        lines.append("  - analyze_account: Get detailed account info including biggest transactions")
        lines.append("    args: account_hash (string)")
        _TOOLS_DESCRIPTION_CACHE = "\n".join(lines)
    return _TOOLS_DESCRIPTION_CACHE


@tool
async def query_casper_blockchain(tool_name: str, arguments: dict = None):
    """Query the Casper blockchain using the MCP server.

    Call this when the user asks about anything on-chain:
    accounts, balances, blocks, deploys, validators, contracts,
    tokens, NFTs, transfers, network status, DeFi, etc.

    Args:
        tool_name: The exact MCP tool name (e.g. GetNetworkStatus, GetAccountBalance, GetLatestBlocks)
        arguments: JSON object of arguments for the tool (e.g. {"account_hash": "..."})
    """
    if arguments is None:
        arguments = {}
    return await call_tool(tool_name, arguments)


@tool
async def send_cspr_transfer(recipient: str, amount_in_cspr: float, transfer_id: int = None):
    """Send CSPR tokens from the server wallet to another account.

    The agent calls this when the user wants to transfer CSPR.
    Uses the secret key configured on the server.

    Args:
        recipient: The recipient's account hash (e.g. "account-hash-...")
        amount_in_cspr: Amount of CSPR to send (e.g. 5.5 for 5.5 CSPR)
        transfer_id: Optional user-defined identifier (uint64)
    """
    secret_key = os.getenv("SECRET_KEY_PATH", "secret_key.pem")
    if not Path(secret_key).exists():
        return "Error: Secret key file not found. Configure SECRET_KEY_PATH."

    node = os.getenv("CASPER_NODE", "http://65.109.115.124:7777")
    chain = os.getenv("CASPER_NETWORK", "casper-test")

    amount_motes = int(amount_in_cspr * 1_000_000_000)

    cmd = [
        "casper-client", "put-transaction", "transfer",
        "--node-address", node,
        "--chain-name", chain,
        "--secret-key", secret_key,
        "--target", recipient,
        "--transfer-amount", str(amount_motes),
        "--payment-amount", "1000000000",
        "--standard-payment", "true",
        "--gas-price-tolerance", "1",
    ]
    if transfer_id is not None:
        cmd.extend(["--transfer-id", str(transfer_id)])

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode != 0:
            return f"Transfer failed: {result.stderr.strip() or result.stdout.strip()}"
        data = json.loads(result.stdout)
        tx_hash = data.get("result", {}).get("transaction_hash", {})
        if isinstance(tx_hash, dict):
            tx_hash = tx_hash.get("Version1", str(tx_hash))
        return f"Transfer submitted successfully!\nTransaction hash: {tx_hash}\nAmount: {amount_in_cspr} CSPR to {recipient}\nCheck status: casper-client get-transaction --node-address {node} {tx_hash}"
    except subprocess.TimeoutExpired:
        return "Transfer timed out after 60 seconds."
    except json.JSONDecodeError:
        return f"Transfer submitted but could not parse response: {result.stdout[:500]}"
    except FileNotFoundError:
        return "Error: casper-client not found. Install it first."
    except Exception as e:
        return f"Transfer failed: {str(e)}"


@tool
async def analyze_account(account_hash: str):
    """Get detailed info about a Casper account including balance and biggest transactions.

    Analyzes an account by querying on-chain data and scanning recent blocks
    for the largest transfers sent and received.

    Args:
        account_hash: The account hash (e.g. "account-hash-...")
    """
    from .account_analyzer import analyze_account_impl
    return await analyze_account_impl(account_hash)
