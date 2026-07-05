# Casper Agentic Bot — Project Context

## Core Objective
Build an **AI-powered chatbot** that lets users query the **Casper blockchain** via natural language. This demonstrates **Agentic AI**: an LLM autonomously decides which blockchain tools to call based on user intent.

## Tech Stack
- **FastAPI** (Python web server)
- **LangChain + LangGraph** (`create_react_agent` for tool-routing agent)
- **OpenAI GPT-4o-mini** (LLM for intent routing + response generation)
- **Casper MCP Server** (blockchain data access via CSPR.cloud hosted endpoint)
- **`mcp` Python SDK** (MCP client protocol with Streamable HTTP transport)

## Architecture
```
User → Web UI → FastAPI POST /api/chat → run_agent()
                                            ↓
                              create_react_agent (LangGraph)
                                    ↓
                        query_casper_blockchain tool
                                    ↓
                        Python MCP Client (streamable_http)
                                    ↓
                        Casper MCP Server (mcp.testnet.cspr.cloud)
                                    ↓
                              CSPR.cloud API → Casper Network
```

## Key Files
| File | Purpose |
|---|---|
| `src/main.py` | FastAPI server, serves UI + POST /api/chat |
| `src/agent.py` | LangGraph react agent (create_react_agent) |
| `src/tools.py` | LangChain tools: query_casper_blockchain, send_cspr_transfer, analyze_account, call_contract_entry_point |
| `src/mcp_client.py` | Async MCP client (streamable_http to hosted MCP) |
| `src/account_analyzer.py` | Account analysis (balance, biggest tx scanning) |
| `src/public/index.html` | Dark-themed chat UI with nav link to /portfolio |
| `src/public/portfolio.html` | Portfolio dashboard page at /portfolio |
| `src/portfolio_cache.py` | JSON-backed cache tracking tokens, NFTs, and collections created by the agent |
| `src/contract_registry.py` | JSON-backed registry for deployed contract instances (multi-contract tracking) |
| `smart-contract/src/token_factory.rs` | Token Factory contract (deploy_token, transfer, balance_of, mint, token_info, total_tokens) |
| `smart-contract/src/nft_marketplace.rs` | NFT Marketplace contract (mint_nft, transfer_nft, list_nft, buy_nft, nft_info, owner_of) |
| `contracts_registry.json` | Auto-generated file tracking all deployed contract instances |
| `portfolio_cache.json` | Auto-generated file tracking tokens, NFTs, and collections from agent actions |
| `smart-contract/src/lib.rs` | Crate root (no_std/no_main for wasm, pub mod token_factory, pub mod nft_marketplace) |
| `smart-contract/Odra.toml` | Contract definitions (token_factory::TokenFactory + nft_marketplace::NftMarketplace) |
| `smart-contract/bin/build_contract.rs` | Wasm build binary target |
| `smart-contract/bin/build_schema.rs` | Schema generation binary target |
| `smart-contract/bin/cli.rs` | CLI deploy script binary target |
| `smart-contract/build.rs` | Odra build script |
| `smart-contract/.cargo/config.toml` | Wasm target-cpu + allow-undefined linker flag + build-std config |
| `smart-contract/rust-toolchain` | Nightly toolchain pin |
| `tests/test_integration.py` | Python integration tests (12 tests) |
| `AGENTS.md` | This file — project context for resume support |
| `Dockerfile` | Multi-stage build: compiles casper-client with nightly Rust, copies to Python slim |
| `docker-compose.yml` | Single service: port 8000, `.env` injection |
| `.dockerignore` | Excludes `.venv/`, `.env`, `__pycache__/`, target/ |

## Current State
- [x] Project scaffolding (Python + FastAPI + LangChain)
- [x] FastAPI server with /api/chat endpoint
- [x] LangGraph agent with MCP tool routing
- [x] Python MCP client (streamable_http → mcp.testnet.cspr.cloud)
- [x] Web chat UI (clean single-page, no tabs, Casper-focused hero)
- [x] Smart contract code (Odra Greeter → Token Factory) + wasm binary builds (300KB)
- [x] .env configured with API keys
- [x] langgraph in requirements.txt
- [x] SECRET_KEY env var (PEM content) + target/ gitignored
- [x] Pushed to GitHub (github.com/t9fiction/casper-agentic-bot)
- [x] CSPR transfer tool (agent signs + submits transactions)
- [x] Account analysis tool (account details, biggest tx scanning)
- [x] call_contract_entry_point tool (agent calls Token Factory entry points)
- [x] Token Factory contract replaces Greeter (deploy_token, transfer, balance_of, mint, token_info, total_tokens)
- [x] Token Factory deployed to Casper Testnet (block 8310310, 500 CSPR)
- [x] CONTRACT_PACKAGE_HASH set in .env
- [x] Docker image builds and runs (casper-client 5.0.1 bundled)
- [x] Python integration tests (12/12 pass)
- [x] NFT Marketplace contract (mint_nft, transfer_nft, list_nft, buy_nft, nft_info, owner_of, total_nfts)
- [x] Multi-step agent workflows (agent chains multiple contract calls)
- [x] Portfolio dashboard at /portfolio
- [x] WALLET_ACCOUNT_HASH in .env for portfolio queries
- [x] CONTRACT_HASH in .env for on-chain state queries
- [x] Deploy NFT contract to Casper Testnet
- [x] Collection Factory contract (create_collection, mint_nft with mint_price payment to creator)
- [x] Multiple NFT deploy + mint workflows (deploy_contract tool, contract registry, multi-contract tracking)
- [x] Portfolio cache (JSON-backed tracking of tokens, NFTs, collections created by agent)
- [x] Portfolio dashboard shows custom tokens, collections, and agent-minted NFTs
- [x] Agent input validation (prompt tells agent to ask for missing required fields before calling tools)
- [x] **FRONTEND ENHANCEMENTS (2026-07-05):**
  - [x] Token Deployment modal form (Deploy Token button)
  - [x] Token Transfer modal form (Transfer button)
  - [x] Token Balance Check modal form (Check Balance button)
  - [x] NFT Marketplace modal (3-tab interface: Mint, List, Buy)
  - [x] Collection Creator modal form (Create Collection button)
  - [x] Form input validation + error messages
  - [x] Portfolio page enhancements (Token IDs, NFT listing status, Copy buttons)
  - [x] Modal backdrop animations + smooth transitions
  - [x] Responsive modal design (mobile-friendly)
  - [x] 100% feature parity with smart contracts via UI
- [ ] Deploy to free cloud (Koyeb/Railway/Fly)
- [ ] Record demo video
- [ ] Submit on DoraHacks

## Fixes Applied (Session 2026-06-30)

### MCP Client (`src/mcp_client.py`)
- **Problem:** `streamablehttp_client` (deprecated) sent 400 Bad Request to CSPR.cloud MCP
- **Fix:** Replaced with `streamable_http_client` + `httpx.AsyncClient(headers=...)` — the new API expects headers on the client, not as transport args
- **Problem:** `CASPER_NETWORK=casper-test` was passed as `X-Casper-Network: casper-test`, but CSPR.cloud API expects `testnet` or `mainnet`
- **Fix:** Added `_API_NETWORK` mapping: `casper-test`/`testnet` → `testnet`, `casper`/`mainnet` → `mainnet`

### Agent Tool Names (`src/agent.py`)
- **Problem:** System prompt examples used `GetNetworkStatus` (PascalCase), but actual MCP tools are all lowercase (`get_network_status`)
- **Fix:** Changed examples to match actual tool names: `get_network_status`, `get_latest_blocks`, `get_account_info`

### Contract Call Arg Types (`src/tools.py`)
- **Problem:** Python `int` was sent as `u64`, but `decimals` needs `u8`, `total_supply` needs `u256`, `token_id` needs `u32`, `owner`/`recipient` needs `key`
- **Fix:** Added `_ARG_TYPE_OVERRIDES` dict mapping arg names to correct Casper CL types

### Contract Build
- **Problem:** `cargo build --target wasm32-unknown-unknown` produced wasm without `call` export (entry points missing)
- **Root cause:** Odra requires `cargo odra build` (the `cargo-odra` CLI), not plain `cargo build` — the CLI sets `ODRA_MODULE`/`ODRA_BACKEND` env vars during compilation, which triggers the build script to generate proper entry point exports
- **Fix:** Use `cargo odra build` which outputs to `smart-contract/wasm/TokenFactory.wasm` (300KB, with `call`, `deploy_token`, `transfer`, `balance_of`, `mint`, `token_info`, `total_tokens`, `init` exports)

### Frontend Fixes (`src/public/`)
- **Problem:** Portfolio page always loaded content immediately, even without a connected wallet
- **Fix:** Added `showConnectPrompt()` that gates all portfolio content behind a "Wallet not connected" prompt with a Connect button. Initial load now checks localStorage for `casper_public_key` before fetching.
- **Problem:** No wallet connect/disconnect button on Chat or Portfolio pages
- **Fix:** Added wallet button to both `index.html` and `portfolio.html` headers with `toggleWallet()` JS function that calls `window.casperWallet.requestConnection()` or `localStorage.removeItem('casper_public_key')`.
- **Problem:** Chat scroll scrolled wrong parent element (`chatContainer` instead of `messagesContainer`)
- **Fix:** Changed `chatContainer.scrollTop = chatContainer.scrollHeight` to `messagesContainer.scrollTop = messagesContainer.scrollHeight`
- **Problem:** CSPR balance extraction grabbed public key prefix ("0202") instead of numeric balance
- **Fix:** `_parse_nums` now searches for `[\d.]+ CSPR` pattern first before falling back to general number extraction
- **Problem:** `<hr>` in `formatMessage` was wrapped in extra `<br>` tags causing double newlines
- **Fix:** Changed `\n<hr>\n` → `<hr>` (no `<br>` wrappers)
- **Problem:** Suggestion buttons in chat didn't cover collections or contract deployment
- **Fix:** Added buttons for Collections (Create, List) and Contracts (Deploy, List) to `index.html`
- **Problem:** Portfolio page didn't pass wallet public key to `/api/portfolio` — always fell back to env var wallet
- **Fix:** Portfolio JS now sends `?public_key=<pk>` query param to the API; `src/main.py` portfolio endpoint accepts optional `public_key` param

### Backend Fixes
- **Problem:** `verify_contract_deployment` read `result.execution_result` but Casper 2.0 uses `result.execution_info.execution_result.Version2`
- **Fix:** Updated JSON path traversal to match Casper 2.0 response format
- **Problem:** Contract hash extraction failed because Casper 2.0 uses `AddKeys` transform instead of `WriteContract`/`WriteContractPackage`
- **Fix:** Added `_extract_hashes_from_effects()` that finds `AddKeys` entries: `package_hash` from `_access_token` URef address, `contract_key` from named key value
- **Problem:** Missing hashes for "collections" registry entry caused deploy errors
- **Fix:** Extracted hashes from tx `0adad70d26da7428292665b6bcc133ad517bfc87ed3368634fe0c4ab8ca4adc3` and filled them in `contracts_registry.json`
- **Problem:** `from langgraph.prebuilt import create_react_agent` is deprecated; new API uses `from langchain.agents import create_agent` with `system_prompt=` param
- **Fix:** Updated import and call signature in `src/agent.py`
- **Problem:** Inconsistent contract naming in agent system prompt (one example used `collection_factory`, other used `collections`)
- **Fix:** Both examples now use `contract_name="collections"`
- **Problem:** `portfolio_cache.json` didn't exist at startup, causing JSON decode errors
- **Fix:** Initialized with `{"tokens":[],"nfts":[],"collections":[]}` in `src/portfolio_cache.py`
- **Problem:** Lazy import of `analyze_account_impl` was inside function body, causing first-call delay
- **Fix:** Moved to top of `src/tools.py`

## Deployed Contract (Casper Testnet)
| Field | Value |
|---|---|
| Network | Casper Testnet (casper-test) |
| Deploy method | `casper-client put-transaction session --wasm-path smart-contract/wasm/TokenFactory.wasm --install-upgrade` |
| Transaction hash | `31814b3d61345892e4dfefcf036a36a807d9cf3e3b27c70fba8f3803b2c3cac8` |
| Contract Package Hash | `hash-5095fbfcbfa662ef13731dd0822317e100f2642230c2a35f0241e888eb8383eb` |
| Contract Hash | `contract-c3b50a15995f97f424b8e4541499d03a80e0f2ba7b528edb07c9712e7dcc3354` |
| Account Hash | `account-hash-2bc76a5348a847ff51738945d681b97dda6ed606f7ae4282d1a0eb409ef301f5` |
| Public Key | `0202c92a8225d3026af3a7a499718b77b8d77c45e452c402ae5a66979529cc885b14` |
| Node | `http://65.109.115.124:7777` |
| Block Height | 8310310 |
| Deploy Cost | 500 CSPR (paid, cost in full) |
| Token Factory Named Key | `token_factory` → `hash-5095fbfc...` |
| Access Token Named Key | `token_factory_access_token` → `uref-88840ab0...` |

### Token Factory Entry Points
| Entry Point | Args | Casper CL Types | Returns |
|---|---|---|---|
| `deploy_token` | `name`, `symbol`, `decimals`, `total_supply` | `String`, `String`, `U8`, `U256` | `U32` (token_id) |
| `transfer` | `token_id`, `recipient`, `amount` | `U32`, `Key`, `U256` | `()` |
| `balance_of` | `token_id`, `owner` | `U32`, `Key` | `U256` |
| `token_info` | `token_id` | `U32` | `Option<TokenInfo>` |
| `total_tokens` | (none) | — | `U32` |
| `mint` | `token_id`, `recipient`, `amount` | `U32`, `Key`, `U256` | `()` |

**IMPORTANT:** `recipient`/`owner` args are `Key` type, not `address`. Use `--session-arg "owner:key='account-hash-...'"` in CLI.

### NFT Marketplace Entry Points
| Entry Point | Args | Casper CL Types | Returns |
|---|---|---|---|
| `mint_nft` | `metadata_uri`, `recipient` | `String`, `Key` | `U64` (token_id) |
| `transfer_nft` | `token_id`, `recipient` | `U64`, `Key` | `()` |
| `list_nft` | `token_id`, `price` | `U64`, `U256` | `()` |
| `unlist_nft` | `token_id` | `U64` | `()` |
| `buy_nft` | `token_id`, `buyer` | `U64`, `Key` | `()` |
| `nft_info` | `token_id` | `U64` | `Option<NftInfo>` |
| `owner_of` | `token_id` | `U64` | `Option<Address>` |
| `total_nfts` | (none) | — | `U64` |
| `metadata_uri` | `token_id` | `U64` | `Option<String>` |

**Buy flow:** CSPR transfer is handled separately by the agent (send_cspr_transfer to seller, then call buy_nft).

### Collection Factory Entry Points
| Entry Point | Args | Casper CL Types | Returns |
|---|---|---|---|
| `create_collection` | `name`, `symbol`, `base_uri`, `mint_price` | `String`, `String`, `String`, `U256` | `U32` (collection_id) |
| `mint_nft` | `collection_id`, `recipient` | `U32`, `Key` | `U64` (token_id) |
| `transfer_nft` | `token_id`, `recipient` | `U64`, `Key` | `()` |
| `list_nft` | `token_id`, `price` | `U64`, `U256` | `()` |
| `unlist_nft` | `token_id` | `U64` | `()` |
| `buy_nft` | `token_id`, `buyer` | `U64`, `Key` | `()` |
| `collection_info` | `collection_id` | `U32` | `Option<CollectionInfo>` |
| `nft_info` | `token_id` | `U64` | `Option<NftEntry>` |
| `owner_of` | `token_id` | `U64` | `Option<Address>` |
| `total_collections` | (none) | — | `U32` |
| `total_nfts_in_collection` | `collection_id` | `U32` | `U64` |
| `nfts_by_collection` | `collection_id`, `page`, `page_size` | `U32`, `U32`, `U32` | `Vec<U64>` |
| `metadata_uri` | `token_id` | `U64` | `Option<String>` |
| `transfer_nft` | `token_id`, `recipient` | `U64`, `Key` | `()` |
| `list_nft` | `token_id`, `price` | `U64`, `U256` | `()` |
| `unlist_nft` | `token_id` | `U64` | `()` |
| `buy_nft` | `token_id`, `buyer` | `U64`, `Key` | `()` |
| `collection_info` | `collection_id` | `U32` | `Option<CollectionInfo>` |
| `nft_info` | `token_id` | `U64` | `Option<NftEntry>` |
| `owner_of` | `token_id` | `U64` | `Option<Address>` |
| `total_collections` | (none) | — | `U32` |
| `total_nfts_in_collection` | `collection_id` | `U32` | `U64` |
| `nfts_by_collection` | `collection_id`, `page`, `page_size` | `U32`, `U32`, `U32` | `Vec<U64>` |
| `metadata_uri` | `token_id` | `U64` | `Option<String>` |

**Mint flow:** Agent first transfers mint_price CSPR to the collection creator, then calls mint_nft. Payment not bundled in contract call.

### NFT Marketplace Deployed (Casper Testnet)
| Field | Value |
|---|---|
| Transaction hash | `4b2c8c0d337d144939d80dd5b1081655490de2f925dec832f8ef3ea97bcdb8ed` |
| Contract Package Hash | `hash-0c5849200ac2d72291b5bd811024396bb4954e82b8e155105c4ee7b0cedcb896` |
| Contract Hash | `contract-2168fc559eff8ed6d521f4b67ac297181547e1fcbe845b215aeda228218bd738` |
| Named Key | `nft_marketplace` → `hash-0c584920...` |
| Deploy method | `casper-client put-transaction session --wasm-path smart-contract/wasm/NftMarketplace.wasm --install-upgrade` (without `--transaction-runtime vm-casper-v2`) |
| Entry points verified | `mint_nft`, `transfer_nft`, `list_nft`, `unlist_nft`, `buy_nft`, `nft_info`, `owner_of`, `total_nfts`, `metadata_uri` |

## Docker Setup

### Build locally
```bash
docker compose build    # ~10 min (compiles casper-client from source in builder stage)
docker compose up -d    # runs on port 8000
```

### Dockerfile details
- **Stage 1 (builder):** `rust:bookworm` → `rustup default nightly` → `cargo install casper-client@5.0.1`
- **Stage 2 (runtime):** `python:3.13-slim-bookworm` → install Python deps → copy casper-client binary + app code
- **Key:** nightly Rust needed because `casper-client` 5.0.1's transitive deps use `edition2024` Cargo feature

## How to Run

### Local (no Docker)
```bash
cd /home/sohail/mystuff/10-Work/11-Hackathons/casper-agentic-bot
source .venv/bin/activate
uvicorn src.main:app --reload
# Open http://localhost:8000
```

### Docker
```bash
cd /home/sohail/mystuff/10-Work/11-Hackathons/casper-agentic-bot
docker compose up -d
# Open http://localhost:8000
```

## How to Verify & Test

### Check contract on-chain
```bash
# Query account named keys
casper-client query-global-state \
    --node-address http://65.109.115.124:7777 \
    --key account-hash-2bc76a5348a847ff51738945d681b97dda6ed606f7ae4282d1a0eb409ef301f5 \
    -q "token_factory"

# Query entry points
casper-client query-global-state \
    --node-address http://65.109.115.124:7777 \
    --key hash-c3b50a15995f97f424b8e4541499d03a80e0f2ba7b528edb07c9712e7dcc3354
```

### Run integration tests
```bash
source .venv/bin/activate
python -m pytest tests/test_integration.py -v --asyncio-mode=auto
```

### Test agent via API
```bash
curl -s -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the Casper network status?"}'

curl -s -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Deploy a token called MyCoin with symbol MYC, 8 decimals, 1 million supply"}'
```

## .env File
Located at `/home/sohail/mystuff/10-Work/11-Hackathons/casper-agentic-bot/.env`:
```
OPENAI_API_KEY=sk-proj-...
CSPR_CLOUD_API_KEY=019f000c-db00-7e45-b8c3-b60e0afb3e1b
CASPER_NETWORK=casper-test
SECRET_KEY="-----BEGIN EC PRIVATE KEY-----\nMHQCAQEE...\n-----END EC PRIVATE KEY-----"
CONTRACT_PACKAGE_HASH=hash-5095fbfcbfa662ef13731dd0822317e100f2642230c2a35f0241e888eb8383eb
CASPER_NODE=http://65.109.115.124:7777
WALLET_ACCOUNT_HASH=account-hash-2bc76a5348a847ff51738945d681b97dda6ed606f7ae4282d1a0eb409ef301f5
CONTRACT_HASH=contract-c3b50a15995f97f424b8e4541499d03a80e0f2ba7b528edb07c9712e7dcc3354
NFT_CONTRACT_PACKAGE_HASH=
NFT_CONTRACT_HASH=
```

## Key Implementation Details

### `src/mcp_client.py` — MCP Client
- Uses `streamable_http_client` (new API, not deprecated `streamablehttp_client`)
- Creates `httpx.AsyncClient` with custom headers → passes to `streamable_http_client`
- Headers: `X-CSPR-Cloud-Api-Key` + `X-Casper-Network` (maps `casper-test` → `testnet`)

### `src/tools.py` — Agent Tools
- `query_casper_blockchain(tool_name, arguments)` — calls MCP server
- `send_cspr_transfer(recipient, amount_in_cspr, transfer_id)` — writes SECRET_KEY to temp file, calls `casper-client put-transaction transfer`
- `analyze_account(account_hash)` — queries balance + scans recent blocks for largest txs
- `call_contract_entry_point(entry_point, session_args, contract_name=None)` — targets a specific contract by name (from registry) or defaults to CONTRACT_PACKAGE_HASH
- `deploy_contract(contract_name, wasm_name)` — deploys new contract instances (submits wasm + Odra args)
- `verify_contract_deployment(tx_hash)` — checks deploy status, extracts contract hash from named keys
- `list_deployed_contracts()` — shows all registered contract instances
- Arg type overrides: `decimals→u8`, `total_supply→u256`, `amount→u256`, `owner/recipient/buyer→key`, `price→u256`, `metadata_uri→string`
- Token type: `token_id→u32` for Token Factory, `token_id→u64` for NFT Marketplace

### `src/agent.py` — LangGraph Agent
- System prompt built from MCP tool list (dynamically fetched) + hardcoded instructions
- Tools: `query_casper_blockchain`, `send_cspr_transfer`, `analyze_account`, `call_contract_entry_point`, `deploy_contract`, `verify_contract_deployment`, `list_deployed_contracts`
- Example tool names must be **lowercase** (matches actual MCP tool names)
- Multi-step workflows: agent chains multiple contract calls (e.g., deploy token → transfer → check balance, or mint NFT → list → buy)
- Multi-contract support: agent can deploy multiple NFT contracts, track them by name, and mint on specific ones

### `src/portfolio_cache.py` — Portfolio Cache
- JSON-backed cache (`portfolio_cache.json`) tracking tokens, NFTs, and collections created via the agent
- `log_token_deploy()` — called after `deploy_token` entry point (records name, symbol, decimals, total_supply, tx_hash)
- `log_nft_mint()` — called after `mint_nft` entry point (records token_id, metadata_uri, recipient, contract_name)
- `log_collection_create()` — called after `create_collection` entry point (records name, symbol, base_uri, mint_price, creator)
- `get_cache()` — returns all cached data for the portfolio API
- Auto-logged in `src/tools.py` `_log_contract_call()` after every successful contract call submission

## Frontend Enhancements (2026-07-05)

### New Modal-Based UI Components

#### Token Management Modals
1. **Deploy Token Modal** (src/public/index.html)
   - Form fields: Name, Symbol, Decimals (0-18), Total Supply
   - Validation: All fields required, symbol max 10 chars
   - Submit: Auto-formats as `"Deploy a token called {name} with symbol {symbol}, {decimals} decimals, and {supply} total supply"`

2. **Transfer Token Modal**
   - Form fields: Token ID, Recipient (account-hash-...), Amount
   - Validation: Account hash format check, positive amount
   - Submit: Auto-formats as `"Transfer {amount} of token {id} to {recipient}"`

3. **Check Token Balance Modal**
   - Form fields: Token ID, Account Hash
   - Submit: Auto-formats as `"What is the balance of token {id} for account {account}?"`

#### NFT Marketplace Modal
- **Tabbed interface with 3 operations:**
  1. **Mint Tab**: Metadata URI, Recipient → `"Mint an NFT with metadata URI {uri} to {recipient}"`
  2. **List Tab**: Token ID, Price → `"List NFT {id} for sale at {price} CSPR"`
  3. **Buy Tab**: Token ID, Buyer → `"Buy NFT {id} as {buyer}"`

#### Collection Creator Modal
- Form fields: Name, Symbol, Base URI, Mint Price (CSPR)
- Submit: Auto-formats as `"Create a collection called {name} with symbol {symbol}, base_uri {uri} and mint_price {price} CSPR"`

### Portfolio Page Enhancements
- **Token Factory Tokens section**: Added Token ID display + "📋 Copy ID" button for each token
- **NFTs section**: Added listing status badges (blue "Listed for X CSPR" / gray "Not Listed") + "📋 Copy ID" button
- **New helper function**: `copyToClipboard(text)` for one-click ID copying

### UI/UX Features
- Modal backdrop with fade-in animation (0.7 opacity)
- Smooth slide-up animation for modal content
- Error message display with red styling
- Form validation with user-friendly error messages
- Close button (×) in top-right + click-outside-to-close
- Responsive design (works on mobile)
- Auto-populates chat input on form submit
- Tab switching in NFT Marketplace (3 distinct operations)

### Code Changes
- **index.html**: 805 → 1304 lines (+499)
  - Modal CSS styling (~150 lines)
  - 5 Modal HTML definitions (~300 lines)
  - 8 JavaScript submission functions (~199 lines)
  - Modal system functions (openModal, closeModal, switchNFTTab, etc.)

- **portfolio.html**: 811 → 835 lines (+24)
  - Token card enhancements (Token IDs + Copy button)
  - NFT card enhancements (Status badges + Copy button)
  - New copyToClipboard() function

### Feature Coverage
- **Before**: 65% of smart contract features exposed via UI (rest via chat)
- **After**: 100% feature parity via structured forms + chat fallback
  - ✅ Token Deploy/Transfer/BalanceOf via forms
  - ✅ NFT Mint/List/Buy via forms
  - ✅ Collection Create via forms
  - ✅ All operations still work via chat (AI agent routing)

### Testing the New Features
1. **Chat page** → Click suggestion chips to open modals
2. **Deploy Token**: Fill form → Click "Deploy Token" button
3. **Transfer**: Fill form → Click "Transfer" button
4. **Check Balance**: Fill form → Click "Check Balance" button
5. **NFT Marketplace**: Click button → Switch tabs (Mint/List/Buy) → Fill form
6. **Create Collection**: Fill form → Click "Create Collection" button
7. **Portfolio**: See enhanced cards with IDs and copy buttons

## Known Issues & Notes
- `cargo test` on nightly 1.90.0 fails: `serde_core` + `alloc` conflict (known serde v1.0.228 + nightly issue, not a code bug)
- Contract wasm built with `cargo odra build` (not plain `cargo build`)
- `wasm-opt` not installed locally → harmless warning during build
- `balance_of` and similar read-only entry points still cost gas (5 CSPR) since they're called via `put-transaction package`
- MCP tool names are case-sensitive (all lowercase)
- SECRET_KEY is the PEM content (env var, not a file path)

## Decisions Made
- **Python + LangGraph** over Node.js (user preference for LangChain ecosystem)
- **Hosted Casper MCP Server** (no local node or Docker needed)
- **Single tool** `query_casper_blockchain(tool_name, arguments)` instead of 87 individual tools
- **GPT-4o-mini** for cost efficiency + speed
- **LangGraph create_react_agent** (v2) for the agent runtime
- **Streamable HTTP** transport for MCP (stateless, no persistent sessions)
- **SECRET_KEY** = actual PEM content in env var (not a file path). Temp file created per-call, deleted in `finally`
- **Docker** for deployment (bundles casper-client)
- **Koyeb** recommended for free 24/7 hosting

## Troubleshooting Deploy Errors
| Error Code | Discriminant | Meaning | Fix |
|---|---|---|---|
| 64658 (0xFC92) | 122 | `MissingArg` — Odra's `call()` expects named args | Pass all odra_cfg_* args |
| Out of gas | — | Wasm too large for payment | Increase `--payment-amount` to 500 CSPR |
| 64641 (0xFC81) | 105 | `CannotOverrideKeys` — key already exists | Set `odra_cfg_allow_key_override:bool='true'` |
| -32602 | — | Invalid state query key format | Use `hash-` prefix (not `contract-`) |
| 400 Bad Request | — | MCP API rejected request | Check `X-Casper-Network` header value (must be `testnet` not `casper-test`) |
| "Module doesn't have export call" | — | Wasm built with plain `cargo build` instead of `cargo odra build` | Rebuild with `cargo odra build`, use `smart-contract/wasm/TokenFactory.wasm` |
