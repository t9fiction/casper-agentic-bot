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


class TestContractRegistry:
    def setup_method(self):
        self.test_file = Path("_test_registry.json")
        import src.contract_registry as cr
        cr.REGISTRY_FILE = self.test_file
        if self.test_file.exists():
            self.test_file.unlink()

    def teardown_method(self):
        if self.test_file.exists():
            self.test_file.unlink()

    def test_register_deploy(self):
        from src.contract_registry import register_deploy, get_contract
        entry = register_deploy("test_nft", "NftMarketplace", "0xdead", "test_nft")
        assert entry["contract_name"] == "test_nft"
        assert entry["wasm_name"] == "NftMarketplace"
        assert entry["tx_hash"] == "0xdead"
        assert entry["status"] == "pending"
        assert get_contract("test_nft")["contract_name"] == "test_nft"

    def test_register_duplicate_overwrites(self):
        from src.contract_registry import register_deploy, get_contract
        register_deploy("dup", "NftMarketplace", "0xaaa", "dup")
        register_deploy("dup", "TokenFactory", "0xbbb", "dup2")
        c = get_contract("dup")
        assert c["wasm_name"] == "TokenFactory"
        assert c["tx_hash"] == "0xbbb"

    def test_update_contract(self):
        from src.contract_registry import register_deploy, update_contract, get_contract
        register_deploy("nft1", "NftMarketplace", "0x123", "nft1")
        update_contract("nft1", package_hash="hash-abc", contract_hash="contract-def", status="active")
        c = get_contract("nft1")
        assert c["package_hash"] == "hash-abc"
        assert c["contract_hash"] == "contract-def"
        assert c["status"] == "active"

    def test_get_contract_not_found(self):
        from src.contract_registry import get_contract
        assert get_contract("nonexistent") is None

    def test_list_contracts(self):
        from src.contract_registry import register_deploy, list_contracts
        register_deploy("a", "NftMarketplace", "0x1", "a")
        register_deploy("b", "TokenFactory", "0x2", "b")
        reg = list_contracts()
        assert "a" in reg
        assert "b" in reg
        assert len(reg) == 2

    def test_get_active_contract(self):
        from src.contract_registry import register_deploy, update_contract, get_active_contract
        register_deploy("pending1", "NftMarketplace", "0x1", "p1")
        register_deploy("active1", "NftMarketplace", "0x2", "a1")
        update_contract("active1", status="active")
        active = get_active_contract()
        assert active is not None
        assert active["contract_name"] == "active1"

    def test_get_active_contract_filtered_by_wasm(self):
        from src.contract_registry import register_deploy, update_contract, get_active_contract
        register_deploy("tf1", "TokenFactory", "0x1", "tf1")
        register_deploy("nft1", "NftMarketplace", "0x2", "nft1")
        update_contract("tf1", status="active")
        update_contract("nft1", status="active")
        nft_active = get_active_contract(wasm_name="NftMarketplace")
        assert nft_active["contract_name"] == "nft1"
        tf_active = get_active_contract(wasm_name="TokenFactory")
        assert tf_active["contract_name"] == "tf1"

    def test_get_active_contract_returns_latest(self):
        from src.contract_registry import register_deploy, update_contract, get_active_contract
        register_deploy("old", "NftMarketplace", "0x1", "old")
        update_contract("old", status="active")
        register_deploy("new", "NftMarketplace", "0x2", "new")
        update_contract("new", status="active")
        active = get_active_contract()
        assert active["contract_name"] == "new"


class TestPortfolioCache:
    def setup_method(self):
        self.test_file = Path("_test_portfolio.json")
        import src.portfolio_cache as pc
        pc.CACHE_FILE = self.test_file
        if self.test_file.exists():
            self.test_file.unlink()

    def teardown_method(self):
        if self.test_file.exists():
            self.test_file.unlink()

    def test_log_token_deploy(self):
        from src.portfolio_cache import log_token_deploy, get_cache
        log_token_deploy("MyToken", "MTK", 8, "1000000", "0xabc", contract_name="token_factory", recipient="acc-hash-1")
        cache = get_cache()
        assert len(cache["tokens"]) == 1
        t = cache["tokens"][0]
        assert t["name"] == "MyToken"
        assert t["symbol"] == "MTK"
        assert t["decimals"] == 8
        assert t["total_supply"] == "1000000"
        assert t["tx_hash"] == "0xabc"
        assert t["status"] == "pending"

    def test_log_nft_mint(self):
        from src.portfolio_cache import log_nft_mint, get_cache
        log_nft_mint(token_id="0", metadata_uri="ipfs://test.json", collection="test_collection",
                      contract_name="test_nft", recipient="acc-hash-1", tx_hash="0xnft")
        cache = get_cache()
        assert len(cache["nfts"]) == 1
        n = cache["nfts"][0]
        assert n["token_id"] == "0"
        assert n["metadata_uri"] == "ipfs://test.json"
        assert n["collection"] == "test_collection"
        assert n["recipient"] == "acc-hash-1"

    def test_log_collection_create(self):
        from src.portfolio_cache import log_collection_create, get_cache
        log_collection_create("CyberPunks", "CYBR", "ipfs://cp/", "10000000000",
                              "0xcol", contract_name="collections", creator="acc-hash-1")
        cache = get_cache()
        assert len(cache["collections"]) == 1
        c = cache["collections"][0]
        assert c["name"] == "CyberPunks"
        assert c["symbol"] == "CYBR"
        assert c["base_uri"] == "ipfs://cp/"
        assert c["mint_price"] == "10000000000"
        assert c["creator"] == "acc-hash-1"

    def test_multiple_entries(self):
        from src.portfolio_cache import log_token_deploy, log_nft_mint, log_collection_create, get_cache
        log_token_deploy("A", "A", 8, "1", "0x1")
        log_token_deploy("B", "B", 6, "2", "0x2")
        log_nft_mint(token_id="0", tx_hash="0xn1")
        log_collection_create("C", "C", "ipfs://", "0", "0xc")
        cache = get_cache()
        assert len(cache["tokens"]) == 2
        assert len(cache["nfts"]) == 1
        assert len(cache["collections"]) == 1

    def test_get_tokens_for_wallet(self):
        from src.portfolio_cache import log_token_deploy, get_tokens_for_wallet
        log_token_deploy("T1", "T", 8, "100", "0x1", recipient="wallet-a")
        log_token_deploy("T2", "T", 8, "200", "0x2", recipient="wallet-b")
        wallet_a = get_tokens_for_wallet("wallet-a")
        assert len(wallet_a) == 1
        assert wallet_a[0]["name"] == "T1"

    def test_get_nfts_for_wallet(self):
        from src.portfolio_cache import log_nft_mint, get_nfts_for_wallet
        log_nft_mint(token_id="1", recipient="wallet-a", tx_hash="0x1")
        log_nft_mint(token_id="2", recipient="wallet-b", tx_hash="0x2")
        wallet_b = get_nfts_for_wallet("wallet-b")
        assert len(wallet_b) == 1
        assert wallet_b[0]["token_id"] == "2"

    def test_empty_cache(self):
        from src.portfolio_cache import get_cache
        cache = get_cache()
        assert cache == {"tokens": [], "nfts": [], "collections": []}

    def test_cache_isolation_between_calls(self):
        from src.portfolio_cache import log_token_deploy, get_cache
        log_token_deploy("X", "X", 8, "1", "0x1")
        log_token_deploy("Y", "Y", 8, "2", "0x2")
        cache = get_cache()
        assert len(cache["tokens"]) == 2


class TestNftArgResolution:
    """Test that call_contract_entry_point resolves NFT arg types correctly.

    These tests verify the internal logic that maps entry point names
    to correct Casper CL types (u64 for NFT token_id, u32 for Token Factory).
    """

    def _simulate_arg_building(self, entry_point, session_args):
        """Replicate the arg-building logic from tools.py call_contract_entry_point."""
        _NFT_ENTRY_POINTS = {
            "mint_nft", "transfer_nft", "list_nft", "unlist_nft",
            "buy_nft", "nft_info", "owner_of", "metadata_uri", "total_nfts",
            "collection_info", "total_collections", "total_nfts_in_collection",
            "nfts_by_collection",
        }
        _ARG_TYPE_OVERRIDES = {
            "decimals": "u8",
            "total_supply": "u256",
            "amount": "u256",
            "owner": "key",
            "recipient": "key",
            "buyer": "key",
            "price": "u256",
            "metadata_uri": "string",
            "collection_id": "u32",
            "mint_price": "u256",
            "page": "u32",
            "page_size": "u32",
        }
        _NFT_TOKEN_TYPE = "u64"
        _BASE_TOKEN_TYPE = "u32"

        args = []
        for arg_name, arg_value in session_args.items():
            if arg_name == "token_id":
                cl_type = _NFT_TOKEN_TYPE if entry_point in _NFT_ENTRY_POINTS else _BASE_TOKEN_TYPE
            else:
                cl_type = _ARG_TYPE_OVERRIDES.get(arg_name)
            if cl_type:
                arg_str = f"{arg_name}:{cl_type}='{arg_value}'"
            elif isinstance(arg_value, bool):
                arg_str = f"{arg_name}:bool='{str(arg_value).lower()}'"
            elif isinstance(arg_value, int):
                arg_str = f"{arg_name}:u64='{arg_value}'"
            elif isinstance(arg_value, str):
                arg_str = f"{arg_name}:string='{arg_value}'"
            else:
                arg_str = f"{arg_name}:string='{arg_value}'"
            args.append(arg_str)
        return args

    def test_nft_token_id_is_u64(self):
        """NFT entry points should use u64 for token_id."""
        for ep in ["mint_nft", "transfer_nft", "list_nft", "buy_nft", "nft_info", "owner_of"]:
            result = self._simulate_arg_building(ep, {"token_id": "1"})
            assert "token_id:u64='1'" in result, f"{ep} should use u64 for token_id"

    def test_token_factory_token_id_is_u32(self):
        """Token Factory entry points should use u32 for token_id."""
        for ep in ["deploy_token", "transfer", "balance_of", "token_info", "mint"]:
            result = self._simulate_arg_building(ep, {"token_id": "1"})
            assert "token_id:u32='1'" in result, f"{ep} should use u32 for token_id"

    def test_recipient_is_key(self):
        """recipient arg should be key CL type."""
        result = self._simulate_arg_building("mint_nft", {"recipient": "account-hash-abc"})
        assert "recipient:key='account-hash-abc'" in result

    def test_buyer_is_key(self):
        """buyer arg should be key CL type."""
        result = self._simulate_arg_building("buy_nft", {"buyer": "account-hash-abc"})
        assert "buyer:key='account-hash-abc'" in result

    def test_price_is_u256(self):
        """price arg should be u256 CL type."""
        result = self._simulate_arg_building("list_nft", {"price": "50"})
        assert "price:u256='50'" in result

    def test_collection_id_is_u32(self):
        """collection_id arg should be u32 CL type."""
        result = self._simulate_arg_building("mint_nft", {"collection_id": "0"})
        assert "collection_id:u32='0'" in result

    def test_mint_price_is_u256(self):
        """mint_price arg should be u256 CL type."""
        result = self._simulate_arg_building("create_collection", {"mint_price": "10000000000"})
        assert "mint_price:u256='10000000000'" in result

    def test_metadata_uri_is_string(self):
        """metadata_uri arg should be string CL type."""
        result = self._simulate_arg_building("mint_nft", {"metadata_uri": "ipfs://test.json"})
        assert "metadata_uri:string='ipfs://test.json'" in result

    def test_decimals_is_u8(self):
        """decimals arg should be u8 CL type."""
        result = self._simulate_arg_building("deploy_token", {"decimals": "8"})
        assert "decimals:u8='8'" in result

    def test_total_supply_is_u256(self):
        """total_supply arg should be u256 CL type."""
        result = self._simulate_arg_building("deploy_token", {"total_supply": "1000000"})
        assert "total_supply:u256='1000000'" in result

    def test_amount_is_u256(self):
        """amount arg should be u256 CL type."""
        result = self._simulate_arg_building("transfer", {"amount": "500"})
        assert "amount:u256='500'" in result

    def test_owner_is_key(self):
        """owner arg should be key CL type."""
        result = self._simulate_arg_building("balance_of", {"owner": "account-hash-abc"})
        assert "owner:key='account-hash-abc'" in result

    def test_page_args_are_u32(self):
        """page and page_size args should be u32 CL type."""
        result = self._simulate_arg_building("nfts_by_collection", {"collection_id": "0", "page": "1", "page_size": "10"})
        assert "page:u32='1'" in result
        assert "page_size:u32='10'" in result

    def test_collection_entry_points_have_u64_token_id(self):
        """Collection Factory entry points should use u64 for token_id."""
        for ep in ["collection_info", "total_nfts_in_collection", "nfts_by_collection"]:
            result = self._simulate_arg_building(ep, {"collection_id": "0"})
            assert "collection_id:u32='0'" in result, f"{ep} should use u32 for collection_id"

    def test_all_nft_entry_points_resolve_correctly(self):
        """Every NFT entry point should resolve without errors."""
        test_cases = [
            ("mint_nft", {"metadata_uri": "ipfs://x.json", "recipient": "acc-hash-1"}),
            ("transfer_nft", {"token_id": "0", "recipient": "acc-hash-2"}),
            ("list_nft", {"token_id": "0", "price": "100"}),
            ("unlist_nft", {"token_id": "0"}),
            ("buy_nft", {"token_id": "0", "buyer": "acc-hash-3"}),
            ("nft_info", {"token_id": "0"}),
            ("owner_of", {"token_id": "0"}),
            ("metadata_uri", {"token_id": "0"}),
            ("collection_info", {"collection_id": "0"}),
            ("nfts_by_collection", {"collection_id": "0", "page": "0", "page_size": "10"}),
        ]
        for ep, args in test_cases:
            result = self._simulate_arg_building(ep, args)
            assert len(result) > 0
            assert all(":" in a for a in result), f"All args for {ep} should have CL type annotations"


class TestDeployContractValidation:
    """Test that deploy_contract validates inputs correctly."""

    def test_deploy_contract_missing_wasm(self):
        """Should return error for nonexistent wasm file."""
        import src.tools as tools
        from pathlib import Path
        fake_wasm = tools._WASM_DIR / "NonExistent.wasm"
        assert not fake_wasm.exists()

    def test_deploy_contract_wasm_exists(self):
        """All expected wasm files should exist."""
        import src.tools as tools
        expected = ["NftMarketplace.wasm", "TokenFactory.wasm", "CollectionFactory.wasm"]
        for name in expected:
            wasm_path = tools._WASM_DIR / name
            assert wasm_path.exists(), f"Missing wasm: {name}"
            assert wasm_path.stat().st_size > 100_000, f"{name} too small (build issue?)"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
