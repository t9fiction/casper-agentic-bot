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

## Current State
- [x] Project scaffolding (Python + FastAPI + LangChain)
- [x] FastAPI server with /api/chat endpoint
- [x] LangGraph agent with MCP tool routing
- [x] Python MCP client (streamable_http → mcp.testnet.cspr.cloud)
- [x] Web chat UI
- [x] Smart contract code (Odra Greeter) + wasm binary builds
- [x] .env configured with API keys
- [x] langgraph in requirements.txt
- [x] secret_key.pem + target/ gitignored
- [x] Pushed to GitHub (github.com/t9fiction/casper-agentic-bot)
- [ ] Deploy smart contract to Casper Testnet
- [ ] Record demo video
- [ ] Submit on DoraHacks

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
