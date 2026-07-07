---
title: Casper Agentic Bot
emoji: 🤖
colorFrom: blue
colorTo: purple
sdk: docker
app_port: 8000
pinned: false
---

# Casper Agentic Bot

**AI-powered chatbot** for the Casper blockchain — ask questions in plain English, send transfers, analyze accounts, and monitor whale activity. Built with LangGraph + GPT-4o-mini.

Built for the **Casper Agentic Buildathon 2026** (Qualification Round).

## Demo

```
User:  "What's the current network status?"
Bot:   Calls GetNetworkStatus → returns era, validator count, total stake, etc.

User:  "Send 5 CSPR to account-hash-2bc76a..."
Bot:   Signs + submits a native transfer via casper-client → returns tx hash

User:  "Analyze account account-hash-2bc76a..."
Bot:   Fetches balance, named keys, and scans recent blocks for activity

User:  "Monitor this whale account for transactions above 1000 CSPR"
Bot:   Adds account to background watcher, polls every 30s, alerts in Monitor tab

User:  "Show me the latest 3 blocks"
Bot:   Calls GetLatestBlocks → returns block hashes, heights, timestamps, proposers

User:  "Get account info for 01abc..."
Bot:   Calls GetAccountInfo → returns balance, staking, delegation status
```

## Features

| Feature | Description |
|---|---|
| **Blockchain Queries** | 87+ MCP tools for on-chain data (blocks, accounts, validators, contracts, NFTs, DeFi) |
| **CSPR Transfers** | Agent signs and submits native CSPR transfers using the server's secret key |
| **Account Analysis** | Detailed account info with recent transaction scanning |
| **Whale Monitoring** | Background watcher that polls accounts every 30s and displays alerts in the Monitor tab |
| **Smart Contract Interaction** | Deployed Greeter contract on Testnet — read/write entry points via CLI |

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python + FastAPI |
| Agent Framework | LangChain + LangGraph (create_react_agent) |
| LLM | GPT-4o-mini |
| Blockchain Data | Casper MCP Server (via CSPR.cloud) |
| MCP Protocol | `mcp` Python SDK (Streamable HTTP) |
| Smart Contracts | Odra Framework (Rust) |
| Frontend | HTML + CSS + vanilla JS |

## Quick Start

### 1. Prerequisites
- Python 3.10+
- [OpenAI API key](https://platform.openai.com/api-keys)
- [CSPR.cloud API key](https://cspr.cloud) (free)
- [Casper CLI client](https://docs.casper.network/developers/cli/setup/) (for transfers)
- A funded Testnet account with a PEM secret key (for transfers)

### 2. Setup

```bash
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
CASPER_NETWORK=testnet
SECRET_KEY_PATH=secret_key.pem
CASPER_NODE=http://65.109.115.124:7777
```

Place your PEM secret key at `secret_key.pem` in the project root.

### 3. Run

```bash
uvicorn src.main:app --reload
```

Open **http://localhost:8000**.

## Smart Contract (Testnet)

A **Greeter** contract built with Odra is deployed on Casper Testnet. It stores a greeting string and exposes entry points to read, write, and interact with it.

### Deployed Addresses

| Field | Value |
|---|---|
| Contract Package Hash | `contract-package-ac102e24f6dc92e7e3b098f2af114817a67b62fe35764813854057a0859571f4` |
| Contract Hash (v1) | `contract-e294029ed8d748f31ab36690e6f68bc777cef9094cfbb0a91fd8c3c41745ba72` |
| Account | `account-hash-2bc76a5348a847ff51738945d681b97dda6ed606f7ae4282d1a0eb409ef301f5` |
| Node | `65.109.115.124:7777` |

### Entry Points

| Name | Args | Returns | Description |
|---|---|---|---|
| `get_greeting` | none | `String` | Read the current greeting |
| `set_greeting` | `greeting: String` | `Unit` | Write a new greeting |
| `greet` | none | `String` | Returns "Hello, {greeting}!" + increments counter |
| `get_greet_count` | none | `U32` | Number of times `greet()` was called |

### Interact (read/write) via CLI

**Prerequisite:** Install the [Casper CLI client](https://docs.casper.network/developers/cli/setup/).

Set these once (paste into your terminal):

```bash
export NODE=http://65.109.115.124:7777
export CHAIN=casper-test
export PACKAGE=hash-ac102e24f6dc92e7e3b098f2af114817a67b62fe35764813854057a0859571f4
export KEY=/path/to/your/secret_key.pem
```

#### Read — get the greeting

```bash
casper-client put-transaction package \
    --node-address $NODE --chain-name $CHAIN \
    --secret-key $KEY \
    --contract-package-hash $PACKAGE \
    --session-entry-point get_greeting \
    --payment-amount 5000000000 \
    --standard-payment true --gas-price-tolerance 1
```

Save the `transaction_hash` from the output, then check the result:

```bash
casper-client get-transaction --node-address $NODE <TX_HASH>
```

Look for `"error_message": null` — that means success.

#### Write — set a new greeting

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

#### Greet — get a personalized message + increment counter

```bash
casper-client put-transaction package \
    --node-address $NODE --chain-name $CHAIN \
    --secret-key $KEY \
    --contract-package-hash $PACKAGE \
    --session-entry-point greet \
    --payment-amount 5000000000 \
    --standard-payment true --gas-price-tolerance 1
```

#### Verify the greeting was updated

Call `get_greeting` again (first command) to confirm the new greeting is stored.

## Chat UI

Open `http://localhost:8000` and use natural language:

| You say | What happens |
|---|---|
| *"What's the network status?"* | Agent calls MCP `GetNetworkStatus` |
| *"Send 5 CSPR to account-hash-2bc76a..."* | Agent signs + submits a native transfer |
| *"Analyze account account-hash-..."* | Agent fetches balance, info, and recent activity |
| *"Monitor account-hash-... for transactions > 100 CSPR"* | Background watcher starts, alerts in Monitor tab |
| *"What entry points does the greeter contract have?"* | Agent queries the deployed contract |

### Chat Tab
Type or click suggestion chips. The agent autonomously decides which tool to call.

### Monitor Tab
Switch to the **Monitor** tab to:
- Add accounts to watch (with optional label and minimum CSPR threshold)
- View live alerts from the background watcher (polls every 30s)
- Remove monitored accounts

> **Note:** Write calls to the Greeter contract (`set_greeting`) are CLI-only. The hosted MCP endpoint exposes read tools only.

## Source Code

The smart contract source is in `smart-contract/src/greeter.rs` (Odra Rust). Build locally:

```bash
cd smart-contract
cargo odra build
cargo odra deploy --network testnet
```

## Hackathon Submission Checklist

- [x] Working prototype querying Casper Testnet
- [x] On-chain component (Greeter contract on Testnet)
- [x] Open-source GitHub repo with README
- [x] Deploy smart contract to Testnet
- [x] Push to GitHub
- [ ] Demo video (record UI walkthrough + code)

### Judging Criteria Alignment

| Criterion | How We Hit It |
|---|---|
| Technical Execution | FastAPI + LangGraph + MCP + background monitor worker |
| Innovation & Originality | Natural language → blockchain via AI agent that transacts |
| Use of AI / Agentic Systems | GPT-4o-mini autonomously routes tool calls, signs transfers, analyzes accounts |
| Real-World Applicability | Send CSPR, analyze whale wallets, monitor accounts — practical DeFi use |
| Working Smart Contracts | Greeter contract deployed on Testnet with verified entry points |
| Long-Term Launch Plans | Extensible to DeFi protocols, staking automation, multi-agent systems |

## Resources
- [Casper AI Toolkit](https://www.casper.network/ai)
- [Casper MCP Server](https://github.com/msanlisavas/casper-mcp)
- [CSPR.cloud](https://cspr.cloud)
- [Odra Framework](https://odra.dev)
