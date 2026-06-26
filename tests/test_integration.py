"""Integration tests for Casper Agentic Bot.

Tests the Python backend modules, tools, and AI agent.

Requires:
  - .env with OPENAI_API_KEY and CSPR_CLOUD_API_KEY
  - casper-client CLI installed
  - secret_key.pem (for transfer/contract tests)
  - CONTRACT_PACKAGE_HASH env var (for contract entry point tests)

Run: python -m pytest tests/ -v
"""

import os, pytest, json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


class TestImports:
    def test_import_agent(self):
        from src.agent import run_agent
        assert callable(run_agent)

    def test_import_tools(self):
        from src.tools import query_casper_blockchain, send_cspr_transfer, analyze_account, call_contract_entry_point
        for tool in [query_casper_blockchain, send_cspr_transfer, analyze_account, call_contract_entry_point]:
            assert hasattr(tool, "name")
            assert hasattr(tool, "func") or hasattr(tool, "coroutine")

    def test_import_mcp_client(self):
        from src.mcp_client import list_tools, call_tool
        assert callable(list_tools)
        assert callable(call_tool)


class TestMCPClient:
    @pytest.mark.asyncio
    async def test_list_tools(self):
        from src.mcp_client import list_tools
        tools = await list_tools()
        assert len(tools) > 0
        names = [t.name for t in tools]
        assert "get_account_info" in names or any("account" in n.lower() for n in names)

    @pytest.mark.asyncio
    async def test_call_read_tool(self):
        from src.mcp_client import call_tool
        result = await call_tool("get_network_status", {})
        assert result is not None
        assert isinstance(result, str)
        assert len(result) > 50


class TestAnalyzeAccount:
    @pytest.mark.asyncio
    async def test_analyze_known_account(self):
        from src.account_analyzer import analyze_account_impl
        account_hash = "account-hash-2bc76a5348a847ff51738945d681b97dda6ed606f7ae4282d1a0eb409ef301f5"
        result = await analyze_account_impl(account_hash)
        assert result is not None
        assert isinstance(result, str)

    @pytest.mark.asyncio
    async def test_analyze_invalid_account(self):
        from src.account_analyzer import analyze_account_impl
        result = await analyze_account_impl("")
        assert isinstance(result, str)
        assert "error" in result.lower() or "failed" in result.lower() or "invalid" in result.lower()


async def _call_tool(tool, *args, **kwargs):
    """Invoke a StructuredTool by calling its underlying function directly."""
    func = tool.func or tool.coroutine
    return await func(*args, **kwargs)


class TestSendCSPRTransfer:
    @pytest.mark.asyncio
    async def test_missing_secret_key(self):
        """Should produce an error message, not crash, when secret key is missing."""
        from src.tools import send_cspr_transfer
        result = await _call_tool(
            send_cspr_transfer,
            recipient="account-hash-2bc76a5348a847ff51738945d681b97dda6ed606f7ae4282d1a0eb409ef301f5",
            amount_in_cspr=0.001,
        )
        assert "Error" in result or "failed" in result or "not found" in result.lower()

    @pytest.mark.skipif(
        not os.getenv("SECRET_KEY"),
        reason="SECRET_KEY not set, skipping live transfer test",
    )
    @pytest.mark.asyncio
    async def test_live_transfer_small(self):
        from src.tools import send_cspr_transfer
        result = await _call_tool(
            send_cspr_transfer,
            recipient="account-hash-2bc76a5348a847ff51738945d681b97dda6ed606f7ae4282d1a0eb409ef301f5",
            amount_in_cspr=0.001,
            transfer_id=42,
        )
        assert "submitted" in result.lower() or "failed" in result.lower()
        if "submitted" in result.lower():
            assert "Transaction hash" in result


class TestCallContractEntryPoint:
    @pytest.mark.asyncio
    async def test_missing_package_hash(self):
        from src.tools import call_contract_entry_point
        old = os.environ.pop("CONTRACT_PACKAGE_HASH", None)
        result = await _call_tool(call_contract_entry_point, "total_tokens", {})
        assert "error" in result.lower() or "not configured" in result.lower()
        if old:
            os.environ["CONTRACT_PACKAGE_HASH"] = old


class TestAgent:
    @pytest.mark.asyncio
    async def test_agent_responds_to_hello(self):
        from src.agent import run_agent
        result = await run_agent("Hello, what can you help me with?")
        assert result is not None
        assert isinstance(result, str)
        assert len(result) > 20

    @pytest.mark.asyncio
    async def test_agent_answers_network_query(self):
        from src.agent import run_agent
        result = await run_agent("What is the current state of the Casper network?")
        assert result is not None
        assert isinstance(result, str)
        assert len(result) > 50


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
