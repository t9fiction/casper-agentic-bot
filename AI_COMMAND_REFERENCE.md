# 🎯 AI CHATBOT COMMAND REFERENCE

Quick copy-paste commands for all AI capabilities.

---

## NFT MARKETPLACE COMMANDS

### Mint Single NFT
```
Mint an NFT with metadata URI ipfs://QmExample/nft-1.json to my account
```

### Mint Multiple NFTs (Different URIs)
```
Mint these 3 NFTs:
- ipfs://QmExample/nft-1.json
- ipfs://QmExample/nft-2.json
- ipfs://QmExample/nft-3.json
```

### Transfer NFT
```
Transfer NFT #5 to account account-hash-2bc76a5348a847ff51738945d681b97dda6ed606f7ae4282d1a0eb409ef301f5
```

### List NFT for Sale
```
List NFT #5 for 50 CSPR
```

### Unlist NFT
```
Unlist NFT #5 from sale
```

### Buy NFT
```
Buy NFT #5 (I'll pay the owner 50 CSPR)
```

### Check NFT Info
```
Get info about NFT #5
```

### Check Who Owns NFT
```
Who owns NFT #5?
```

### Count Total NFTs
```
How many NFTs have been minted total?
```

---

## COLLECTION FACTORY COMMANDS

### Create Collection (All Parameters)
```
Create a collection called CyberPunks with symbol CYBR,
base_uri ipfs://QmCyberPunks/ and mint price 1 CSPR
```

### Create Free Collection
```
Create a collection called Pets with symbol PET,
base_uri ipfs://QmPets/ and mint price 0
```

### Create Paid Collection
```
Create a collection called BoredApes with symbol BAPE,
base_uri ipfs://QmBoredApes/ and mint price 5 CSPR
```

### Mint Single NFT in Collection
```
Mint an NFT to my account in the CyberPunks collection
```

### Mint Multiple NFTs in Collection
```
Mint 10 NFTs to my account in the CyberPunks collection
```

### Mint Batch (100+)
```
Mint 100 NFTs to my account in the Pets collection
```

### Get Collection Details
```
Show me collection 0 details
```

### Get Collection Info by Name
```
Tell me about the CyberPunks collection
```

### List All Collections
```
List all collections
```

### Get Total Collections
```
How many collections exist?
```

### Get NFTs in Collection
```
Show me all NFTs in collection 0
```

### Get NFT Count in Collection
```
How many NFTs are in the Pets collection?
```

### Transfer NFT Within Collection
```
Transfer NFT #3 to account account-hash-friend
```

### List NFT from Collection for Sale
```
List NFT #0 from CyberPunks for 25 CSPR
```

### Buy NFT from Collection
```
Buy NFT #1 from Pets for 2 CSPR
```

### Check NFT in Collection
```
Get info about NFT #0 in the Pets collection
```

---

## TOKEN FACTORY COMMANDS

### Deploy Custom Token
```
Deploy a token called MyToken with symbol MYT,
decimals 8, and total supply 1,000,000
```

### Deploy Token (Different Decimals)
```
Deploy a token called UltraCoin with symbol ULTRA,
decimals 18, and total supply 1,000,000,000
```

### Check Token Balance
```
Check my balance of token 0
```

### Check Specific Account Balance
```
Check balance of token 0 for account account-hash-2bc76a5348a847ff51738945d681b97dda6ed606f7ae4282d1a0eb409ef301f5
```

### Transfer Tokens
```
Transfer 1000 tokens of token 0 to account account-hash-friend
```

### Transfer Half of Supply
```
Deploy a token GiftToken with symbol GFT, decimals 8, supply 1000000,
then transfer 500000 to account account-hash-friend
```

### Get Token Info
```
Show me info about token 0
```

### Get Total Tokens
```
How many tokens have been deployed?
```

### Mint More Tokens (Deployer Only)
```
Mint 100000 more tokens of token 0 to my account
```

---

## ADVANCED MULTI-STEP WORKFLOWS

### Create Collection + Mint 10
```
Create a collection called ArtGallery with symbol ART,
base_uri ipfs://QmGallery/ and mint price 0,
then mint 10 NFTs to my account in that collection
```

### Deploy Token + Transfer to Friend + Check Balance
```
Deploy a token called FriendCoin with symbol FND, decimals 8, supply 1000000,
then transfer 500000 to account account-hash-friend,
then show both of our balances
```

### Mint + List + Verify Ownership
```
Mint an NFT with ipfs://QmTest/art.json,
list it for 100 CSPR,
and show me its current info
```

### Create 2 Collections + Mint in Both
```
Create collection 1 called Punks with symbol PNK, base_uri ipfs://Punks/ and price 1 CSPR
Create collection 2 called Apes with symbol APE, base_uri ipfs://Apes/ and price 2 CSPR
Then mint 5 in Punks and 5 in Apes to me
```

### Buy NFT Workflow
```
What's the info on NFT #3?
(Then after seeing price)
Buy NFT #3
```

---

## PORTFOLIO & VERIFICATION COMMANDS

### Check My Portfolio
```
Show me my portfolio
```

### Verify Transaction
```
Verify transaction 0x1234567890abcdef
```

### List My Deployed Contracts
```
List all my deployed contracts
```

### Analyze My Account
```
Analyze my account details
```

### Get Network Status
```
What's the network status?
```

### Check Latest Blocks
```
Show me the latest blocks
```

### Get Account Info
```
Get info about my account
```

---

## CSPR TRANSFER COMMANDS

### Send CSPR
```
Send 5 CSPR to account account-hash-2bc76a5348a847ff51738945d681b97dda6ed606f7ae4282d1a0eb409ef301f5
```

### Send Multiple Transfers
```
Send 2 CSPR to account-hash-friend1
Send 3 CSPR to account-hash-friend2
```

---

## CONVERSATIONAL QUERIES

### Ask AI About Blockchain
```
What is Casper blockchain?
```

### Ask About NFTs
```
What's the difference between NFT Marketplace and Collection Factory?
```

### Ask About Metadata
```
How do metadata URIs work for collections?
```

### Get Help
```
How do I mint an NFT?
```

### Explain Concepts
```
Explain motes vs CSPR
```

---

## REAL EXAMPLES

### Example 1: Single Artist NFT
```
Mint an NFT with metadata URI ipfs://QmArtist2024/masterpiece.json to my account
```

**Expected:**
- Returns token_id (e.g., #15)
- Shows metadata_uri
- Transaction hash for verification
- NFT appears in Portfolio

---

### Example 2: Bulk Collection Drop
```
Create a collection called PixelPets2024 with symbol PPET,
base_uri ipfs://QmPixelPets2024/ and mint price 0,
then mint 50 NFTs to my account in that collection
```

**Expected:**
- Collection created with ID
- 50 NFTs minted with auto-generated URIs (0.json through 49.json)
- All transaction hashes listed
- ~1-2 minutes to finalize on blockchain

---

### Example 3: Premium NFT with Royalties
```
Create a collection called PremiumArt with symbol PAR,
base_uri ipfs://QmPremiumArt/ and mint price 10 CSPR,
then mint 1 NFT to my account
```

**Expected:**
- Collection created
- 1 NFT minted (will pay 10 CSPR mint price)
- Transaction shows payment to collection creator

---

### Example 4: Multi-Contract Management
```
First, deploy a token called GovernanceToken with symbol GOV,
decimals 18, total supply 10,000,000.
Then check the balance.
And list all my contracts.
```

**Expected:**
- Token deployed with contract hash
- Balance shown
- All deployed contracts listed
- AI remembers all 3 steps in one conversation

---

### Example 5: NFT Trading Flow
```
First tell me about NFT #2.
Then if the price looks good, I'll buy it for that amount.
After buying, show me that I'm the new owner.
```

**Expected:**
- NFT info shown (owner, price, metadata_uri)
- AI waits for confirmation
- Payment sent to current owner
- Ownership transferred
- Ownership verified

---

## PARAMETER FORMATS

### Account Hash
✅ Correct:
```
account-hash-2bc76a5348a847ff51738945d681b97dda6ed606f7ae4282d1a0eb409ef301f5
```

❌ Don't use:
```
2bc76a5348a847ff51738945d681b97dda6ed606f7ae4282d1a0eb409ef301f5
my-account
account-2bc76a53
```

### Metadata URI
✅ Correct:
```
ipfs://QmXYZ/nft.json
https://example.com/nft.json
ipfs://Qm1234567/collection/0.json
```

❌ Don't use:
```
QmXYZ/nft.json
ipfs://QmXYZ
nft.json
```

### Base URI (for Collections)
✅ Correct (ends with /):
```
ipfs://QmMyCollection/
ipfs://QmPets/
https://example.com/nfts/
```

❌ Don't use (no trailing /):
```
ipfs://QmMyCollection
ipfs://QmPets
```

### Amounts (CSPR)
✅ Correct:
```
0 (free)
1 (1 CSPR)
5.5 (5.5 CSPR)
100 (100 CSPR)
```

❌ Don't use (motes - AI converts):
```
1000000000 (let AI handle conversion)
50000000000
```

### Token ID
✅ Correct:
```
0 (first NFT/token)
5 (sixth NFT/token)
99 (hundredth NFT)
```

❌ Don't use:
```
#5 (no hash)
token-5
nft_5
```

### Collection ID
✅ Correct:
```
0 (first collection)
1 (second collection)
```

❌ Don't use:
```
CyberPunks (use name, AI finds ID from context)
MyCollection
```

---

## SHORTCUTS IN CHAT

### If AI asks "Which collection?"
Say: "The one I just created" or "CyberPunks" or "Collection 0"

### If AI asks for missing parameter
Provide: Just the missing value, not entire command

### If transaction fails
Ask: "Why did it fail?" (AI will explain)

### If you want to verify
Say: "Verify that transaction" or "Verify the last transaction"

---

## COMMON WORKFLOWS

### Workflow 1: Launch Your First NFT (5 min)
1. "Mint an NFT with metadata URI ipfs://QmTest/1.json"
2. Wait for transaction
3. Go to Portfolio → NFTs
4. ✅ Done!

### Workflow 2: Create NFT Series (20 min)
1. "Create a collection called MySeries with symbol MS, base_uri ipfs://QmSeries/ and mint price 0"
2. (Get collection_id)
3. "Mint 10 NFTs to me in MySeries"
4. Wait ~1 minute
5. Go to Portfolio → Collections
6. ✅ All 10 appear!

### Workflow 3: Launch Paid Collection (30 min)
1. Prepare 20 metadata JSONs (0.json through 19.json)
2. Upload to IPFS (get base_uri)
3. "Create collection Premium with symbol PREM, base_uri ipfs://QmYourHash/ and mint price 2 CSPR"
4. "Mint 20 NFTs in Premium"
5. Wait ~2-3 minutes
6. Verify in Portfolio
7. ✅ Collection live with 20 NFTs!

### Workflow 4: NFT Trading Simulation
1. "Mint an NFT with ipfs://QmTest/rare.json"
2. "List it for 100 CSPR"
3. (Other user buys it)
4. "Who owns NFT #0 now?"
5. ✅ Ownership transferred!

### Workflow 5: Token Airdrop
1. "Deploy a token called CommunityToken with symbol COM, decimals 8, supply 1000000"
2. "Transfer 10000 to account account-hash-friend1"
3. "Transfer 10000 to account account-hash-friend2"
4. "Show me my balance of token 0"
5. ✅ Tokens distributed!

---

## TROUBLESHOOTING COMMANDS

### If NFT doesn't appear after mint
```
Check portfolio for NFT #0
```

### If transaction seems stuck
```
Verify transaction 0x...
```

### If you need collection ID
```
List all collections
```

### If you don't know an NFT's details
```
Get info about NFT #5
```

### If you forget your balance
```
What's my CSPR balance?
```

---

## TIPS & TRICKS

1. **Type naturally** - "Create a collection called..." works just fine
2. **AI remembers** - Don't repeat collection info in follow-up message
3. **Copy-paste hashes** - Use transaction hashes for verification
4. **Check portfolio** - Fastest way to verify ownership
5. **Save output** - Screenshot transaction hashes for records
6. **IPFS first** - Upload metadata to IPFS before creating collection
7. **Test with 0 price** - Use free collections before paid ones
8. **Use devnet** - Always test on testnet before mainnet

---

**Last Updated:** 2026-07-05
