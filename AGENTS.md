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
| `src/tools.py` | LangChain tool: query_casper_blockchain (wraps MCP call_tool) |
| `src/mcp_client.py` | Async MCP client (streamable_http to hosted MCP) |
| `src/public/index.html` | Dark-themed chat UI |
| `smart-contract/src/greeter.rs` | Odra Greeter contract module |
| `smart-contract/src/lib.rs` | Crate root (no_std, extern alloc, pub mod greeter) |
| `smart-contract/Odra.toml` | Contract definition (greeter::Greeter) |
| `smart-contract/bin/build_contract.rs` | Wasm build binary target |
| `smart-contract/build.rs` | Odra build script |
| `smart-contract/.cargo/config.toml` | Wasm target-cpu + allow-undefined linker flag |
| `smart-contract/rust-toolchain` | Nightly toolchain pin |
| `AGENTS.md` | This file — project context for resume support |
| `src/transfers.py` | CSPR transfer tool (subprocess to casper-client) |
| `src/account_analyzer.py` | Account analysis (biggest tx, details) |
| `src/monitor.py` | Background account monitor (30s poll loop) |

## Current State
- [x] Project scaffolding (Python + FastAPI + LangChain)
- [x] FastAPI server with /api/chat endpoint
- [x] LangGraph agent with MCP tool routing
- [x] Python MCP client (streamable_http → mcp.testnet.cspr.cloud)
- [x] Web chat UI (chat + monitor tabs)
- [x] Smart contract code (Odra Greeter) + wasm binary builds
- [x] .env configured with API keys
- [x] langgraph in requirements.txt
- [x] secret_key.pem + target/ gitignored
- [x] Pushed to GitHub (github.com/t9fiction/casper-agentic-bot)
- [x] Deploy smart contract to Casper Testnet 🎉
- [x] CSPR transfer tool (agent signs + submits transactions)
- [x] Account analysis tool (account details, biggest tx scanning)
- [x] Account monitoring feature (background watcher, alerts via UI)
- [ ] Record demo video
- [ ] Submit on DoraHacks

## Deployed Contract (Casper Testnet)
| Field | Value |
|---|---|
| Network | Casper Testnet (casper-test) |
| Deploy method | `put-transaction session` with `--install-upgrade` |
| Contract Package Hash | `contract-package-ac102e24f6dc92e7e3b098f2af114817a67b62fe35764813854057a0859571f4` |
| Contract Hash | `contract-e294029ed8d748f31ab36690e6f68bc777cef9094cfbb0a91fd8c3c41745ba72` |
| Account Hash | `account-hash-2bc76a5348a847ff51738945d681b97dda6ed606f7ae4282d1a0eb409ef301f5` |
| Node | `65.109.115.124:7777` |
| Block Height | 8305683 |
| Deploy Cost | ~231 CSPR (limit 500 CSPR) |
| Entry Points | `init`, `get_greeting`, `set_greeting`, `greet`, `get_greet_count` |

### Deploy Notes
- Used `put-transaction session` (not deprecated `put-deploy`)
- Required args: `odra_cfg_package_hash_key_name`, `odra_cfg_allow_key_override`, `odra_cfg_is_upgradable`, `odra_cfg_is_upgrade`, and init args
- 500 CSPR payment was needed — the 280KB wasm consumed ~231 CSPR
- `put-deploy` was deprecated; `put-transaction` with `--install-upgrade` flag is the correct Casper 2.0 approach

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
    -q "greeter"

# Query contract entity to see entry points
casper-client query-global-state \
    --node-address http://65.109.115.124:7777 \
    --key hash-e294029ed8d748f31ab36690e6f68bc777cef9094cfbb0a91fd8c3c41745ba72
```

## How to Call Entry Points (Read & Write)

Set env vars:
```bash
export NODE=http://65.109.115.124:7777
export CHAIN=casper-test
export PACKAGE=hash-ac102e24f6dc92e7e3b098f2af114817a67b62fe35764813854057a0859571f4
export KEY=secret_key.pem
```

**Read:** `get_greeting` — submits a tx, then check `"error_message": null`
```bash
casper-client put-transaction package \
    --node-address $NODE --chain-name $CHAIN \
    --secret-key $KEY \
    --contract-package-hash $PACKAGE \
    --session-entry-point get_greeting \
    --payment-amount 5000000000 \
    --standard-payment true --gas-price-tolerance 1
```

**Write:** `set_greeting` — pass the new greeting as a session arg
```bash
casper-client put-transaction package \
    --node-address $NODE --chain-name $CHAIN \
    --secret-key $KEY \
    --contract-package-hash $PACKAGE \
    --session-entry-point set_greeting \
    --session-arg "greeting:string='GM Casper!'" \
    --payment-amount 5000000000 \
    --standard-payment true --gas-price-tolerance 1
```

**Call:** `greet` — returns "Hello, {greeting}!" and increments counter
```bash
casper-client put-transaction package \
    --node-address $NODE --chain-name $CHAIN \
    --secret-key $KEY \
    --contract-package-hash $PACKAGE \
    --session-entry-point greet \
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
