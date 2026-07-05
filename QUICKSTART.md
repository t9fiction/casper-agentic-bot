# Quick Start - 5 Minute Setup

## 1. Clone & Setup (1 minute)
```bash
cd casper-agentic-bot
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## 2. Configure (1 minute)
```bash
cp .env.example .env
```

Edit `.env` and add:
- `OPENAI_API_KEY` from https://platform.openai.com/api-keys
- `CSPR_CLOUD_API_KEY` from https://cspr.cloud

## 3. Run (1 minute)
```bash
uvicorn src.main:app --reload
```

Open: **http://localhost:8000**

---

## What You Can Do

### Chat Tab (Natural Language)
- "What's the network status?"
- "Deploy a token called MyToken with symbol MTK, 8 decimals, 1 million supply"
- "Mint an NFT to account-hash-..."
- "Analyze account account-hash-..."

### Modals (Structured Forms)
- Click "🪙 Deploy Token" → Fill form → Auto-sends to agent
- Click "🖼️ NFT Marketplace" → Choose Mint/List/Buy tab → Fill form
- Click "🏛️ Create Collection" → Fill form
- Click "💰 Check Balance" → Fill form

### Portfolio Tab
- View deployed tokens
- View owned NFTs
- View created collections
- Check wallet balance
- Copy IDs with "📋 Copy" buttons

---

## Test Immediately

### No Keys? Use Chat Only
Even without API keys, test locally:
1. Open http://localhost:8000
2. Click suggestion chip "Network Status"
3. Should see response (if API keys configured)

### With Keys? Deploy Tokens
1. Fill "🪙 Deploy Token" modal
2. Submit → Agent deploys to Casper Testnet
3. Check Portfolio to see deployed token

### Check Portfolio
1. Connect Casper Wallet (button in header)
2. Click "📊 Portfolio"
3. See all assets you've created

---

## API Keys (Free)

### OpenAI
- Sign up: https://platform.openai.com
- Create key in: https://platform.openai.com/api-keys
- Copy key starting with `sk-proj-`

### CSPR.cloud
- Sign up: https://cspr.cloud
- Get API key from dashboard
- Use any key provided

---

## Troubleshooting

```bash
# Port already in use?
uvicorn src.main:app --port 3000

# Wrong Python version?
python3 --version  # Should be 3.10+

# Missing OpenAI API?
# Edit .env and add your key
grep OPENAI_API_KEY .env

# Tests failing?
python -m pytest tests/ -v
```

---

## Next Steps

1. ✅ Get server running
2. 🧪 Test modals and chat
3. 🌐 Connect wallet for portfolio
4. 📤 Deploy token/NFT
5. 🚀 Deploy to cloud (Koyeb/Railway/Fly)
6. 📹 Record demo video
7. 📝 Submit to DoraHacks

---

## File Locations

- **Chat UI**: http://localhost:8000 (src/public/index.html)
- **Portfolio UI**: http://localhost:8000/portfolio (src/public/portfolio.html)
- **API Backend**: src/main.py
- **Configuration**: .env
- **Smart Contracts**: smart-contract/src/
- **Tests**: tests/test_integration.py

---

For detailed setup guide, see: **SETUP.md**

For project details, see: **README.md** and **AGENTS.md**
