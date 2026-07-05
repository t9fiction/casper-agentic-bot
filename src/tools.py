import json, os, subprocess, tempfile, time
from pathlib import Path
from langchain_core.tools import tool
from .mcp_client import list_tools, call_tool
from .contract_registry import register_deploy, update_contract, get_contract, list_contracts as _list_registry, get_active_contract
from .portfolio_cache import log_token_deploy, log_nft_mint, log_collection_create
from .account_analyzer import analyze_account_impl

_PROJECT_ROOT = Path(__file__).parent.parent
_WASM_DIR = _PROJECT_ROOT / "smart-contract" / "wasm"

_TOOLS_DESCRIPTION_CACHE = None


def _get_secret_key_path() -> str:
    """Write SECRET_KEY env var content to a temp file and return its path."""
    key_value = os.getenv("SECRET_KEY")
    if not key_value:
        return ""
    tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".pem", delete=False)
    tmp.write(key_value)
    tmp.close()
    return tmp.name


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
        lines.append("")
        lines.append("  - call_contract_entry_point: Call an entry point on a deployed smart contract")
        lines.append("    args: entry_point (string), session_args (dict of arg_name:value), contract_name (optional string)")
        lines.append("    Available entry points:")
        lines.append("      Token Factory: deploy_token(name, symbol, decimals, total_supply), transfer(token_id, recipient, amount), balance_of(token_id, owner), token_info(token_id), total_tokens(), mint(token_id, recipient, amount)")
        lines.append("      NFT Marketplace: mint_nft(metadata_uri, recipient), transfer_nft(token_id, recipient), list_nft(token_id, price), unlist_nft(token_id), buy_nft(token_id, buyer), nft_info(token_id), owner_of(token_id), total_nfts(), metadata_uri(token_id)")
        lines.append("      Collection Factory (named key 'collections'): create_collection(name, symbol, base_uri, mint_price), mint_nft(collection_id, recipient), transfer_nft(token_id, recipient), list_nft(token_id, price), unlist_nft(token_id), buy_nft(token_id, buyer), collection_info(collection_id), nft_info(token_id), owner_of(token_id), total_collections(), total_nfts_in_collection(collection_id), nfts_by_collection(collection_id, page, page_size), metadata_uri(token_id)")
        lines.append("")
        lines.append("  - deploy_contract: Deploy a new smart contract instance to the network")
        lines.append("    args: contract_name (string), wasm_name (string, default: NftMarketplace)")
        lines.append("")
        lines.append("  - verify_contract_deployment: Check if a submitted deploy completed")
        lines.append("    args: tx_hash (string)")
        lines.append("")
        lines.append("  - list_deployed_contracts: List all deployed contract instances")
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
    secret_key_path = _get_secret_key_path()
    if not secret_key_path:
        return "Error: Secret key not found. Set the SECRET_KEY environment variable to your PEM key content."

    node = os.getenv("CASPER_NODE", "http://65.109.115.124:7777")
    chain = os.getenv("CASPER_NETWORK", "casper-test")

    amount_motes = int(amount_in_cspr * 1_000_000_000)

    cmd = [
        "casper-client", "put-transaction", "transfer",
        "--node-address", node,
        "--chain-name", chain,
        "--secret-key", secret_key_path,
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
    finally:
        if os.environ.get("SECRET_KEY"):
            try:
                os.unlink(secret_key_path)
            except OSError:
                pass


def _log_contract_call(entry_point: str, session_args: dict, tx_hash: str, contract_name: str = None):
    wallet = os.getenv("WALLET_ACCOUNT_HASH", "")
    args = session_args or {}
    if entry_point == "deploy_token":
        log_token_deploy(
            name=args.get("name", ""),
            symbol=args.get("symbol", ""),
            decimals=int(args.get("decimals", 0)),
            total_supply=str(args.get("total_supply", "0")),
            tx_hash=tx_hash,
            contract_name=contract_name,
            recipient=wallet,
        )
    elif entry_point == "mint_nft":
        recipient = args.get("recipient", args.get("buyer", wallet))
        log_nft_mint(
            token_id=args.get("token_id", ""),
            metadata_uri=args.get("metadata_uri", ""),
            recipient=recipient,
            contract_name=contract_name,
            tx_hash=tx_hash,
            collection=contract_name or "nft_marketplace",
        )
    elif entry_point == "create_collection":
        log_collection_create(
            name=args.get("name", ""),
            symbol=args.get("symbol", ""),
            base_uri=args.get("base_uri", ""),
            mint_price=str(args.get("mint_price", "0")),
            tx_hash=tx_hash,
            contract_name=contract_name or "collections",
            creator=wallet,
        )


@tool
async def call_contract_entry_point(entry_point: str, session_args: dict = None, contract_name: str = None):
    """Call an entry point on a deployed smart contract.

    Use this when the user wants to deploy tokens, check balances,
    transfer tokens, mint tokens, or query token info on-chain,
    or mint/list/buy NFTs.
    The Token Factory manages multiple tokens with metadata.
    The NFT Marketplace manages NFTs with listing and buying.

    You can target a specific contract by name (from deploy_contract)
    or leave contract_name empty to use the default Token Factory contract.

    Args:
        entry_point: The entry point name (e.g. deploy_token, transfer, balance_of, token_info, mint, mint_nft, list_nft, buy_nft, nft_info)
        session_args: Named arguments as a dict (e.g. {"name": "MyToken", "symbol": "MTK", "decimals": 8, "total_supply": "1000000"})
        contract_name: Optional — name of a previously deployed contract instance to target
    """
    if session_args is None:
        session_args = {}

    secret_key_path = _get_secret_key_path()
    if not secret_key_path:
        return "Error: Secret key not found. Set the SECRET_KEY environment variable to your PEM key content."

    node = os.getenv("CASPER_NODE", "http://65.109.115.124:7777")
    chain = os.getenv("CASPER_NETWORK", "casper-test")

    # Resolve which contract to call
    subcommand = "package"
    pkg_identifier = None

    if contract_name:
        entry = get_contract(contract_name)
        if not entry:
            return f"Error: No contract found with name '{contract_name}'. Use deploy_contract first or list_deployed_contracts to see available ones."
        if entry.get("status") != "active":
            return f"Error: Contract '{contract_name}' status is '{entry.get('status')}'. Wait for deployment to complete and use verify_contract_deployment."
        # Use the named key (package-name subcommand) - works for all Casper 2.0 contracts
        subcommand = "package-name"
        pkg_identifier = entry["named_key"]
    else:
        pkg_identifier = os.getenv("CONTRACT_PACKAGE_HASH", "")
        if not pkg_identifier:
            return "Error: No default CONTRACT_PACKAGE_HASH configured and no contract_name specified. Deploy a contract first or specify contract_name."

    if subcommand == "package-name":
        cmd = [
            "casper-client", "put-transaction", "package-name",
            "--node-address", node,
            "--chain-name", chain,
            "--secret-key", secret_key_path,
            "--transaction-package-name", pkg_identifier,
            "--session-entry-point", entry_point,
            "--payment-amount", "10000000000",
            "--standard-payment", "true",
            "--gas-price-tolerance", "1",
        ]
    else:
        cmd = [
            "casper-client", "put-transaction", "package",
            "--node-address", node,
            "--chain-name", chain,
            "--secret-key", secret_key_path,
            "--contract-package-hash", pkg_identifier,
            "--session-entry-point", entry_point,
            "--payment-amount", "10000000000",
            "--standard-payment", "true",
            "--gas-price-tolerance", "1",
        ]

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
        cmd.extend(["--session-arg", arg_str])

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode != 0:
            error_msg = result.stderr.strip() or result.stdout.strip()
            import sys
            print(f"DEBUG: Contract call failed - {error_msg}", file=sys.stderr)
            return f"Contract call failed: {error_msg}"

        data = json.loads(result.stdout)
        tx_hash = data.get("result", {}).get("transaction_hash", {})
        if isinstance(tx_hash, dict):
            tx_hash = tx_hash.get("Version1", str(tx_hash))

        import sys
        print(f"DEBUG: Contract call successful", file=sys.stderr)
        print(f"DEBUG: Entry point: {entry_point}", file=sys.stderr)
        print(f"DEBUG: TX Hash: {tx_hash}", file=sys.stderr)
        print(f"DEBUG: Session args: {session_args}", file=sys.stderr)

        _log_contract_call(entry_point, session_args, tx_hash, contract_name)

        return (
            f"✅ Contract call submitted successfully!\n"
            f"Entry point: {entry_point}\n"
            f"Transaction Hash: {tx_hash}\n"
            f"Arguments: {json.dumps(session_args)}\n"
            f"\n⏳ Please wait 30-60 seconds for execution on-chain.\n"
            f"Verification Command: casper-client get-transaction --node-address {node} {tx_hash}\n"
            f"\nTo verify in chat, say: 'verify deployment {tx_hash}'"
        )
    except subprocess.TimeoutExpired:
        return "Contract call timed out after 120 seconds."
    except json.JSONDecodeError:
        return f"Contract call submitted but could not parse response: {result.stdout[:500]}"
    except FileNotFoundError:
        return "Error: casper-client not found. Install it first."
    except Exception as e:
        return f"Contract call failed: {str(e)}"
    finally:
        if os.environ.get("SECRET_KEY"):
            try:
                os.unlink(secret_key_path)
            except OSError:
                pass


@tool
async def analyze_account(account_hash: str):
    """Get detailed info about a Casper account including balance and biggest transactions.

    Analyzes an account by querying on-chain data and scanning recent blocks
    for the largest transfers sent and received.

    Args:
        account_hash: The account hash (e.g. "account-hash-...")
    """
    return await analyze_account_impl(account_hash)


@tool
async def deploy_contract(contract_name: str, wasm_name: str = "NftMarketplace"):
    """Deploy a new smart contract instance to the Casper network.

    Use this when the user wants to create a new NFT collection or deploy
    a new contract. Each deployment creates an independent contract on-chain.

    Args:
        contract_name: A unique name for this contract instance (e.g. 'cyberpunks', 'bored_apes')
        wasm_name: Which wasm to deploy — 'NftMarketplace' or 'TokenFactory' (default: NftMarketplace)
    """
    wasm_path = _WASM_DIR / f"{wasm_name}.wasm"
    if not wasm_path.exists():
        return f"Error: Wasm file not found at {wasm_path}"

    secret_key_path = _get_secret_key_path()
    if not secret_key_path:
        return "Error: Secret key not found. Set the SECRET_KEY environment variable."

    existing = get_contract(contract_name)
    if existing:
        return f"Contract '{contract_name}' already exists (status: {existing.get('status')}). Use a different name."

    node = os.getenv("CASPER_NODE", "http://65.109.115.124:7777")
    chain = os.getenv("CASPER_NETWORK", "casper-test")
    named_key = contract_name

    cmd = [
        "casper-client", "put-transaction", "session",
        "--node-address", node,
        "--chain-name", chain,
        "--secret-key", secret_key_path,
        "--wasm-path", str(wasm_path),
        "--payment-amount", "500000000000",
        "--transferred-value", "0",
        "--session-arg", f"odra_cfg_package_hash_key_name:string='{named_key}'",
        "--session-arg", "odra_cfg_allow_key_override:bool='false'",
        "--session-arg", "odra_cfg_is_upgradable:bool='true'",
        "--session-arg", "odra_cfg_is_upgrade:bool='false'",
        "--install-upgrade",
        "--standard-payment", "true",
        "--gas-price-tolerance", "1",
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode != 0:
            return f"Deploy failed: {result.stderr.strip() or result.stdout.strip()}"
        data = json.loads(result.stdout)
        tx_hash = data.get("result", {}).get("transaction_hash", {})
        if isinstance(tx_hash, dict):
            tx_hash = tx_hash.get("Version1", str(tx_hash))

        register_deploy(contract_name, wasm_name, str(tx_hash), named_key, status="pending")

        return (
            f"✅ Deploy submitted for '{contract_name}'!\n"
            f"Transaction hash: {tx_hash}\n"
            f"Named key: {named_key}\n"
            f"Wasm: {wasm_name}\n\n"
            f"⏳ Waiting for execution... Use verify_contract_deployment(tx_hash=\"{tx_hash}\") "
            f"after ~30 seconds to check if it succeeded and get the contract hash."
        )
    except subprocess.TimeoutExpired:
        return "Deploy timed out after 120 seconds."
    except json.JSONDecodeError:
        return f"Deploy submitted but could not parse response: {result.stdout[:500]}"
    except FileNotFoundError:
        return "Error: casper-client not found. Install it first."
    except Exception as e:
        return f"Deploy failed: {str(e)}"
    finally:
        if os.environ.get("SECRET_KEY"):
            try:
                os.unlink(secret_key_path)
            except OSError:
                pass


@tool
async def verify_contract_deployment(tx_hash: str):
    """Check if a submitted contract deploy has been executed on-chain.

    Use this after deploy_contract to verify the deployment succeeded.
    Once verified, the contract can be used via call_contract_entry_point
    with the contract_name used during deploy_contract.

    Args:
        tx_hash: The transaction hash returned by deploy_contract
    """
    node = os.getenv("CASPER_NODE", "http://65.109.115.124:7777")
    cmd = [
        "casper-client", "get-transaction",
        "--node-address", node,
        tx_hash,
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            return f"Query failed: {result.stderr.strip() or result.stdout.strip()}"

        data = json.loads(result.stdout)
        exec_info = data.get("result", {}).get("execution_info", {})
        tx_result = exec_info.get("execution_result", {})
        if isinstance(tx_result, dict) and tx_result.get("Version2"):
            exec_data = tx_result["Version2"]
            error = exec_data.get("error_message")
            if error:
                return f"❌ Deploy failed: {error}"

            # Extract package_hash and contract_hash from effects
            effects = exec_data.get("effects", [])
            package_hash = ""
            contract_key = ""
            named_key = ""
            access_uref_addr = ""

            registry = _list_registry()
            matched_name = None
            for name, info in registry.items():
                if info.get("tx_hash") == tx_hash:
                    matched_name = name
                    named_key = info.get("named_key", name)
                    break

            for effect in effects:
                kind = effect.get("kind", {})
                if isinstance(kind, dict) and "AddKeys" in kind:
                    entries = kind["AddKeys"]
                    if isinstance(entries, list):
                        for entry in entries:
                            entry_name = entry.get("name", "")
                            entry_key = entry.get("key", "")
                            if entry_name == named_key:
                                contract_key = entry_key
                            elif entry_name.endswith("_access_token") and entry_key.startswith("uref-"):
                                access_uref_addr = entry_key[5:].split("-")[0]

            if access_uref_addr:
                package_hash = f"hash-{access_uref_addr}"

            if matched_name:
                update_contract(
                    matched_name,
                    package_hash=package_hash or None,
                    contract_hash=contract_key or None,
                    status="active",
                )
                parts = []
                if package_hash:
                    parts.append(f"Package: {package_hash}")
                if contract_key:
                    parts.append(f"Contract: {contract_key}")
                hash_info = "\n".join(parts)
                return (
                    f"✅ Contract '{matched_name}' deployed successfully!\n"
                    f"Named key: {named_key}\n"
                    f"{hash_info}\n"
                    f"You can now use call_contract_entry_point with "
                    f"contract_name=\"{matched_name}\" to interact with it."
                )
            else:
                return (
                    f"✅ Deploy executed successfully (no errors).\n"
                    f"Transaction: {tx_hash[:20]}...\n"
                    f"The contract was deployed but not found in the local registry."
                )

        return f"⏳ Deploy still pending. Check again in 30 seconds."
    except subprocess.TimeoutExpired:
        return "Query timed out."
    except json.JSONDecodeError:
        return f"Could not parse response: {result.stdout[:500]}"
    except FileNotFoundError:
        return "Error: casper-client not found."
    except Exception as e:
        return f"Query failed: {str(e)}"


@tool
async def list_deployed_contracts():
    """List all contract instances that have been deployed through this agent.

    Shows the name, wasm type, status, and package hash of each deployed contract.
    """
    registry = _list_registry()
    if not registry:
        return "No contracts have been deployed yet. Use deploy_contract to create one."

    lines = ["📋 Deployed Contracts:", ""]
    for name, info in registry.items():
        status_icon = "✅" if info.get("status") == "active" else "⏳" if info.get("status") == "pending" else "❌"
        lines.append(f"{status_icon} {name}")
        lines.append(f"   Wasm: {info.get('wasm_name', 'NftMarketplace')}")
        lines.append(f"   Status: {info.get('status', 'unknown')}")
        if info.get("package_hash"):
            lines.append(f"   Package: {info['package_hash']}")
        if info.get("tx_hash"):
            lines.append(f"   Tx: {info['tx_hash'][:16]}...")
        lines.append("")
    return "\n".join(lines)
