# Casper Agentic Bot

**AI-powered chatbot** for the Casper blockchain — deploy tokens, mint NFTs, create collections, and query the chain using natural language. Built with LangGraph + GPT-4o-mini.

Built for the **Casper Agentic Buildathon 2026**.

## Demo

```
User: "Deploy a token called MyCoin with symbol MYC, 8 decimals, 1M supply"
Bot:  Calls deploy_token → returns token ID and tx hash

User: "Mint an NFT with metadata URI https://example.com/nft.json to my wallet"
Bot:  Calls mint_nft → returns token ID and tx hash

User: "Create a collection called Art with symbol ART and mint price 10 CSPR"
Bot:  Calls create_collection → returns collection ID

User: "What's the network status?"
Bot:  Calls get_network_status → returns era, validator count, total stake

User: "Send 5 CSPR to account-hash-2bc76a..."
Bot:  Signs + submits a native transfer via casper-client

User: "Analyze account account-hash-2bc76a..."
Bot:  Fetches balance, named keys, and scans recent blocks for largest txs
```

## Features

| Feature | Description |
|---|---|
| **Token Creation** | Deploy custom tokens with name, symbol, decimals, total supply via chat or modal form |
| **Token Transfers** | Transfer tokens between wallets, check balances |
| **NFT Minting** | Mint NFTs with metadata URIs, transfer, list for sale, buy listed NFTs |
| **Collection Factory** | Create NFT collections with configurable mint prices |
| **Blockchain Queries** | 87+ MCP tools for on-chain data (blocks, accounts, validators, contracts) |
| **CSPR Transfers** | Agent signs and submits native CSPR transfers |
| **Account Analysis** | Detailed account info with recent transaction scanning |
| **Portfolio Dashboard** | Web dashboard showing all created tokens, NFTs, and collections |
| **Multi-Contract Tracking** | Deploy and track multiple contract instances by name |
| **Multi-Step Workflows** | Agent chains multiple operations (deploy → transfer → verify) autonomously |

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python + FastAPI |
| Agent Framework | LangChain + LangGraph (create_react_agent) |
| LLM | GPT-4o-mini |
| Blockchain Data | Casper MCP Server (via CSPR.cloud) |
| MCP Protocol | `mcp` Python SDK (Streamable HTTP) |
| Smart Contracts | Odra Framework (Rust) |
| Frontend | HTML + CSS + vanilla JS (chat + modals + portfolio) |

## Quick Start

### Prerequisites
- Python 3.10+
- [OpenAI API key](https://platform.openai.com/api-keys)
- [CSPR.cloud API key](https://cspr.cloud) (free)
- A funded Testnet account with a PEM secret key

### Setup

```bash
git clone https://github.com/t9fiction/casper-agentic-bot
cd casper-agentic-bot
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env`:
```
OPENAI_API_KEY=sk-...
CSPR_CLOUD_API_KEY=your-key
CASPER_NETWORK=casper-test
SECRET_KEY="-----BEGIN EC PRIVATE KEY-----\n..."
CASPER_NODE=http://65.109.115.124:7777
CONTRACT_PACKAGE_HASH=hash-5095fbfcbfa662ef13731dd0822317e100f2642230c2a35f0241e888eb8383eb
CONTRACT_HASH=contract-c3b50a15995f97f424b8e4541499d03a80e0f2ba7b528edb07c9712e7dcc3354
WALLET_ACCOUNT_HASH=account-hash-2bc76a5348a847ff51738945d681b97dda6ed606f7ae4282d1a0eb409ef301f5
```

### Run

```bash
uvicorn src.main:app --reload
```

Open **http://localhost:8000**.

### Docker

```bash
docker compose up -d
# Open http://localhost:8000
```

## Smart Contracts (Casper Testnet)

### Token Factory
| Entry Point | Args | Returns |
|---|---|---|
| `deploy_token` | name, symbol, decimals (U8), total_supply (U256) | U32 (token_id) |
| `transfer` | token_id (U32), recipient (Key), amount (U256) | — |
| `balance_of` | token_id (U32), owner (Key) | U256 |
| `mint` | token_id (U32), recipient (Key), amount (U256) | — |
| `token_info` | token_id (U32) | Option\<TokenInfo\> |
| `total_tokens` | — | U32 |

### NFT Marketplace
| Entry Point | Args | Returns |
|---|---|---|
| `mint_nft` | metadata_uri (String), recipient (Key) | U64 (token_id) |
| `transfer_nft` | token_id (U64), recipient (Key) | — |
| `list_nft` | token_id (U64), price (U256) | — |
| `buy_nft` | token_id (U64), buyer (Key) | — |
| `nft_info` | token_id (U64) | Option\<NftInfo\> |
| `total_nfts` | — | U64 |

### Collection Factory
| Entry Point | Args | Returns |
|---|---|---|
| `create_collection` | name, symbol, base_uri, mint_price (U256) | U32 (collection_id) |
| `mint_nft` | collection_id (U32), recipient (Key) | U64 |
| `list_nft` | token_id (U64), price (U256) | — |
| `buy_nft` | token_id (U64), buyer (Key) | — |

### Deployed Addresses

| Contract | Package Hash | Contract Hash |
|---|---|---|
| Token Factory | `hash-5095fbfcbfa662ef13731dd0822317e100f2642230c2a35f0241e888eb8383eb` | `contract-c3b50a15995f97f424b8e4541499d03a80e0f2ba7b528edb07c9712e7dcc3354` |
| NFT Marketplace | `hash-0c5849200ac2d72291b5bd811024396bb4954e82b8e155105c4ee7b0cedcb896` | `contract-2168fc559eff8ed6d521f4b67ac297181547e1fcbe845b215aeda228218bd738` |

## Chat UI

Open `http://localhost:8000` and use natural language or click suggestion chips to open modal forms:

| You say | What happens |
|---|---|
| *"Deploy a token called MyCoin with symbol MYC, 8 decimals, 1M supply"* | Agent calls `deploy_token` |
| *"Mint an NFT with URI https://..."* | Agent calls `mint_nft` |
| *"Create a collection called Art with mint price 10"* | Agent calls `create_collection` |
| *"What's the network status?"* | Agent calls `get_network_status` |
| *"Send 5 CSPR to account-hash-..."* | Agent signs + submits native transfer |
| *"Analyze account account-hash-..."* | Agent fetches balance and activity |

### Modals
- **Deploy Token** — fillable form for name, symbol, decimals, supply
- **Transfer Token** — form for token ID, recipient, amount
- **Balance Check** — form for token ID + account
- **NFT Marketplace** — 3-tab interface (Mint / List / Buy)
- **Collection Creator** — form for name, symbol, base URI, mint price

### Portfolio Dashboard
Open `http://localhost:8000/portfolio` to see all created tokens, minted NFTs, and collections. Connect your Casper wallet to view your portfolio.

## Docker Setup

```bash
docker compose build   # ~10 min (compiles casper-client from source)
docker compose up -d   # runs on port 8000
```

Multi-stage build: Stage 1 compiles `casper-client` 5.0.1 with nightly Rust, Stage 2 runs Python 3.13-slim.

## Test

```bash
source .venv/bin/activate
python -m pytest tests/test_integration.py -v --asyncio-mode=auto
```

## Source Code

Smart contracts in `smart-contract/src/`:
- `token_factory.rs` — Token Factory (Token Faucet standard)
- `nft_marketplace.rs` — NFT Marketplace
- `collection_factory.rs` — Collection Factory

Build locally:
```bash
cd smart-contract
cargo odra build
```

Backend in `src/`:
- `main.py` — FastAPI server
- `agent.py` — LangGraph ReAct agent
- `tools.py` — LangChain tools (deploy, transfer, mint, query, analyze)
- `mcp_client.py` — MCP client (Streamable HTTP)
- `portfolio_cache.py` — JSON-backed portfolio cache
- `contract_registry.py` — JSON-backed contract instance registry

## Hackathon Submission

- [x] Working prototype querying Casper Testnet
- [x] Token Factory deployed on Testnet (3 entry points)
- [x] NFT Marketplace deployed on Testnet
- [x] Collection Factory deployed on Testnet
- [x] Open-source GitHub repo with README
- [x] Docker image (reproducible build)
- [x] Frontend UI with modals and portfolio dashboard
- [ ] Demo video
- [ ] Deploy to free cloud

## Links
- [GitHub](https://github.com/t9fiction/casper-agentic-bot)
- [Casper AI Toolkit](https://www.casper.network/ai)
- [Casper MCP Server](https://github.com/msanlisavas/casper-mcp)
- [CSPR.cloud](https://cspr.cloud)
- [Odra Framework](https://odra.dev)
