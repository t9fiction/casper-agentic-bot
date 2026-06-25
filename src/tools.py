import json
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
            schema = t.inputSchema or {}
            props = list((schema.get("properties") or {}).keys())
            lines.append(f"  - {name}: {desc}")
            if props:
                lines.append(f"    args: {', '.join(props)}")
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
