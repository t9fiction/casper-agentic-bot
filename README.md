# Casper Agentic Bot

**AI-powered chatbot** for the Casper blockchain — ask questions in plain English, get real on-chain data.

Built for the **Casper Agentic Buildathon 2026** (Qualification Round).

## Demo

```
User:  "What's the current network status?"
Bot:   Calls GetNetworkStatus → returns era, validator count, total stake, etc.

User:  "Show me the latest 3 blocks"
Bot:   Calls GetLatestBlocks → returns block hashes, heights, timestamps, proposers

User:  "Get account info for 01abc..."
Bot:   Calls GetAccountInfo → returns balance, staking, delegation status
```

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python + FastAPI |
| Agent Framework | LangChain (OpenAI tools agent) |
| LLM | GPT-4o-mini |
| Blockchain Data | Casper MCP Server (via CSPR.cloud) |
| MCP Protocol | `mcp` Python SDK |
| Smart Contracts | Odra Framework (Rust) |
| Frontend | HTML + CSS + vanilla JS |

## Quick Start

### 1. Prerequisites
- Python 3.10+
- [OpenAI API key](https://platform.openai.com/api-keys)
- [CSPR.cloud API key](https://cspr.cloud) (free)

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
```

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

### Interact via the Chat UI

Start the server (`uvicorn src.main:app --reload`), open `http://localhost:8000`, and ask questions like:

- *"What entry points does the greeter contract have?"*
- *"Get the current greeting from the deployed contract."*

Write calls (`set_greeting`) are **not available through the chat UI** — the hosted MCP endpoint only exposes read tools. Use the CLI commands above for writes.

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
| Technical Execution | FastAPI + LangChain + MCP integration |
| Innovation & Originality | Natural language → blockchain via AI agent |
| Use of AI / Agentic Systems | GPT-4o-mini autonomously routes tool calls |
| Real-World Applicability | Non-technical users can query on-chain data |
| Working Smart Contracts | Greeter on Testnet |
| Long-Term Launch Plans | Extensible to transfers, DeFi, wallet mgmt |

## Resources
- [Casper AI Toolkit](https://www.casper.network/ai)
- [Casper MCP Server](https://github.com/msanlisavas/casper-mcp)
- [CSPR.cloud](https://cspr.cloud)
- [Odra Framework](https://odra.dev)
