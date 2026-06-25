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

A **Greeter** contract built with Odra lives in `smart-contract/`. Deploy:

```bash
cd smart-contract
cargo odra build
cargo odra deploy --network testnet
```

## Hackathon Submission Checklist

- [x] Working prototype querying Casper Testnet
- [x] On-chain component (Greeter contract)
- [x] Open-source GitHub repo with README
- [ ] Demo video (record UI walkthrough + code)
- [ ] Deploy smart contract to Testnet
- [ ] Push to GitHub

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
