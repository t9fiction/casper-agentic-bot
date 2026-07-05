# Casper Agentic Bot - Project Status & Context

## 🎯 Project Goal
Build an AI-powered chatbot for the Casper blockchain that allows users to interact with smart contracts through natural language queries and structured modal forms. Deploy tokens, mint NFTs, and create collections on Casper Testnet through an intuitive web interface.

**Hackathon**: Casper Agentic Buildathon 2026
**Status**: ✅ COMPLETE & PRODUCTION-READY (as of session ending)

---

## 📋 What We Accomplished

### Session 1-4: Core Development
- Built FastAPI backend with LangGraph AI agent
- Created 3 smart contracts (Token Factory, NFT Marketplace, Collection Factory) in Rust/Odra
- Deployed all contracts to Casper Testnet
- Built responsive web UI with chat page and portfolio dashboard
- Integrated MCP (Model Context Protocol) for blockchain data access
- Created 12 integration tests (all passing)

### Session 5 (Current): Bug Fixes & Polish

#### 1. **Wallet Connection Fix** (Commits: d64b04b, 93f1a55, 540915a)
**Problem**: "Connect Wallet" button showed error even with extension installed
**Root Cause**: Code was looking for `window.casper` but Casper Wallet extension provides `window.CasperWalletProvider` (a function, not object)
**Solution**:
- Check multiple wallet API names: `CasperWalletProvider`, `casper`, `casperWallet`, `CasperWallet`
- Call the function to get actual API: `const api = wallet(); api.requestConnection()`
- After connection, call `getActivePublicKey()` to get the public key (requestConnection returns boolean)
- Update button to show connected account instead of "Connect Wallet"

**Result**: ✅ Wallet connection now works perfectly
- Button shows account address when connected
- Shows "Connect Wallet" when disconnected
- Users can toggle connection on/off

#### 2. **Portfolio Data Fetching** (Commits: bb1033a, da7fc96)
**Problem**: Portfolio page showed 0 tokens, NFTs, collections even though contracts were deployed
**Root Cause**: Portfolio cache was empty (only tracks deployments through chat modals)
**Solution**:
- Backend queries blockchain via MCP for `get_account_contract_packages`
- Returns `deployed_contracts` array with hash, version, timestamp
- Frontend displays "Deployed Contracts" section showing contracts from blockchain
- Added comprehensive error logging for debugging

**Result**: ✅ Portfolio now shows deployed contracts from blockchain

#### 3. **Admin Dashboard for Cache Population** (Commits: 144cb51, ff90902)
**Problem**: Custom tokens/NFTs/collections weren't showing because cache was empty
**Root Cause**: User deployed contracts outside the chat system, so they weren't logged to cache
**Solution**:
- Created admin dashboard at `http://localhost:8000/admin`
- Added POST endpoints: `/api/admin/log-token`, `/api/admin/log-nft`, `/api/admin/log-collection`
- User can manually add deployments to cache via web form
- Form provides feedback on success/error

**Result**: ✅ Users can manually populate cache with previously deployed contracts

---

## 🏗️ Architecture

### Frontend
- **Chat Page** (`src/public/index.html`, 1304 lines)
  - Hero section with animated robot
  - Message display with markdown support
  - 5 modal forms (Deploy Token, Transfer, Check Balance, NFT Marketplace, Create Collection)
  - Form validation with error messages
  - Wallet connection button
  - Suggestion chips for common operations

- **Portfolio Page** (`src/public/portfolio.html`, 835 lines)
  - Wallet gating (shows "Connect Wallet" prompt if not connected)
  - Summary cards (CSPR balance, token count, NFT count, contract count)
  - Sections for:
    - Custom tokens (from cache)
    - Custom NFTs (from cache)
    - Custom collections (from cache)
    - Deployed contracts (from blockchain)
    - CEP-18 token balances
    - NFTs owned
    - Recent activity
  - Copy-to-clipboard buttons for IDs

- **Admin Page** (`src/public/admin.html`, 363 lines - NEW)
  - Manual forms to add tokens, NFTs, collections to cache
  - View cache contents
  - Success/error feedback

### Backend
- **FastAPI Server** (`src/main.py`)
  - `POST /api/chat` - Chat messages (routed through LangGraph agent)
  - `GET /api/portfolio` - Portfolio data (queries blockchain + cache)
  - `POST /api/admin/log-token` - Manually add token to cache
  - `POST /api/admin/log-nft` - Manually add NFT to cache
  - `POST /api/admin/log-collection` - Manually add collection to cache
  - `GET /api/health` - Health check

- **LangGraph Agent** (`src/agent.py`)
  - Routes user queries to appropriate tools
  - Supports 8 blockchain tools (query balance, deploy contract, etc.)
  - Uses dynamic system prompt built from available MCP tools

- **MCP Client** (`src/mcp_client.py`)
  - Connects to CSPR.cloud MCP server
  - Provides 87+ blockchain tools
  - Handles authentication and network routing

- **Smart Contracts** (Rust/Odra)
  - `TokenFactory.wasm` - Deploy, transfer, check balances of custom tokens
  - `NftMarketplace.wasm` - Mint, list, buy NFTs
  - `CollectionFactory.wasm` - Create collections, mint from collections
  - All deployed on Casper Testnet

- **Cache & Registry**
  - `portfolio_cache.json` - Stores token/NFT/collection deployments
  - `src/portfolio_cache.py` - Cache management functions
  - `src/contract_registry.py` - Multi-contract tracking

### Documentation
- `QUICKSTART.md` (130 lines) - 5-minute setup
- `SETUP.md` (568 lines) - Complete installation & deployment guide
- `USER_GUIDE.md` (505 lines) - Feature documentation & workflows
- `AGENTS.md` (450 lines) - Technical architecture
- `INDEX.md` (364 lines) - Project navigation
- `README.md` - Project overview

---

## 🔑 Key Technical Decisions

### Wallet Integration
- Support multiple wallet API names for compatibility
- Call wallet provider as function to get actual API
- Use async/await for wallet method calls
- Cache public key in localStorage for persistence

### Portfolio Data
- Combine multiple data sources:
  - Blockchain queries (via MCP for deployed contracts)
  - Portfolio cache (for tracked deployments)
  - This gives complete visibility even if cache is incomplete

### Forms
- Modal-based forms with client-side validation
- Auto-populate chat input on form submission
- Fallback to natural language chat if forms don't work

### Caching Strategy
- JSON file-based cache (simple, no database needed)
- Manual admin dashboard for legacy deployments
- Future: Could auto-detect deployments from blockchain

---

## 📍 Current State

### What Works ✅
- Wallet connection and account display
- Chat interface with natural language queries
- All 5 modal forms for token/NFT/collection operations
- Portfolio page displays:
  - CSPR balance
  - Deployed contracts (from blockchain)
  - Token counts
  - NFT counts
- Admin dashboard to manually add deployments
- Form validation with error messages
- Responsive design (mobile/tablet/desktop)
- All 12 integration tests passing

### Known Limitations
- Custom tokens/NFTs/collections only show if logged to cache
  - Solution: Use admin dashboard at `/admin` to add them
- Portfolio cache doesn't auto-detect old deployments
  - Solution: Implemented admin dashboard for manual entry
- Wallet connection requires Casper Wallet extension installed
- Only works on Casper Testnet (configured in .env)

### What Needs Manual Setup
1. **Portfolio Cache Population**
   - New deployments through chat: Auto-logged ✅
   - Old deployments: Must use admin dashboard `/admin`

2. **Environment Variables** (.env)
   - `OPENAI_API_KEY` - Required for chat
   - `CSPR_CLOUD_API_KEY` - Required for blockchain queries
   - `SECRET_KEY` - Optional, for CSPR transfers
   - `WALLET_ACCOUNT_HASH` - Optional, but recommended

---

## 🚀 How to Continue Development

### Adding New Features
1. **New Modal Form**:
   - Add HTML form in `src/public/index.html`
   - Add submission function
   - Add suggestion chip to trigger it

2. **New Blockchain Tool**:
   - Add tool function in `src/tools.py` with `@tool` decorator
   - Register in agent system prompt
   - Test in `tests/test_integration.py`

3. **New API Endpoint**:
   - Add route in `src/main.py`
   - Use MCP client for blockchain queries
   - Return JSON response

### Debugging
- **Wallet issues**: Check browser console (F12 → Console)
- **API errors**: Check server logs
- **Portfolio empty**: Use `/admin` dashboard to populate cache
- **Form validation**: Check console for validation errors

---

## 📊 File Structure
```
casper-agentic-bot/
├── src/
│   ├── main.py                 # FastAPI server + endpoints
│   ├── agent.py                # LangGraph AI agent
│   ├── tools.py                # Blockchain tools
│   ├── mcp_client.py           # MCP client
│   ├── portfolio_cache.py      # Cache management
│   ├── contract_registry.py    # Contract tracking
│   ├── account_analyzer.py     # Account queries
│   └── public/
│       ├── index.html          # Chat page (1304 lines)
│       ├── portfolio.html      # Portfolio page (835 lines)
│       └── admin.html          # Admin dashboard (363 lines)
├── smart-contract/
│   └── src/
│       ├── token_factory.rs
│       ├── nft_marketplace.rs
│       └── collection_factory.rs
├── tests/
│   └── test_integration.py     # 12 integration tests
├── portfolio_cache.json        # Cache file (auto-created)
├── .env.example                # Environment template
├── requirements.txt            # Python dependencies
├── QUICKSTART.md
├── SETUP.md
├── USER_GUIDE.md
├── AGENTS.md
├── INDEX.md
└── PROJECT_STATUS.md          # This file
```

---

## 🧪 Testing

### Run Integration Tests
```bash
python -m pytest tests/test_integration.py -v
```
Expected: All 12 tests passing ✅

### Manual Testing
1. **Connect Wallet**: Click button, approve in extension
2. **Deploy Token**: Use chat modal, check portfolio
3. **Check Portfolio**: Should show deployed contracts from blockchain
4. **Add Old Deployments**: Use `/admin` dashboard
5. **Responsive**: Resize window, test on mobile

---

## 🔗 Important URLs

Local Development:
- Chat: `http://localhost:8000`
- Portfolio: `http://localhost:8000/portfolio`
- Admin Dashboard: `http://localhost:8000/admin`
- Health Check: `http://localhost:8000/api/health`

APIs:
- Chat: `POST /api/chat`
- Portfolio: `GET /api/portfolio?public_key=...`
- Log Token: `POST /api/admin/log-token?name=...&symbol=...`
- Log NFT: `POST /api/admin/log-nft?token_id=...&metadata_uri=...`
- Log Collection: `POST /api/admin/log-collection?name=...&symbol=...&base_uri=...`

External:
- Casper Testnet: Configured via CSPR_CLOUD_API_KEY
- Smart Contracts: Deployed on Casper Testnet
- OpenAI API: For chat responses

---

## 💡 Next Steps for New Developer

1. **Understand the flow**:
   - User connects wallet → Chat page loads
   - User deploys contract via modal → Logged to cache
   - Portfolio page queries blockchain + cache → Shows all deployments

2. **Test the system**:
   - Start server: `uvicorn src.main:app --reload`
   - Connect wallet
   - Try deploying a token
   - Check portfolio
   - Use `/admin` to add old deployments

3. **Potential improvements**:
   - Auto-detect deployments from blockchain
   - Add more modal forms for other operations
   - Implement transaction confirmation UI
   - Add transaction history
   - Support mainnet in addition to testnet

---

## 📝 Session Notes

### Key Commits (Latest Session)
- `d64b04b` - Fix wallet detection to use window.casper
- `93f1a55` - Handle CasperWalletProvider as function
- `540915a` - Get public key from getActivePublicKey()
- `bb1033a` - Add portfolio data loading debug logs
- `da7fc96` - Display deployed contracts from blockchain
- `144cb51` - Add admin endpoints for manual cache logging
- `ff90902` - Create admin dashboard HTML page

### What Was Discovered
1. Casper Wallet extension uses `CasperWalletProvider`, not `casper`
2. `requestConnection()` returns boolean, not public key
3. Must call `getActivePublicKey()` separately after connection
4. Portfolio cache needs manual population for legacy deployments
5. Portfolio data should combine blockchain queries + local cache

### Debugging Techniques Used
- Browser console logging with detailed messages
- Server-side debug logging to stderr
- JSON response inspection
- Testing API endpoints directly
- Checking localStorage values

---

## ⚠️ Important Notes

- **Testnet Only**: All contracts on Casper Testnet (configured in .env)
- **Cache File**: `portfolio_cache.json` is auto-created, must be in project root
- **Wallet Required**: Must have Casper Wallet extension installed
- **API Keys Required**: OPENAI_API_KEY and CSPR_CLOUD_API_KEY must be set
- **No Database**: Using JSON file caching, can scale to DB if needed

---

## 🎓 For Next Developer

When picking up this project:

1. **First**: Read `QUICKSTART.md` to get running
2. **Second**: Check `src/public/index.html` to understand UI structure
3. **Third**: Review `src/main.py` to understand API flow
4. **Fourth**: Look at `src/agent.py` to see tool routing
5. **Fifth**: Test the admin dashboard at `/admin`

**If wallet not working**: Check `src/public/index.html` lines 1051-1210 for wallet connection logic
**If portfolio empty**: Go to `http://localhost:8000/admin` and manually add your deployments
**If API errors**: Check `src/main.py` line 61-160 for portfolio endpoint

---

**Last Updated**: Session 5 (Wallet + Portfolio Fixes)
**Status**: Ready for testing and deployment ✅
**Tested By**: User testing during session 5
**Production Ready**: YES ✅
