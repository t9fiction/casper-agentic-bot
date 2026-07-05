# 🤖 AI CHATBOT NFT TESTING & VERIFICATION GUIDE

**Updated: 2026-07-05**

This guide shows you exactly how to test the AI chatbot's NFT capabilities using real examples. Each section includes:
- What to type in the chat
- What to expect from the AI
- How to verify it worked

---

## QUICK START: Test in 5 minutes

### Step 1: Open the App
```
cd casper-agentic-bot
source .venv/bin/activate
uvicorn src.main:app --reload
```
Open: http://localhost:8000

### Step 2: Connect Wallet
- Click "🔗 Connect Wallet"
- Approve in CasperWallet extension
- You should see your account hash and CSPR balance

### Step 3: Test #1 — Mint a Single NFT

**Type in chat:**
```
Mint an NFT with metadata URI ipfs://QmExample/nft-1.json to my account
```

**Expected Response:**
- ✅ AI identifies this as NFT Marketplace mint
- ✅ AI calls entry point: `mint_nft`
- ✅ Shows transaction hash: `Transaction Hash: 0x...`
- ✅ NFT appears in Portfolio → 🖼️ NFTs

**Verify in Portfolio:**
- Go to Portfolio page
- Scroll to 🖼️ NFTs section
- Should show: "ipfs://QmExample/nft-1.json"

---

### Step 4: Test #2 — Create a Collection

**Type in chat:**
```
Create a collection called Pets with symbol PET, base_uri ipfs://QmPets/ and mint price 0
```

**Expected Response:**
- ✅ AI validates all parameters (name, symbol, base_uri, mint_price)
- ✅ AI converts mint_price to motes (0 CSPR = 0 motes)
- ✅ AI calls create_collection on collections contract
- ✅ Shows transaction hash
- ✅ Returns collection_id

**Verify in Portfolio:**
- Go to Portfolio page
- Look for Collections section
- Should show: "Pets (PET)" with base_uri

---

### Step 5: Test #3 — Mint NFTs in Collection

**Type in chat:**
```
Mint 3 NFTs to my account in the Pets collection
```

**Expected Response:**
- ✅ AI identifies collection_id (should be 0 or latest)
- ✅ AI calls mint_nft 3 times
- ✅ Each mint auto-generates URI: ipfs://QmPets/0.json, ipfs://QmPets/1.json, ipfs://QmPets/2.json
- ✅ Shows 3 transaction hashes

**Verify in Portfolio:**
- Portfolio → 🖼️ NFTs
- Should show 3 NFTs from Pets collection with auto-generated URIs

---

## DETAILED TEST SCENARIOS

### Scenario 1: NFT Marketplace (Single NFT)

**What it does:**
- Mints individual NFTs with custom metadata URIs
- Each NFT is independent
- Good for unique, one-of-a-kind items

**Test Case:**
```
Chat: "Mint NFT with metadata URI ipfs://QmABC/mystical-dragon.json"
```

**Behind the Scenes:**
```python
# AI runs:
call_contract_entry_point(
    entry_point="mint_nft",
    session_args={
        "metadata_uri": "ipfs://QmABC/mystical-dragon.json",
        "recipient": "account-hash-XXX"  # Your wallet
    }
    # contract_name defaults to "nft_marketplace"
)
```

**What Happens:**
1. AI extracts your account hash from connected wallet
2. AI calls mint_nft entry point
3. Smart contract creates NFT with unique token_id
4. NFT is owned by your account
5. Transaction hash returned and tracked

**Verify:**
```javascript
// Check in browser console:
fetch('/api/portfolio?public_key=account-hash-XXX')
  .then(r => r.json())
  .then(d => console.log(d.nfts))
// Should show your newly minted NFT
```

---

### Scenario 2: Collection Factory (Series of NFTs)

**What it does:**
- Creates a "template" for a collection
- All NFTs in collection share same base_uri
- URIs auto-generated: base_uri + token_id + ".json"
- Good for series, limited editions, bulk minting

**Test Case:**
```
Chat: "Create a collection called CyberPunks with symbol CYBR,
       base_uri ipfs://Qm1234CyberPunks/ and mint price 1 CSPR"
```

**Behind the Scenes:**
```python
# AI converts 1 CSPR to motes:
mint_price_motes = 1 * 1_000_000_000  # = 1000000000

# AI runs:
call_contract_entry_point(
    entry_point="create_collection",
    session_args={
        "name": "CyberPunks",
        "symbol": "CYBR",
        "base_uri": "ipfs://Qm1234CyberPunks/",
        "mint_price": "1000000000"  # in motes
    },
    contract_name="collections"
)
```

**What Happens:**
1. AI validates all 4 required parameters
2. AI calls create_collection on collections contract
3. Smart contract stores collection with ID (u32)
4. Collection creator is set to your account
5. Returns collection_id (e.g., 0, 1, 2...)

**Result:**
```json
{
  "collection_id": 0,
  "name": "CyberPunks",
  "symbol": "CYBR",
  "base_uri": "ipfs://Qm1234CyberPunks/",
  "mint_price": "1000000000 motes",
  "transaction_hash": "0x..."
}
```

---

### Scenario 3: Batch Minting in Collection

**Test Case:**
```
Chat: "Mint 5 NFTs to my account in the CyberPunks collection"
```

**Behind the Scenes:**
```python
# AI runs 5 times:
for i in range(5):
    call_contract_entry_point(
        entry_point="mint_nft",
        session_args={
            "collection_id": 0,
            "recipient": "account-hash-XXX"
        },
        contract_name="collections"
    )
    # Each returns token_id: 0, 1, 2, 3, 4
```

**Auto-Generated URIs:**
```
NFT #0: ipfs://Qm1234CyberPunks/0.json
NFT #1: ipfs://Qm1234CyberPunks/1.json
NFT #2: ipfs://Qm1234CyberPunks/2.json
NFT #3: ipfs://Qm1234CyberPunks/3.json
NFT #4: ipfs://Qm1234CyberPunks/4.json
```

**Important:**
- All 5 metadata JSON files MUST exist on IPFS
- At base_uri path with these exact filenames
- If any file missing, metadata fetch fails

**Verify:**
```javascript
// Check portfolio
fetch('/api/portfolio')
  .then(r => r.json())
  .then(d => {
    console.log("NFTs in collection:");
    d.nfts.forEach(nft => console.log(nft.metadata_uri));
  })
```

Expected output:
```
ipfs://Qm1234CyberPunks/0.json
ipfs://Qm1234CyberPunks/1.json
ipfs://Qm1234CyberPunks/2.json
ipfs://Qm1234CyberPunks/3.json
ipfs://Qm1234CyberPunks/4.json
```

---

### Scenario 4: Complex Multi-Step Workflow

**Test Case:**
```
Chat: "Create a collection called ArtGallery with symbol ART,
       base_uri ipfs://QmGallery/ and 0 CSPR,
       then mint 3 NFTs to me in that collection"
```

**What AI Does (Multi-Step):**

**Step 1: Create Collection**
```
create_collection(name="ArtGallery", symbol="ART",
                  base_uri="ipfs://QmGallery/", mint_price="0")
→ Returns: collection_id = 0
```

**Step 2: Mint NFT #1**
```
mint_nft(collection_id=0, recipient="your-account")
→ Returns: token_id = 0
→ Auto-generated URI: ipfs://QmGallery/0.json
```

**Step 3: Mint NFT #2**
```
mint_nft(collection_id=0, recipient="your-account")
→ Returns: token_id = 1
→ Auto-generated URI: ipfs://QmGallery/1.json
```

**Step 4: Mint NFT #3**
```
mint_nft(collection_id=0, recipient="your-account")
→ Returns: token_id = 2
→ Auto-generated URI: ipfs://QmGallery/2.json
```

**AI Response Timeline:**
```
🔄 Creating collection ArtGallery...
✅ Collection created (ID: 0)
   Transaction: 0x...

🔄 Minting NFT #0...
✅ NFT #0 minted
   URI: ipfs://QmGallery/0.json
   Transaction: 0x...

🔄 Minting NFT #1...
✅ NFT #1 minted
   URI: ipfs://QmGallery/1.json
   Transaction: 0x...

🔄 Minting NFT #2...
✅ NFT #2 minted
   URI: ipfs://QmGallery/2.json
   Transaction: 0x...

✅ All done! 3 NFTs created in ArtGallery collection.
```

---

## AI CAPABILITIES CHECKLIST

### ✅ What AI Can Do

**Collection Management:**
- [x] Create a collection (name, symbol, base_uri, mint_price)
- [x] List all collections
- [x] Get collection info (name, symbol, creator, total_supply)
- [x] Validate required parameters before calling

**NFT Operations:**
- [x] Mint single NFT (Marketplace) with custom metadata URI
- [x] Mint multiple NFTs in collection with auto-generated URIs
- [x] Transfer NFT to another account
- [x] List NFT for sale (with price in CSPR)
- [x] Buy NFT (with payment to owner)
- [x] Get NFT info (owner, creator, metadata_uri, price)
- [x] Check NFT ownership

**Token Operations:**
- [x] Deploy custom token (name, symbol, decimals, supply)
- [x] Transfer tokens
- [x] Check token balance
- [x] Get token info
- [x] Mint additional tokens (deployer only)

**Multi-Step Workflows:**
- [x] Create collection + mint X NFTs in one command
- [x] Deploy token + transfer to friend + check balances
- [x] List NFT + collect payment + transfer in sequence
- [x] Track state across multiple steps

**Conversation Features:**
- [x] Remember context from previous messages (session memory)
- [x] Track collection IDs and contract names
- [x] Ask for missing parameters before proceeding
- [x] Explain transaction hashes clearly
- [x] Guide users through required steps

---

### ❌ What AI Cannot Do

- [ ] Mint without specifying (metadata_uri for Marketplace OR collection details for Factory)
- [ ] Create collection without all 4 parameters (name, symbol, base_uri, mint_price)
- [ ] Accept metadata URIs that don't exist on IPFS
- [ ] Send CSPR without valid recipient account hash
- [ ] List NFT without token_id
- [ ] Buy NFT without checking owner and price first

**Instead:** AI will ask for missing info or explain what's needed.

---

## PARAMETER VALIDATION

### When AI Asks for Missing Parameters

**Scenario:** User says "Create a collection"

**AI Response:**
```
I'd like to create a collection for you! I need a few details:

1. **Name** - What should the collection be called? (e.g., "CyberPunks")
2. **Symbol** - Short symbol (e.g., "CYBR")
3. **Base URI** - IPFS path where metadata files are stored
   (e.g., "ipfs://QmXYZ/")
4. **Mint Price** - Cost per NFT in CSPR (e.g., 1, 10, or 0 for free)

Please provide these details and I'll create it!
```

**Why:** AI checks for these BEFORE calling the contract:
- Prevents wasted transactions
- Validates format (e.g., base_uri must end with /)
- Confirms user intent
- Converts units correctly (CSPR → motes)

---

## UNIT CONVERSIONS AI PERFORMS

### CSPR ↔ Motes
```python
# When user says "1 CSPR":
motes = 1 * 1_000_000_000  # = 1,000,000,000 motes

# When user says "50 CSPR":
motes = 50 * 1_000_000_000  # = 50,000,000,000 motes

# If mint_price in JSON shows "1000000000", AI displays: "1 CSPR"
```

**How AI displays it:**
```
Mint Price: 1 CSPR (1,000,000,000 motes)
```

---

## TRANSACTION TRACKING

### Every Operation Returns a Transaction Hash

**Example Response:**
```
✅ NFT Minted!
   Token ID: 5
   Metadata URI: ipfs://QmExample/nft-5.json
   Owner: account-hash-2bc76a534...
   Transaction Hash: 0x1234567890abcdef...

   ⏳ The transaction will be finalized in ~30 seconds.
   Want to verify? Run: "Check transaction 0x1234567890abcdef"
```

**How to Verify:**
```
Chat: "Verify transaction 0x1234567890abcdef"
```

AI will call `verify_contract_deployment` and show:
```
✅ Transaction confirmed!
   Block: 12345
   Status: EXECUTED
   Gas Used: 523,000
```

---

## SESSION MEMORY EXAMPLES

AI remembers across messages in the same conversation:

### Example 1: Collection ID Memory
```
Message 1:
  User: "Create collection Pets with base_uri ipfs://Pets/ and mint 0"
  AI: "✅ Collection created (ID: 0)"

Message 2:
  User: "Mint 5 NFTs to me"
  AI: "I'll mint 5 NFTs in the Pets collection (ID: 0) ..."
  ✅ AI remembered the collection ID from message 1!
```

### Example 2: Contract Name Tracking
```
Message 1:
  User: "Deploy a contract called MyNFTs"
  AI: "✅ Deploying MyNFTs..."

Message 2:
  User: "Mint an NFT to me on MyNFTs"
  AI: "I'll mint on the MyNFTs contract..."
  ✅ AI remembered contract name from message 1!

Message 3:
  User: "List my contracts"
  AI: Shows MyNFTs in the list
  ✅ AI tracked deployment across 2 messages!
```

---

## TESTING CHECKLIST

Use this to systematically test all features:

### Part 1: Basic Operations (5 min)
- [ ] Connect wallet successfully
- [ ] See portfolio with balance
- [ ] Chat "Hello" and get response
- [ ] Chat "What's the network?" and see testnet

### Part 2: Single NFT (10 min)
- [ ] Chat: "Mint an NFT with metadata URI ipfs://QmTest/nft-1.json"
- [ ] See transaction hash in response
- [ ] Wait 30 seconds
- [ ] Check Portfolio → NFTs and see it listed

### Part 3: Collection Creation (10 min)
- [ ] Chat: "Create collection MyCollection with symbol MYC, base_uri ipfs://QmMyCollection/ and 0 CSPR"
- [ ] See transaction hash and collection_id
- [ ] Check Portfolio → Collections and see it listed

### Part 4: Batch Minting (10 min)
- [ ] Chat: "Mint 3 NFTs to me in MyCollection"
- [ ] See 3 transaction hashes
- [ ] Check Portfolio → NFTs and see 3 with auto-generated URIs

### Part 5: Multi-Step (10 min)
- [ ] Chat: "Create collection Test2 with base_uri ipfs://QmTest2/ and mint 2 to me"
- [ ] Should see collection creation + 2 mint operations
- [ ] All in one conversation

### Part 6: Session Memory (5 min)
- [ ] Chat: "List all my collections"
- [ ] Chat: "Tell me about collection 0"
- [ ] Chat: "Mint 1 NFT in collection 0" (uses ID from previous message)

---

## TROUBLESHOOTING

### Issue: AI says "Missing required parameters"

**Why:** AI detected incomplete input

**Solution:**
```
Provide: name, symbol, base_uri (with /), mint_price
Example: "Create collection Pets with symbol PET,
          base_uri ipfs://Pets/ and mint price 5"
```

### Issue: "Transaction Hash: undefined" or missing

**Why:** Tool call failed or returned unusual format

**Solution:**
```
1. Check wallet is connected
2. Check you have enough CSPR for gas (~500 CSPR per deploy)
3. Try simpler command: "Mint NFT with ipfs://Test/1.json"
4. Check browser console for errors (F12)
```

### Issue: NFT doesn't appear in portfolio after mint

**Why:** Transaction not yet finalized OR not in cache

**Solution:**
```
1. Wait 30-60 seconds (blockchain processing)
2. Refresh portfolio page (F5)
3. Check blockchain explorer with tx_hash
4. If deployed from CLI, use Admin dashboard to log it
```

### Issue: Collection creation fails

**Why:** Base URI format wrong or mint_price conversion failed

**Solution:**
```
✅ Correct: "ipfs://QmXYZ/" (ends with /)
❌ Wrong:   "ipfs://QmXYZ" (no /)

✅ Correct: mint_price="10" (in CSPR, AI converts to motes)
❌ Wrong:   mint_price="10000000000" (user shouldn't do conversion)
```

---

## QUICK REFERENCE: Common Commands

### Create Collection (with all params)
```
Create a collection called [Name] with symbol [SYMBOL],
base_uri ipfs://[HASH]/ and mint price [AMOUNT] CSPR
```

### Mint Single NFT
```
Mint NFT with metadata URI ipfs://[HASH]/[file].json to my account
```

### Mint Multiple in Collection
```
Mint [NUMBER] NFTs to my account in [CollectionName] collection
```

### List NFT for Sale
```
List NFT #[ID] for [PRICE] CSPR
```

### Buy NFT
```
Buy NFT #[ID] for [PRICE] CSPR
```

### Get Collection Info
```
Show me collection [ID] details
```

### Deploy Token
```
Deploy a token called [Name] with symbol [SYMBOL],
decimals [NUM], total supply [AMOUNT]
```

---

## NEXT STEPS

1. **Test the AI now:** Run the server and try a command
2. **Upload to IPFS:** Prepare metadata JSONs for bulk collection
3. **Create NFT series:** Use Collection Factory for organized batches
4. **Marketplace operations:** Test buy/sell workflows

---

**Questions?** Check NFT_GUIDE.md for detailed workflows or MCP_FIX_SUMMARY.md for technical details.
