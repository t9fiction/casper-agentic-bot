import os
import httpx
from contextlib import asynccontextmanager
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

CHAIN_NAME = os.getenv("CASPER_NETWORK", "casper-test")
_API_NETWORK = "mainnet" if CHAIN_NAME in ("casper", "mainnet") else "testnet"
MCP_URL = (
    "https://mcp.cspr.cloud/mcp"
    if _API_NETWORK == "mainnet"
    else "https://mcp.testnet.cspr.cloud/mcp"
)


@asynccontextmanager
async def get_session():
    api_key = os.getenv("CSPR_CLOUD_API_KEY")
    if not api_key:
        raise RuntimeError("CSPR_CLOUD_API_KEY environment variable is required")

    headers = {
        "X-CSPR-Cloud-Api-Key": api_key,
        "X-Casper-Network": _API_NETWORK,
    }

    async with httpx.AsyncClient(headers=headers, follow_redirects=True) as client:
        async with streamable_http_client(
            MCP_URL, http_client=client
        ) as streams:
            read, write, _ = streams
            async with ClientSession(read, write) as session:
                await session.initialize()
                yield session


async def list_tools():
    async with get_session() as session:
        result = await session.list_tools()
        return result.tools


async def call_tool(name: str, args: dict | None = None):
    async with get_session() as session:
        result = await session.call_tool(name, args or {})
        texts = [
            c.text
            for c in (result.content or [])
            if hasattr(c, "text") and c.text
        ]
        return "\n".join(texts)
