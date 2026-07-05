# Casper Agentic Bot — Setup & Running Guide

## Quick Start (5 minutes)

```bash
# 1. Clone and enter directory
cd casper-agentic-bot

# 2. Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your API keys (see below)

# 5. Run the server
uvicorn src.main:app --reload

# 6. Open browser
# Chat: http://localhost:8000
# Portfolio: http://localhost:8000/portfolio
```

---

## Prerequisites

### Required (Must Have)
- **Python 3.10+** (check: `python3 --version`)
- **OpenAI API Key** (get from: https://platform.openai.com/api-keys)
- **CSPR.cloud API Key** (get from: https://cspr.cloud)

### Optional (For Transfers)
- **Casper CLI client** (for sending CSPR transfers)
- **Secret key in PEM format** (.pem file or env var content)
- **Funded Testnet account** (to pay for transactions)

---

## Step 1: Clone the Repository

```bash
git clone https://github.com/t9fiction/casper-agentic-bot.git
cd casper-agentic-bot
```

---

## Step 2: Set Up Python Virtual Environment

### macOS / Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Windows
```bash
python -m venv .venv
.venv\Scripts\activate
```

### Verify activation
```bash
which python  # Should show path in .venv/
# or
where python  # On Windows
```

---

## Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

**What gets installed:**
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `langchain` + `langgraph` - AI agent framework
- `langchain-openai` - OpenAI integration
- `mcp` - Model Context Protocol client
- `python-dotenv` - Load .env files
- `httpx` - HTTP client for MCP

**Installation time:** ~2-3 minutes

---

## Step 4: Configure Environment Variables

### A. Copy example file
```bash
cp .env.example .env
```

### B. Edit `.env` with your credentials

```env
# REQUIRED - OpenAI API
OPENAI_API_KEY=sk-proj-YOUR_ACTUAL_KEY_HERE

# REQUIRED - Casper blockchain data
CSPR_CLOUD_API_KEY=YOUR_ACTUAL_KEY_HERE

# RECOMMENDED - Network config (don't change)
CASPER_NETWORK=casper-test
CASPER_NODE=http://65.109.115.124:7777
CONTRACT_PACKAGE_HASH=hash-5095fbfcbfa662ef13731dd0822317e100f2642230c2a35f0241e888eb8383eb

# OPTIONAL - For CSPR transfers (leave blank if not using)
SECRET_KEY="-----BEGIN EC PRIVATE KEY-----\nMHQCAQEE...\n-----END EC PRIVATE KEY-----"
WALLET_ACCOUNT_HASH=account-hash-2bc76a5348a847ff51738945d681b97dda6ed606f7ae4282d1a0eb409ef301f5
CONTRACT_HASH=contract-c3b50a15995f97f424b8e4541499d03a80e0f2ba7b528edb07c9712e7dcc3354
```

### Get Your API Keys

#### OpenAI API Key
1. Go to https://platform.openai.com/api-keys
2. Click "Create new secret key"
3. Copy the key starting with `sk-proj-`
4. Paste into `.env` as `OPENAI_API_KEY`

#### CSPR.cloud API Key
1. Go to https://cspr.cloud
2. Sign up or log in
3. Navigate to API keys
4. Copy your API key
5. Paste into `.env` as `CSPR_CLOUD_API_KEY`

#### Secret Key (Optional - for transfers only)
If you want to send CSPR transfers:
1. Export your Casper testnet secret key in PEM format
2. Open the file and copy the content (including BEGIN/END lines)
3. In `.env`, set `SECRET_KEY` to the content (replace newlines with `\n`)

**Example:**
```env
SECRET_KEY="-----BEGIN EC PRIVATE KEY-----\nMHQCAQEE...\n-----END EC PRIVATE KEY-----"
```

---

## Step 5: Run the Application

### Local Development (Recommended)

```bash
uvicorn src.main:app --reload
```

**Output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

**Features:**
- Auto-reloads on code changes
- Debug mode enabled
- Access logs printed

### Production Mode

```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

### With Custom Port

```bash
uvicorn src.main:app --port 3000 --reload
```

---

## Step 6: Open the Web Interface

### Chat Page
- **URL**: http://localhost:8000
- **Features**:
  - Natural language chatbot for blockchain queries
  - Suggestion chips for common operations
  - Modal forms for token/NFT operations
  - Wallet connection

### Portfolio Page
- **URL**: http://localhost:8000/portfolio
- **Features**:
  - View CSPR balance
  - Track deployed tokens
  - Monitor NFTs owned
  - View collections created
  - Refresh button to reload data

---

## Testing the Application

### Test 1: Simple Chat
1. Open http://localhost:8000
2. Type: "What is the current Casper network status?"
3. Click Send
4. Agent should respond with network data

### Test 2: Modal Form - Deploy Token
1. Click suggestion chip "🪙 Deploy Token"
2. Fill form:
   - Token Name: `MyTestToken`
   - Symbol: `MTT`
   - Decimals: `8`
   - Total Supply: `1000000`
3. Click "Deploy Token"
4. Agent submits deployment to testnet

### Test 3: Modal Form - Check Balance
1. Click "💰 Check Balance"
2. Fill form:
   - Token ID: `0`
   - Account Hash: (your account hash)
3. Click "Check Balance"
4. Agent queries token balance

### Test 4: NFT Marketplace
1. Click "🖼️ NFT Marketplace"
2. Try each tab:
   - **Mint**: Enter metadata URI + recipient → Mint
   - **List**: Enter token ID + price → List for sale
   - **Buy**: Enter token ID + buyer → Buy NFT

### Test 5: Portfolio
1. Click "📊 Portfolio" in suggestions
2. Connect wallet (if prompted)
3. View deployed tokens, NFTs, collections
4. Click "📋 Copy ID" buttons to copy IDs

### Test 6: Error Validation
1. Try to submit a form without filling fields
2. Should see red error: "Please fill in all fields"
3. Enter invalid account hash format
4. Should see error: "Invalid account hash format"

---

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'fastapi'"
**Solution**: Ensure virtual environment is activated
```bash
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate      # Windows
pip install -r requirements.txt
```

### Issue: "openai.error.AuthenticationError"
**Solution**: Check OPENAI_API_KEY in .env
```bash
# Verify your key starts with sk-proj-
grep OPENAI_API_KEY .env
```

### Issue: "ConnectionError: Failed to connect to MCP server"
**Solution**: Check internet connection and CSPR.cloud API key
```bash
# Verify API key is correct
grep CSPR_CLOUD_API_KEY .env

# Check MCP endpoint is reachable
curl https://mcp.testnet.cspr.cloud/health
```

### Issue: "Agent times out or doesn't respond"
**Solution**:
- Check OpenAI API key is valid and has credits
- Check CSPR.cloud API key is valid
- Check internet connection
- Try simpler query: "Hello" or "What's the network status?"

### Issue: "Modal forms not appearing"
**Solution**: Clear browser cache and reload (Ctrl+Shift+Delete)

### Issue: "Portfolio page shows 'Wallet not connected'"
**Solution**:
- Install Casper Wallet extension
- Connect wallet in header
- Refresh page

---

## Docker Setup (Alternative)

### Build Docker image
```bash
docker compose build
```

### Run with Docker
```bash
docker compose up -d
```

**Access:**
- Chat: http://localhost:8000
- Portfolio: http://localhost:8000/portfolio

### Stop Docker
```bash
docker compose down
```

**Note:** Docker build includes casper-client, takes ~10 minutes

---

## Run Integration Tests

```bash
# Activate virtual environment
source .venv/bin/activate

# Run all tests
python -m pytest tests/test_integration.py -v

# Run specific test
python -m pytest tests/test_integration.py::TestMCPClient::test_list_tools -v

# Run with async mode
python -m pytest tests/test_integration.py -v --asyncio-mode=auto
```

**Expected output:**
```
tests/test_integration.py::TestImports::test_import_agent PASSED
tests/test_integration.py::TestImports::test_import_tools PASSED
tests/test_integration.py::TestMCPClient::test_list_tools PASSED
...
====== 12 passed in 2.5s ======
```

---

## Project Structure

```
casper-agentic-bot/
├── src/
│   ├── main.py              # FastAPI server
│   ├── agent.py             # LangGraph AI agent
│   ├── tools.py             # Blockchain tools
│   ├── mcp_client.py        # MCP client
│   ├── account_analyzer.py  # Account queries
│   ├── contract_registry.py # Contract tracking
│   ├── portfolio_cache.py   # Token/NFT cache
│   └── public/
│       ├── index.html       # Chat UI (1304 lines)
│       └── portfolio.html   # Portfolio UI (835 lines)
├── smart-contract/
│   ├── src/
│   │   ├── token_factory.rs    # Token Factory contract
│   │   ├── nft_marketplace.rs  # NFT Marketplace contract
│   │   └── collection_factory.rs # Collection Factory contract
│   ├── wasm/
│   │   ├── TokenFactory.wasm
│   │   ├── NftMarketplace.wasm
│   │   └── CollectionFactory.wasm
│   └── Odra.toml
├── tests/
│   └── test_integration.py  # 12 integration tests
├── .env.example
├── .env                     # YOUR KEYS HERE
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── README.md
├── AGENTS.md
├── SETUP.md                 # THIS FILE
├── portfolio_cache.json     # Auto-generated
└── contracts_registry.json  # Auto-generated
```

---

## Features Overview

### Chat Page Features
- ✅ Natural language blockchain queries
- ✅ 12+ suggestion chips (grouped by category)
- ✅ Hero section with animated robot
- ✅ Real-time message streaming
- ✅ Code/markdown formatting
- ✅ Wallet connection
- ✅ **NEW: Modal forms for:**
  - Token deployment
  - Token transfers
  - Balance checking
  - NFT minting/listing/buying
  - Collection creation

### Portfolio Page Features
- ✅ CSPR balance display
- ✅ Token Factory tokens list
- ✅ NFT ownership tracking
- ✅ Collection information
- ✅ Recent activity timeline
- ✅ Wallet address display
- ✅ **NEW: Enhanced with:**
  - Token IDs
  - NFT listing status
  - Copy-to-clipboard buttons

### Smart Contracts (Deployed on Testnet)
- ✅ **Token Factory**: Deploy custom tokens, transfer, check balances
- ✅ **NFT Marketplace**: Mint NFTs, list/buy, manage ownership
- ✅ **Collection Factory**: Create collections, mint from collections, pagination

---

## API Endpoints

### Chat Endpoint
```
POST /api/chat
Content-Type: application/json

{
  "message": "Deploy a token called MyToken with symbol MTK, 8 decimals, 1000000 supply"
}

Response:
{
  "reply": "I'll deploy the token for you...",
  "error": null
}
```

### Portfolio Endpoint
```
GET /api/portfolio?public_key=02abc...

Response:
{
  "wallet": "account-hash-...",
  "cspr_balance": "100.5",
  "tokens": [...],
  "nfts": [...],
  "collections": [...]
}
```

---

## Development Tips

### Add New Modal Form
1. Create HTML modal in `src/public/index.html`
2. Add CSS styling (use existing `.modal` classes)
3. Add JavaScript function `submitFormName(event)`
4. Add suggestion chip that calls `openModal('formNameModal')`

### Add New Agent Tool
1. Create function in `src/tools.py` with `@tool` decorator
2. Register in `src/agent.py` tools list
3. Add to system prompt with description

### Debug Agent Responses
1. Check `src/agent.py` system prompt
2. Add print statements to tool functions
3. Check `.env` configuration
4. Review LangChain/LangGraph logs

---

## Deployment

### Free Cloud Hosting Options

#### Option 1: Koyeb (Recommended)
```bash
# 1. Sign up: https://koyeb.com
# 2. Connect GitHub repo
# 3. Set build command: pip install -r requirements.txt
# 4. Set run command: uvicorn src.main:app --host 0.0.0.0 --port 8000
# 5. Add environment variables (.env values)
# 6. Deploy
```

#### Option 2: Railway
```bash
# 1. Sign up: https://railway.app
# 2. Connect GitHub
# 3. Set environment variables
# 4. Deploy
```

#### Option 3: Fly.io
```bash
# 1. Install flyctl
# 2. Run: fly launch
# 3. Set secrets: fly secrets set OPENAI_API_KEY=...
# 4. Deploy: fly deploy
```

---

## Next Steps

1. **Test locally**: Run through all test cases above
2. **Connect wallet**: Install Casper Wallet extension
3. **Deploy contract**: Use chat to deploy test tokens/NFTs
4. **View portfolio**: Check portfolio page for created assets
5. **Deploy to cloud**: Use one of the options above
6. **Record demo video**: Show UI walkthrough
7. **Submit to hackathon**: https://dorahacks.io

---

## Support & Troubleshooting

### Common Issues

| Issue | Solution |
|---|---|
| Port 8000 already in use | `uvicorn src.main:app --port 3000` |
| Virtual env not activating | Use full path: `source /full/path/.venv/bin/activate` |
| OpenAI API rate limit | Wait 60 seconds before retrying |
| Wallet not connecting | Ensure Casper Wallet extension is installed |
| Modal not showing | Clear cache: Ctrl+Shift+Delete |
| Forms not validating | Check browser console for errors (F12) |

### Get Help

1. **Check logs**: Look at server output for error messages
2. **Browser console**: Press F12 → Console tab for client errors
3. **GitHub issues**: https://github.com/t9fiction/casper-agentic-bot/issues
4. **Casper docs**: https://docs.casper.network

---

## File Sizes & Performance

- **index.html**: 1304 lines (~50 KB)
- **portfolio.html**: 835 lines (~35 KB)
- **Total frontend**: ~85 KB (minified would be ~30 KB)
- **Python backend**: ~8 files, ~800 lines
- **Smart contracts**: 3 wasm files (~850 KB total)
- **Page load time**: <500ms (Chat), <1s (Portfolio)
- **Modal open time**: <200ms (smooth animation)

---

## License & Attribution

Built for **Casper Agentic Buildathon 2026** 🚀

- **Frontend**: HTML5 + Vanilla JS + CSS3
- **Backend**: Python + FastAPI + LangGraph
- **Blockchain**: Casper Network + Odra Framework
- **AI**: OpenAI GPT-4o-mini

---

**Happy coding! 🎉 Start the server and explore the blockchain through natural language!**
