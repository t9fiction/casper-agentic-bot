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
| `src/main.py` | FastAPI server, serves UI + POST /api/chat, monitor endpoints |
| `src/agent.py` | LangGraph react agent (create_react_agent) |
| `src/tools.py` | LangChain tools: query_casper_blockchain, send_cspr_transfer, analyze_account, call_contract_entry_point |
| `src/mcp_client.py` | Async MCP client (streamable_http to hosted MCP) |
| `src/account_analyzer.py` | Account analysis (balance, biggest tx scanning) |
| `src/monitor.py` | Background account monitor (30s poll loop) |
| `src/public/index.html` | Dark-themed chat UI with nav link to /monitor |
| `src/public/monitor.html` | Standalone monitor page at /monitor |
| `smart-contract/src/token_factory.rs` | Token Factory contract (deploy_token, transfer, balance_of, mint, token_info, total_tokens) |
| `smart-contract/src/lib.rs` | Crate root (no_std/no_main for wasm, pub mod token_factory) |
| `smart-contract/Odra.toml` | Contract definition (token_factory::TokenFactory) |
| `smart-contract/bin/build_contract.rs` | Wasm build binary target |
| `smart-contract/bin/build_schema.rs` | Schema generation binary target |
| `smart-contract/bin/cli.rs` | CLI deploy script binary target |
| `smart-contract/build.rs` | Odra build script |
| `smart-contract/.cargo/config.toml` | Wasm target-cpu + allow-undefined linker flag + build-std config |
| `smart-contract/rust-toolchain` | Nightly toolchain pin |
| `tests/test_integration.py` | Python integration tests (12 tests) |
| `AGENTS.md` | This file — project context for resume support |

## Current State
- [x] Project scaffolding (Python + FastAPI + LangChain)
- [x] FastAPI server with /api/chat endpoint
- [x] LangGraph agent with MCP tool routing
- [x] Python MCP client (streamable_http → mcp.testnet.cspr.cloud)
- [x] Web chat UI (clean single-page, no tabs, Casper-focused hero)
- [x] Smart contract code (Odra Greeter → Token Factory) + wasm binary builds (160KB)
- [x] .env configured with API keys
- [x] langgraph in requirements.txt
- [x] SECRET_KEY env var (PEM content) + target/ gitignored
- [x] Pushed to GitHub (github.com/t9fiction/casper-agentic-bot)
- [x] CSPR transfer tool (agent signs + submits transactions)
- [x] Account analysis tool (account details, biggest tx scanning)
- [x] call_contract_entry_point tool (agent calls Token Factory entry points)
- [x] Monitor feature moved to standalone /monitor page (nav links on both pages)
- [x] Token Factory contract replaces Greeter (deploy_token, transfer, balance_of, mint)
- [x] Python integration tests (12 tests pass — imports, MCP client, account analyzer, CSPR transfer, contract calls, agent responses)
- [ ] Deploy Token Factory to Casper Testnet
- [ ] Set CONTRACT_PACKAGE_HASH env var after deployment
- [ ] Record demo video
- [ ] Submit on DoraHacks

## Deployed Contract (Casper Testnet)
| Field | Value |
|---|---|
| Network | Casper Testnet (casper-test) |
| Deploy method | `put-transaction session` with `--install-upgrade` |
| Contract Package Hash | `hash-5095fbfcbfa662ef13731dd0822317e100f2642230c2a35f0241e888eb8383eb` |
| Contract Hash | `contract-c3b50a15995f97f424b8e4541499d03a80e0f2ba7b528edb07c9712e7dcc3354` |
| Account Hash | `account-hash-2bc76a5348a847ff51738945d681b97dda6ed606f7ae4282d1a0eb409ef301f5` |
| Node | `65.109.115.124:7777` |
| Block Height | 8310310 |
| Deploy Cost | 500 CSPR for Token Factory (300KB wasm) |

### Token Factory Entry Points
| Entry Point | Args | Returns | Description |
|---|---|---|---|
| `deploy_token` | `name: String, symbol: String, decimals: u8, total_supply: U256` | `u32` (token_id) | Deploy a new token, deployer gets full supply |
| `transfer` | `token_id: u32, recipient: Address, amount: U256` | `()` | Transfer tokens between accounts |
| `balance_of` | `token_id: u32, owner: Address` | `U256` | Query token balance |
| `token_info` | `token_id: u32` | `Option<TokenInfo>` | Get token metadata |
| `total_tokens` | (none) | `u32` | Count of deployed tokens |
| `mint` | `token_id: u32, recipient: Address, amount: U256` | `()` | Mint new tokens (deployer only) |

### Deploy Notes (Token Factory)
- Wasm binary: 160KB (smaller than Greeter's 280KB)
- Deploy command template (fill in actual env vars):
  ```bash
  casper-client put-transaction session \
    --node-address $NODE --chain-name $CHAIN \
    --secret-key $KEY \
    --session-path smart-contract/target/wasm32-unknown-unknown/release/casper_agentic_token_factory_build_contract.wasm \
    --install-upgrade \
    --session-arg "odra_cfg_package_hash_key_name:string='token_factory'" \
    --session-arg "odra_cfg_allow_key_override:bool='true'" \
    --session-arg "odra_cfg_is_upgradable:bool='true'" \
    --session-arg "odra_cfg_is_upgrade:bool='false'" \
    --payment-amount 500000000000
  ```

### Test Note
- `cargo test` on nightly 1.90.0 fails due to `serde_core` alloc conflict (nightly toolchain issue, not code bug)
- Contract compiles to wasm correctly (verified: 160KB .wasm file)
- Python integration tests pass (12/12): `python -m pytest tests/test_integration.py -v --asyncio-mode=auto`

## How to Run
```bash
cd casper-agentic-bot
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env: add OPENAI_API_KEY + CSPR_CLOUD_API_KEY (free at cspr.cloud)
uvicorn src.main:app --reload
# Open http://localhost:8000
```

## How to Verify Deployed Contract
```bash
# Query account named keys to confirm contract package exists
casper-client query-global-state \
    --node-address http://65.109.115.124:7777 \
    --key account-hash-2bc76a5348a847ff51738945d681b97dda6ed606f7ae4282d1a0eb409ef301f5 \
    -q "token_factory"

# Query contract entity to see entry points
casper-client query-global-state \
    --node-address http://65.109.115.124:7777 \
    --key hash-<CONTRACT_HASH>
```

## How to Call Entry Points (Read & Write)

Set env vars:
```bash
export NODE=http://65.109.115.124:7777
export CHAIN=casper-test
export PACKAGE=hash-<DEPLOYED_PACKAGE_HASH>
export KEY=<(echo "$SECRET_KEY")
```

**Deploy a token:** `deploy_token`
```bash
casper-client put-transaction package \
    --node-address $NODE --chain-name $CHAIN \
    --secret-key $KEY \
    --contract-package-hash $PACKAGE \
    --session-entry-point deploy_token \
    --session-arg "name:string='MyToken'" \
    --session-arg "symbol:string='MTK'" \
    --session-arg "decimals:u8='8'" \
    --session-arg "total_supply:u256='1000000'" \
    --payment-amount 5000000000 \
    --standard-payment true --gas-price-tolerance 1
```

**Transfer tokens:** `transfer`
```bash
casper-client put-transaction package \
    --node-address $NODE --chain-name $CHAIN \
    --secret-key $KEY \
    --contract-package-hash $PACKAGE \
    --session-entry-point transfer \
    --session-arg "token_id:u32='0'" \
    --session-arg "recipient:address='account-hash-...'" \
    --session-arg "amount:u256='100'" \
    --payment-amount 5000000000 \
    --standard-payment true --gas-price-tolerance 1
```

**Check balance:** `balance_of`
```bash
casper-client put-transaction package \
    --node-address $NODE --chain-name $CHAIN \
    --secret-key $KEY \
    --contract-package-hash $PACKAGE \
    --session-entry-point balance_of \
    --session-arg "token_id:u32='0'" \
    --session-arg "owner:address='account-hash-...'" \
    --payment-amount 5000000000 \
    --standard-payment true --gas-price-tolerance 1
```

Check results: `casper-client get-transaction --node-address $NODE <TX_HASH>`

## Decisions Made
- **Python + LangGraph** over Node.js (user preference for LangChain ecosystem)
- **Hosted Casper MCP Server** (no local node or Docker needed)
- **Single tool** `query_casper_blockchain(tool_name, arguments)` instead of 87 individual tools — keeps the prompt clean and the tool list manageable
- **GPT-4o-mini** for cost efficiency + speed
- **LangGraph create_react_agent** (v2) for the agent runtime
- **Streamable HTTP** transport for MCP (stateless, no persistent sessions)

## Known Constraints
- MCP write tools are stdio-only (disabled on hosted endpoint). For on-chain transactions, use the smart contract deployment separately.
- CSPR.cloud API key required (free tier available).

## Troubleshooting Deploy Errors
| Error Code | Discriminant | Meaning | Fix |
|---|---|---|---|
| 64658 (0xFC92) | 122 | `MissingArg` — Odra's `call()` expects named args | Pass `odra_cfg_package_hash_key_name`, `odra_cfg_allow_key_override`, `odra_cfg_is_upgradable`, `odra_cfg_is_upgrade`, plus init args |
| Out of gas | — | Wasm too large (280KB) for default payment | Increase `--payment-amount` (500 CSPR worked for ~231 CSPR consumed) |
| 64641 (0xFC81) | 105 | `CannotOverrideKeys` — package hash key already exists | Set `odra_cfg_allow_key_override:bool='true'` |
| -32602 | — | Invalid state query key format | Use `hash-` prefix for contracts (not `contract-`) in Casper 2.0 |
