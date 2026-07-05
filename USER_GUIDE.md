# User Guide - Casper Agentic Bot

## Overview

Casper Agentic Bot is an AI-powered chatbot for the Casper blockchain. You can interact with it in two ways:

1. **Chat (Natural Language)** - Ask questions in plain English
2. **Forms (Structured Input)** - Use modal forms for precise control

---

## Getting Started

### Opening the Application

1. Start the server (see SETUP.md)
2. Open **http://localhost:8000** in your browser
3. You should see the Chat page with:
   - Animated robot hero section
   - Message area in the middle
   - Suggestion chips at the bottom
   - Text input field

### Connecting Your Wallet

1. Click **"Connect Wallet"** button in the top-right
2. Install Casper Wallet extension if prompted
3. Approve connection
4. Your public key will display in the button
5. You're ready to use portfolio features

---

## Chat Page Features

### 1. Hero Section (Collapsed After First Message)
- **Animated robot** with orbiting blockchain icons
- **Title**: "Agentic AI for the Casper Blockchain"
- **Description**: Explains what you can do
- **Call-to-action buttons**: "Create Token" or "Mint NFT"
- **Auto-collapses** when you send your first message

### 2. Suggestion Chips (Quick Actions)

Organized by category. Click any to send the suggestion:

#### Explore
- **Network Status** - Check Casper network state
- **Latest Blocks** - See recent blocks
- **Analyze Wallet** - Analyze account activity

#### Tokens (Token Factory)
- **🪙 Deploy Token** - Opens modal form
- **💸 Transfer** - Opens modal form
- **💰 Check Balance** - Opens modal form

#### NFTs (NFT Marketplace)
- **🖼️ NFT Marketplace** - Opens modal with 3 tabs:
  - **Mint** tab: Mint new NFTs
  - **List** tab: List NFTs for sale
  - **Buy** tab: Purchase listed NFTs

#### Collections (Collection Factory)
- **🏛️ Create Collection** - Opens modal form
- **List Collections** - View all collections via chat

#### Contracts
- **📦 Deploy Contract** - Deploy new contracts
- **List Contracts** - View deployed contracts

#### Actions
- **Send CSPR** - Opens prompt for CSPR transfer
- **📊 Portfolio** - Navigate to portfolio page

### 3. Message Area
- **User messages**: Light blue background, right-aligned
- **Bot messages**: Dark background, left-aligned
- **Formatting support**:
  - `**bold**` → **bold text**
  - `*italic*` → *italic text*
  - Backticks `` `code` `` → `code`
  - Links and transaction hashes are highlighted
- **Typing animation**: Animated dots when agent is thinking

### 4. Text Input
- **Placeholder**: "Deploy tokens, mint NFTs, check balances..."
- **Send button**: Click or press Enter
- **Auto-focus**: Cursor in input when page loads
- **Disabled during response**: Prevents multiple sends

---

## Using Modal Forms

### Deploy Token 🪙
**Click**: Suggestion chip "🪙 Deploy Token"

**Form Fields**:
1. **Token Name** (required)
   - Example: "MyToken", "RocketCoin", "DemoCoin"
   - Max length: unlimited

2. **Symbol** (required)
   - Example: "MTK", "RCK", "DMC"
   - Max length: 10 characters
   - Usually 3-4 letters

3. **Decimals** (required)
   - Range: 0-18
   - Typical value: 8 (like USDC)
   - Higher = more precision

4. **Total Supply** (required)
   - Example: "1000000", "500000000"
   - This is the initial supply created

**What happens**:
- Form submits as: `"Deploy a token called {name} with symbol {symbol}, {decimals} decimals, and {supply} total supply"`
- Agent deploys to Casper Testnet
- Check Portfolio to see your token

---

### Transfer Token 💸
**Click**: Suggestion chip "💸 Transfer"

**Form Fields**:
1. **Token ID** (required)
   - Example: "0", "1", "2"
   - Which token to transfer
   - Check Portfolio for token IDs

2. **Recipient Account Hash** (required)
   - Example: `account-hash-2bc76a5348a847ff51738945d681b97dda6ed606f7ae4282d1a0eb409ef301f5`
   - Must start with `account-hash-`
   - Destination wallet

3. **Amount** (required)
   - Example: "1000", "100.5"
   - How many tokens to send

**What happens**:
- Form submits as: `"Transfer {amount} of token {id} to {recipient}"`
- Agent signs transaction
- Tokens sent to recipient

---

### Check Token Balance 💰
**Click**: Suggestion chip "💰 Check Balance"

**Form Fields**:
1. **Token ID** (required)
   - Example: "0", "1"
   - Which token to check

2. **Account Hash** (required)
   - Example: `account-hash-abc...`
   - Whose balance to check

**What happens**:
- Form submits as: `"What is the balance of token {id} for account {account}?"`
- Agent queries blockchain
- Returns balance for that account/token

---

### NFT Marketplace 🖼️
**Click**: Suggestion chip "🖼️ NFT Marketplace"

**Tabbed Interface** (3 operations):

#### Tab 1: Mint NFT
**Purpose**: Create a new NFT

**Form Fields**:
1. **Metadata URI** (required)
   - Example: `ipfs://Qm...`, `https://example.com/nft.json`
   - Location of NFT metadata (name, image, properties)

2. **Recipient Account Hash** (required)
   - Example: `account-hash-xyz...`
   - Who receives the NFT

**What happens**:
- Form submits as: `"Mint an NFT with metadata URI {uri} to {recipient}"`
- Agent mints NFT to recipient
- NFT appears in Portfolio

#### Tab 2: List NFT for Sale
**Purpose**: Put an NFT on marketplace

**Form Fields**:
1. **NFT Token ID** (required)
   - Example: "0", "1"
   - Which NFT to list

2. **Price (in CSPR)** (required)
   - Example: "100", "50.5"
   - Selling price in CSPR tokens

**What happens**:
- Form submits as: `"List NFT {id} for sale at {price} CSPR"`
- Agent lists NFT on marketplace
- Portfolio shows "Listed for X CSPR" badge

#### Tab 3: Buy NFT
**Purpose**: Purchase a listed NFT

**Form Fields**:
1. **NFT Token ID** (required)
   - Example: "0"
   - Which NFT to buy

2. **Buyer Account Hash** (required)
   - Example: `account-hash-xyz...`
   - Who will own the NFT

**What happens**:
- Form submits as: `"Buy NFT {id} as {buyer}"`
- Agent handles payment separately
- NFT transferred to buyer

---

### Create Collection 🏛️
**Click**: Suggestion chip "🏛️ Create Collection"

**Form Fields**:
1. **Collection Name** (required)
   - Example: "CyberPunks", "ArtCollection"
   - Display name for collection

2. **Symbol** (required)
   - Example: "CYBER", "ART"
   - Short code for collection
   - Max: 10 chars

3. **Base URI** (required)
   - Example: `ipfs://QmXXX/`, `https://example.com/nfts/`
   - Base URL for NFT metadata
   - Typically a folder path
   - Should end with `/`

4. **Mint Price (in CSPR)** (required)
   - Example: "10", "5.5"
   - Cost to mint NFTs in this collection

**What happens**:
- Form submits as: `"Create a collection called {name} with symbol {symbol}, base_uri {uri} and mint_price {price} CSPR"`
- Agent creates collection
- Collection appears in Portfolio
- Others can mint from collection

---

## Portfolio Page Features

### Access Portfolio
1. **From Chat**: Click "📊 Portfolio" suggestion chip
2. **Direct URL**: http://localhost:8000/portfolio
3. **Requires**: Wallet connection

### Page Layout

#### Header Section
- **Title**: "Wallet Portfolio"
- **Description**: "Overview of your on-chain assets on Casper Testnet"
- **Wallet Address**: Short address with copy button
  - Click 📋 to copy full address to clipboard

#### Summary Cards
Four metric cards at top:
1. **💰 CSPR Balance** - Your native CSPR balance
2. **🪙 CEP-18 Tokens** - Standard tokens in wallet
3. **🖼️ NFTs** - NFTs you own
4. **📜 Contracts** - Contracts you deployed

#### Sections Below

**🪙 Token Factory Tokens**
- Shows all custom tokens you deployed
- For each token:
  - Token name and symbol
  - Total supply
  - Decimals
  - Token ID (click "📋 Copy ID")
  - Transaction hash
  - Status badge (pending/active)

**🏛️ Collections**
- Shows collections you created
- For each collection:
  - Name and symbol
  - Base URI (metadata folder)
  - Mint price in CSPR
  - Collection ID
  - Transaction hash
  - Status badge

**🖼️ Custom NFTs (Agent Minted)**
- Shows NFTs minted through the agent
- For each NFT:
  - NFT ID
  - Metadata URI
  - Collection name
  - Recipient wallet
  - Status badge

**🪙 CEP-18 Token Balances**
- Shows standard tokens in your wallet
- For each token:
  - Token name
  - Your balance
  - Token symbol
  - Note: Separate from Token Factory tokens

**🖼️ NFTs**
- Shows NFTs in your portfolio
- For each NFT:
  - NFT ID
  - Collection info
  - Metadata URI
  - **NEW: Status badge** (Listed for X CSPR / Not Listed)

**📋 Recent Activity**
- Shows recent blockchain activity
- Deployment transactions
- Transaction hashes
- Timestamps

---

## Common Workflows

### Workflow 1: Deploy & Transfer Tokens

1. **Deploy**: Click "🪙 Deploy Token" modal
   - Enter: Name, Symbol, Decimals, Supply
   - Submit → Token deployed

2. **Check**: Click "💰 Check Balance" modal
   - Enter: Token ID, Your account hash
   - Submit → See your balance

3. **Transfer**: Click "💸 Transfer" modal
   - Enter: Token ID, Recipient, Amount
   - Submit → Tokens sent

4. **Verify**: Go to Portfolio
   - See deployed token in "Token Factory Tokens" section
   - Click "📋 Copy ID" to get token ID

### Workflow 2: Create NFT Collection & Mint

1. **Create**: Click "🏛️ Create Collection" modal
   - Enter: Name, Symbol, Base URI, Mint Price
   - Submit → Collection created

2. **Mint**: Click "🖼️ NFT Marketplace" → Mint tab
   - Enter: Metadata URI, Recipient
   - Submit → NFT minted to collection

3. **View**: Go to Portfolio
   - See collection in "🏛️ Collections" section
   - See NFT in "🖼️ Custom NFTs" section

### Workflow 3: Buy NFT from Marketplace

1. **List**: Click "🖼️ NFT Marketplace" → List tab
   - Enter: NFT ID, Price (e.g., 100 CSPR)
   - Submit → NFT listed

2. **Buy**: Click "🖼️ NFT Marketplace" → Buy tab
   - Enter: NFT ID, Buyer account
   - Submit → NFT transferred to buyer
   - Note: Payment handled separately by agent

3. **Verify**: Portfolio updates to show new owner

---

## Tips & Tricks

### Copy IDs Easily
- Portfolio cards have "📋 Copy ID" button
- Click to copy token ID, NFT ID, or collection ID
- Paste into forms

### Check Status
- Portfolio "Status" badges show:
  - 🟢 **Active** = Confirmed on blockchain
  - 🔴 **Pending** = Still processing

### Use Chat Fallback
- All modal operations work via chat too
- Example: "Deploy a token called MyToken with symbol MTK, 8 decimals, 1000000 supply"
- Useful if modal doesn't work or you prefer typing

### Save Frequently Used Values
- Keep common account hashes handy
- Bookmark collection base URIs
- Remember token IDs after deployment

### Clear Cache
- If forms don't appear: Ctrl+Shift+Delete (clear cache)
- Refresh page: F5 or Ctrl+R
- Hard refresh: Ctrl+Shift+R

---

## Troubleshooting

### "Wallet not connected"
- **Solution**: Click "Connect Wallet" button, install extension if needed

### Form doesn't submit
- **Solution**: Check all fields are filled (red error message shows what's wrong)

### Transaction failed
- **Solution**: Check CSPR balance, verify account hash format

### Portfolio page blank
- **Solution**: Refresh page, check wallet connection

### Agent doesn't respond
- **Solution**: Check internet, try simpler query, wait for rate limits

### Copy button doesn't work
- **Solution**: Check browser permissions, manual copy with Ctrl+C

---

## Safety & Best Practices

### Protect Your Keys
- ❌ Never share your SECRET_KEY
- ❌ Never paste keys in chat
- ✅ Only add keys to `.env` file locally
- ✅ Use testnet only for development

### Verify Addresses
- ✅ Double-check account hashes before transferring
- ✅ Copy from Portfolio to avoid typos
- ✅ Use "📋 Copy" buttons instead of manual typing

### Understand Costs
- ⚠️ Every transaction costs CSPR (testnet tokens)
- ⚠️ Deployments cost 500 CSPR
- ⚠️ Transfers cost ~5 CSPR each
- ✅ Use testnet for testing (free from faucets)

### Monitor Activity
- ✅ Check Portfolio frequently
- ✅ Verify status badges before relying on assets
- ✅ Monitor recent activity for transactions

---

## Advanced Usage

### Query via Chat
If modals feel limiting, use natural language:
- "Deploy a token called RocketCoin with symbol RCKT, 18 decimals, and 999999999999999999 total supply"
- "Transfer 5000 tokens of token 1 to account-hash-abc..."
- "What NFTs are in collection 0?"

### Chained Operations
Ask agent to do multiple steps:
- "Deploy a token, then transfer 1000 to my wallet"
- "Create a collection, then mint 10 NFTs to it"
- "List all my NFTs and show their prices"

### Custom Queries
- "Show me the top accounts by CSPR balance"
- "When was my account created?"
- "How many validators are on Casper right now?"

---

## Glossary

- **Token ID**: Unique number identifying a custom token (0, 1, 2, ...)
- **NFT ID**: Unique number identifying an NFT
- **Collection ID**: Unique number identifying an NFT collection
- **Account Hash**: Long string like `account-hash-abc...` (wallet ID)
- **CSPR**: Native token on Casper network
- **Testnet**: Casper's test blockchain (free tokens, real contracts)
- **Metadata URI**: URL pointing to NFT metadata (name, image, properties)
- **Base URI**: Folder path for collection metadata (e.g., `ipfs://QmXXX/`)

---

## Getting Help

1. **Check SETUP.md** - Installation & configuration
2. **Check QUICKSTART.md** - 5-minute setup guide
3. **Check README.md** - Project overview
4. **Check AGENTS.md** - Technical architecture details
5. **Check browser console** - Press F12 → Console for errors
6. **Restart server** - Often fixes connectivity issues

---

**Enjoy exploring the Casper blockchain! 🚀**
