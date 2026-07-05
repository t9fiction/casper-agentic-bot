# 🏗️ AI CHATBOT ARCHITECTURE & PROCESSING GUIDE

**Updated: 2026-07-05**

This document explains how the AI chatbot processes commands internally and what happens at each step.

---

## SYSTEM ARCHITECTURE OVERVIEW

```
┌─────────────────────────────────────────────────────────────────┐
│                      FRONTEND (index.html)                       │
│  • Chat input box                                               │
│  • Message display                                              │
│  • 5 Modals: NFT Marketplace, Collection Factory, etc.         │
│  • Wallet connection                                            │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                    POST /api/chat
                   (user message)
                              │
                              ▼
        ┌─────────────────────────────────────────────┐
        │      src/main.py (FastAPI Backend)          │
        │  • Receives chat message                    │
        │  • Routes to run_agent()                    │
        └─────────────────┬───────────────────────────┘
                          │
                          ▼
        ┌─────────────────────────────────────────────┐
        │   src/agent.py (LangGraph Agent)            │
        │  • build_agent() creates AI with tools      │
        │  • run_agent() executes with memory         │
        │  • System prompt defines all capabilities   │
        └─────────────────┬───────────────────────────┘
                          │
         ┌────────────────┼────────────────┐
         │                │                │
         ▼                ▼                ▼
    Query        Contract Call    Transfer CSPR
    Blockchain   Entry Points      Tools
         │                │                │
         └────────────────┼────────────────┘
                          │
                          ▼
        ┌─────────────────────────────────────────────┐
        │   src/mcp_client.py (MCP Connection)        │
        │  • Calls blockchain tools via CSPR.cloud    │
        │  • 87+ tools available                       │
        │  • Converts responses to readable format     │
        └─────────────────┬───────────────────────────┘
                          │
                          ▼
        ┌─────────────────────────────────────────────┐
        │   Casper Blockchain (Testnet)               │
        │  • Token Factory Contract                   │
        │  • NFT Marketplace Contract                 │
        │  • Collection Factory Contract              │
        │  • Smart contract execution                 │
        └─────────────────────────────────────────────┘
```

---

## MESSAGE FLOW: User Types a Command

### Example: User says "Mint an NFT with metadata URI ipfs://QmTest/nft.json"

### 1. FRONTEND CAPTURES INPUT

**File:** `src/public/index.html` (lines 200-300)

```javascript
// User types in chat box and clicks Send
messageInput.addEventListener('keypress', async (e) => {
  if (e.key === 'Enter') {
    const userMessage = messageInput.value.trim();

    // Send to backend
    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: userMessage,
        session_id: 'default'  // Enables conversation memory
      })
    });

    const data = await response.json();
    displayMessage(userMessage, 'user');
    displayMessage(data.reply, 'assistant');
  }
});
```

**What happens:**
- Message: "Mint an NFT with metadata URI ipfs://QmTest/nft.json"
- Sent to `/api/chat` endpoint with session_id="default"
- Session ID enables AI to remember previous messages

---

### 2. BACKEND RECEIVES MESSAGE

**File:** `src/main.py` (lines 42-50)

```python
@app.post("/api/chat")
async def chat(req: ChatRequest):
    if not req.message.strip():
        return JSONResponse({"error": "Message is required"}, status_code=400)
    try:
        # Pass to agent with session_id for memory
        reply = await run_agent(req.message, session_id=req.session_id)
        return {"reply": reply}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
```

**What happens:**
- Request validated (not empty)
- Routed to `run_agent()` function
- Session ID passed to maintain conversation history

---

### 3. AGENT LOADS CONVERSATION HISTORY

**File:** `src/agent.py` (lines 218-242)

```python
async def run_agent(user_input: str, session_id: str = "default"):
    from .conversation import get_conversation

    # Get the conversation session (creates if doesn't exist)
    conv = get_conversation(session_id)

    # Add user's message to history
    conv.add_message("user", user_input)

    # Build agent with all tools
    agent = await build_agent()

    # Get last 20 messages (context window, prevents explosion)
    messages = conv.get_last_n_messages(20)
```

**What happens:**
1. Gets or creates conversation session for this user
2. Adds current message to history
3. Builds agent with tools (NFT, token, blockchain tools)
4. Retrieves last 20 messages for context
5. This allows AI to remember previous collections, contract names, etc.

---

### 4. AGENT BUILDS WITH SYSTEM PROMPT

**File:** `src/agent.py` (lines 10-200)

```python
SYSTEM_PROMPT = """You are Casper Agentic Bot, an AI assistant for the Casper blockchain.

You have access to these tools:
- query_casper_blockchain: Get blockchain info
- send_cspr_transfer: Send CSPR tokens
- call_contract_entry_point: Call smart contract functions
- deploy_contract: Deploy new contracts
- verify_contract_deployment: Check deployment status

NFT MARKETPLACE CONTRACT: Available entry points:
- mint_nft(metadata_uri, recipient) → mints NFT
- transfer_nft(token_id, recipient)
- list_nft(token_id, price)
- buy_nft(token_id, buyer)
- nft_info(token_id)

COLLECTION FACTORY CONTRACT: Available entry points:
- create_collection(name, symbol, base_uri, mint_price)
- mint_nft(collection_id, recipient) → auto-generates URI
- collection_info(collection_id)
- total_collections()

Rules:
1. Validate inputs before calling tools
2. Convert CSPR to motes: multiply by 1_000_000_000
3. For metadata URI, use the exact format provided
4. Always display transaction hashes
5. For collections, base_uri must end with /
"""

async def build_agent():
    tools_desc = await _get_tools_description()
    system_prompt = SYSTEM_PROMPT.format(
        network=NETWORK,
        tools_description=tools_desc
    )

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
    tools = [
        query_casper_blockchain,
        send_cspr_transfer,
        analyze_account,
        call_contract_entry_point,
        deploy_contract,
        verify_contract_deployment,
        list_deployed_contracts
    ]

    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt=SystemMessage(content=system_prompt)
    )
    return agent
```

**What happens:**
- Agent is built with GPT-4o-mini model (fast, efficient)
- Temperature=0.3 (low randomness, consistent responses)
- All 7 tools attached to agent
- System prompt injected with all contract details
- Agent can now make intelligent decisions about which tool to use

---

### 5. AI PROCESSES THE MESSAGE

**Internally (LangGraph):**

```
User Input: "Mint an NFT with metadata URI ipfs://QmTest/nft.json"

AI Processing:
1. Parse the request
   → Identify: "mint" action
   → Identify: "NFT Marketplace" (not Collection)
   → Identify: explicit metadata_uri provided
   → Identify: no explicit recipient (use connected wallet)

2. Validate inputs
   ✓ metadata_uri = "ipfs://QmTest/nft.json" (valid format)
   ✓ recipient = auto-filled from wallet (valid account-hash)
   ✓ All required parameters present

3. Choose tool to use
   → Need to call smart contract
   → Use: call_contract_entry_point

4. Build the tool call
   → entry_point = "mint_nft"
   → contract_name = "nft_marketplace" (default)
   → session_args = {
        "metadata_uri": "ipfs://QmTest/nft.json",
        "recipient": "account-hash-2bc76a5348a847ff51738945d681b97dda6ed606f7ae4282d1a0eb409ef301f5"
      }

5. Execute tool call
   → Send request to MCP client
   → Blockchain processes transaction
   → Returns: {
        "token_id": 5,
        "transaction_hash": "0x1234567890abcdef",
        "owner": "account-hash-...",
        "metadata_uri": "ipfs://QmTest/nft.json"
      }

6. Format response for user
   → Extract transaction_hash
   → Extract token_id
   → Show clear success message
   → Remind user about 30-second wait time
```

---

### 6. TOOL EXECUTION: call_contract_entry_point

**File:** `src/tools.py` (MCP wrapper)

```python
async def call_contract_entry_point(
    entry_point: str,
    session_args: dict = None,
    contract_name: str = None
):
    """
    Call a smart contract entry point via MCP.

    Args:
        entry_point: Name of function (e.g., "mint_nft")
        session_args: Arguments for the function (JSON)
        contract_name: Which contract ("collections", "nft_marketplace", etc.)

    Returns:
        Tool response with transaction hash
    """
    mcp = get_mcp_client()

    # Build tool call
    tool_call = {
        "name": "call_contract_entry_point",
        "args": {
            "entry_point": entry_point,
            "session_args": json.dumps(session_args or {}),
            "contract_name": contract_name or "nft_marketplace"
        }
    }

    # Execute via MCP
    response = await mcp.call_tool("call_contract_entry_point", tool_call["args"])
    return response
```

**What happens:**
1. Tool validates entry_point exists
2. Converts session_args to JSON
3. Calls MCP with correct contract name
4. MCP forwards to CSPR.cloud blockchain API
5. Returns transaction response

---

### 7. BLOCKCHAIN EXECUTION

**On Casper Network:**

```
Smart Contract (NFT Marketplace):

function mint_nft(metadata_uri: String, recipient: AccountHash) {
    // Generate unique token_id
    token_id = next_token_id();  // e.g., 5

    // Create NFT structure
    let nft = NFT {
        token_id: 5,
        owner: recipient,
        creator: sender,  // AI's account
        metadata_uri: "ipfs://QmTest/nft.json",
        listed: false,
        price: 0
    };

    // Store NFT
    nfts[5] = nft;
    balances[recipient]++;

    // Return transaction hash
    return {
        transaction_hash: "0x1234567890abcdef",
        token_id: 5,
        owner: recipient,
        metadata_uri: "ipfs://QmTest/nft.json"
    };
}
```

**Block finalization:**
- Transaction enters pending pool
- Validators process and execute
- ~30 seconds later: in finalized block
- Portfolio API picks it up on next refresh

---

### 8. AI FORMATS RESPONSE

**File:** `src/agent.py` (lines 240-280)

```python
try:
    # Invoke agent with conversation messages
    result = await agent.ainvoke({"messages": messages})
    response_messages = result.get("messages", [])

    # Extract assistant's final response
    assistant_response = None
    for msg in response_messages:
        if msg.type == "ai":
            assistant_response = msg.content
            break

    # Add to conversation history
    conv.add_message("assistant", assistant_response)

    # Return to frontend
    return assistant_response

except Exception as e:
    return f"Error: {str(e)}"
```

**AI's Response Format:**

```
✅ NFT Minted Successfully!

📊 Details:
   Token ID: 5
   Owner: account-hash-2bc76a5348a847ff51738945d681b97dda6ed606f7ae4282d1a0eb409ef301f5
   Metadata URI: ipfs://QmTest/nft.json

🔗 Transaction Hash: 0x1234567890abcdef
⏳ The blockchain will finalize this in ~30 seconds.

💡 Your NFT will appear in Portfolio → 🖼️ NFTs shortly.
```

---

### 9. FRONTEND DISPLAYS RESPONSE

**File:** `src/public/index.html`

```javascript
function displayMessage(text, sender) {
  const msgDiv = document.createElement('div');
  msgDiv.className = sender === 'user' ? 'message user-message' : 'message assistant-message';
  msgDiv.innerHTML = escapeHtml(text);
  messagesContainer.appendChild(msgDiv);
  messagesContainer.scrollTop = messagesContainer.scrollHeight;
}
```

**User sees:**
- Message appears in chat
- Can see transaction hash to verify
- Link to portfolio to check later

---

## CONVERSATION MEMORY: How AI Remembers

### Example: Create Collection + Mint NFTs

**Message 1:**
```
User: "Create a collection called Pets with base_uri ipfs://Pets/ and mint price 0"

AI Processing:
1. Calls create_collection
2. Gets back: collection_id = 0
3. Stores in conversation history:
   "Collection created: name='Pets', id=0, base_uri='ipfs://Pets/'"

AI Response:
"✅ Collection Pets created (ID: 0)"
```

**Message 2:**
```
User: "Now mint 3 NFTs in that collection"

AI Processing:
1. Reads conversation history (previous 20 messages)
2. Finds: "Collection created: name='Pets', id=0"
3. Extracts: collection_id = 0
4. Calls mint_nft 3 times with collection_id=0
5. Each auto-generates: ipfs://Pets/0.json, ipfs://Pets/1.json, ipfs://Pets/2.json

AI Response:
"✅ 3 NFTs minted in Pets collection
   NFT #0: ipfs://Pets/0.json
   NFT #1: ipfs://Pets/1.json
   NFT #2: ipfs://Pets/2.json"
```

**File:** `src/conversation.py`

```python
class Conversation:
    def __init__(self, session_id):
        self.session_id = session_id
        self.messages = []  # List of Message objects

    def add_message(self, role, content):
        """Add message to history"""
        msg = Message(role=role, content=content, timestamp=now())
        self.messages.append(msg)

    def get_last_n_messages(self, n=20):
        """Get last N messages for context"""
        return self.messages[-n:]

    def summary(self):
        """Get conversation summary (contracts, collections created)"""
        summary = []
        for msg in self.messages:
            if "collection" in msg.content.lower():
                summary.append(f"Collection: {msg.content}")
            if "deployed" in msg.content.lower():
                summary.append(f"Deploy: {msg.content}")
        return summary
```

---

## HOW AI HANDLES DIFFERENT SCENARIOS

### Scenario 1: Collection Not Specified

```
User: "Mint 5 NFTs"
↓
AI Processing:
1. Check conversation history
2. Look for: "Collection created: ..."
3. If found → use that collection_id
4. If NOT found → ask user:
   "Which collection? Options:
   - Use an existing collection (provide ID)
   - Create a new collection first"

AI Response:
"I can mint NFTs, but I need to know which collection.
Could you provide:
1. An existing collection ID, OR
2. Collection name (if you already created one)

Or would you like to create a new collection first?"
```

### Scenario 2: Missing Required Parameters

```
User: "Create a collection"
↓
AI Processing:
1. Entry point requires: name, symbol, base_uri, mint_price
2. User provided: NONE
3. Cannot proceed without these

AI Response:
"I'd love to create a collection! I need some details:

1. **Name** - What should it be called? (e.g., "Pets")
2. **Symbol** - 2-4 letter symbol (e.g., "PET")
3. **Base URI** - IPFS path (e.g., "ipfs://QmXYZ/")
4. **Mint Price** - Cost per NFT in CSPR (e.g., "1" or "0" for free)

Provide these and I'll create it!"
```

### Scenario 3: Multi-Step Workflow

```
User: "Create collection CyberPunks with base_uri ipfs://CP/ and mint 100"
↓
AI Processing:
1. Step 1: Create collection
   - Call: create_collection(name="CyberPunks", ...)
   - Get: collection_id = 0

2. Step 2-101: Mint 100 NFTs
   - Loop 100 times:
     - Call: mint_nft(collection_id=0, recipient=your_account)
     - Get: token_id 0, 1, 2, ..., 99
     - Auto-generate: ipfs://CP/0.json through ipfs://CP/99.json

3. Collect results and respond

AI Response:
"✅ Collection created (ID: 0)
✅ 100 NFTs minted!
   - Token IDs: 0-99
   - URIs: ipfs://CP/0.json through ipfs://CP/99.json
   - Transactions: 100 hashes shown

⏳ Finalizing on blockchain (~2 minutes for 100 txs)
📊 Check Portfolio → Collections → CyberPunks"
```

---

## PARAMETER TYPES & CONVERSIONS

### String Parameters (No Conversion)

```
metadata_uri: "ipfs://QmXYZ/nft.json"
  → Passed as-is to contract
  → No validation (trust user)

name: "CyberPunks"
  → Passed as-is
  → 1-256 characters

symbol: "CYBR"
  → Passed as-is
  → Typically 2-4 chars

base_uri: "ipfs://QmXYZ/"
  → Must end with /
  → AI can validate this
```

### Numeric Parameters (Conversion)

```
mint_price (user input): "10 CSPR"
  → Parse: extract "10"
  → Convert: 10 * 1_000_000_000
  → Result: "10000000000 motes"
  → Pass to contract: "10000000000"

list_price: "50" (CSPR)
  → Convert: 50 * 1_000_000_000
  → Pass to contract: "50000000000"

token_id: "5"
  → No conversion (already correct format)
  → Pass as-is: "5"
```

---

## ERROR HANDLING IN AI

### Tool Execution Fails

```
User: "Mint NFT"
↓
AI calls: call_contract_entry_point(...)
↓
MCP returns: Error: "Invalid metadata URI"
↓
AI Response:
"❌ Failed to mint NFT

Reason: Invalid metadata URI format

The URI should be in this format:
✓ ipfs://QmXYZ/file.json
✓ https://example.com/nft.json

What metadata URI would you like to use?"
```

### Insufficient Parameters

```
User: "List this NFT for sale"
↓
AI checks: token_id = MISSING, price = MISSING
↓
AI doesn't call contract
↓
AI Response:
"I can list an NFT for sale! I need:

1. **Token ID** - Which NFT? (e.g., "5")
2. **Price** - How much in CSPR? (e.g., "50")

Please provide these details!"
```

### Insufficient Funds (Post-Execution)

```
User: "Mint NFT for 10 CSPR in PaidCollection"
↓
AI calls: mint_nft + send_cspr_transfer
↓
Blockchain returns: "Insufficient CSPR balance"
↓
AI Response:
"❌ Transaction failed: Insufficient CSPR

Your balance: 0.5 CSPR
Mint price: 10 CSPR
Shortfall: 9.5 CSPR

Please add CSPR to your account first!"
```

---

## TOOL INVOCATION PATTERNS

### Single Tool Call

```python
# Simple case: Just mint an NFT
await call_contract_entry_point(
    entry_point="mint_nft",
    session_args={
        "metadata_uri": "ipfs://QmTest/nft.json",
        "recipient": "account-hash-..."
    }
)
```

### Sequential Tool Calls (Multi-Step)

```python
# Step 1: Create collection
result1 = await call_contract_entry_point(
    entry_point="create_collection",
    session_args={
        "name": "Pets",
        "symbol": "PET",
        "base_uri": "ipfs://Pets/",
        "mint_price": "0"
    },
    contract_name="collections"
)
collection_id = result1["collection_id"]

# Step 2: Mint using the collection_id from step 1
for i in range(3):
    result = await call_contract_entry_point(
        entry_point="mint_nft",
        session_args={
            "collection_id": collection_id,
            "recipient": "account-hash-..."
        },
        contract_name="collections"
    )
    print(f"Minted NFT {i}: {result['token_id']}")
```

### Conditional Tool Calls

```python
# Check if collection exists first
result = await call_contract_entry_point(
    entry_point="collection_info",
    session_args={"collection_id": 0},
    contract_name="collections"
)

if result["error"]:
    # Collection doesn't exist, create it
    create_result = await call_contract_entry_point(
        entry_point="create_collection",
        session_args={...}
    )
else:
    # Collection exists, use it
    mint_result = await call_contract_entry_point(
        entry_point="mint_nft",
        session_args={...}
    )
```

---

## KEY FILES REFERENCE

| File | Role | Key Lines |
|------|------|-----------|
| `src/public/index.html` | Frontend chat UI | 1-1300 |
| `src/main.py` | Backend API endpoint | 42-50 |
| `src/agent.py` | AI system & prompts | 10-200 |
| `src/tools.py` | Tool implementations | Various |
| `src/mcp_client.py` | MCP client wrapper | Handles API calls |
| `src/conversation.py` | Session memory | Stores history |
| Smart Contracts | On-chain execution | Casper network |

---

## COMPLETE FLOW DIAGRAM

```
┌─ User Types Message ─┐
│  "Mint 3 NFTs in    │
│   my collection"    │
└──────────┬──────────┘
           │
           ▼
    ┌─────────────┐
    │ Frontend    │
    │ index.html  │
    └──────┬──────┘
           │ POST /api/chat
           │ {message, session_id}
           │
           ▼
    ┌──────────────┐
    │ main.py      │
    │ chat endpoint│
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │ agent.py     │
    │ run_agent()  │
    └──────┬───────┘
           │
           ├─ Load conversation (get_conversation)
           ├─ Get last 20 messages
           ├─ Build agent with system prompt
           │
           ▼
    ┌──────────────┐
    │ LangGraph    │
    │ Agent        │
    └──────┬───────┘
           │
           ├─ Parse: "Mint 3 NFTs in my collection"
           ├─ Lookup: Find collection_id from history
           ├─ Validate: Confirm recipient from wallet
           ├─ Choose tool: call_contract_entry_point
           │
           ▼
    ┌──────────────────┐
    │ Loop 3 times:    │
    │ call_contract_   │
    │ entry_point()    │
    └──────┬───────────┘
           │
           ├─ Call 1: mint_nft (collection_id, recipient)
           │  → Return: token_id=0, tx_hash=0x111
           │
           ├─ Call 2: mint_nft (collection_id, recipient)
           │  → Return: token_id=1, tx_hash=0x222
           │
           ├─ Call 3: mint_nft (collection_id, recipient)
           │  → Return: token_id=2, tx_hash=0x333
           │
           ▼
    ┌──────────────────┐
    │ mcp_client.py    │
    │ MCP API Calls    │
    └──────┬───────────┘
           │
           ▼
    ┌──────────────────┐
    │ Casper Blockchain│
    │ Network          │
    └──────┬───────────┘
           │
           ├─ Process NFT 0: owner=you, uri=ipfs://.../0.json
           ├─ Process NFT 1: owner=you, uri=ipfs://.../1.json
           ├─ Process NFT 2: owner=you, uri=ipfs://.../2.json
           │
           ▼
    ┌──────────────────┐
    │ Finalize ~30sec  │
    │ later            │
    └──────┬───────────┘
           │
           ▼
    ┌──────────────────────────────────────┐
    │ AI Formats Response:                 │
    │ ✅ 3 NFTs Minted!                    │
    │ Token IDs: 0, 1, 2                   │
    │ URIs: ipfs://.../0.json, ...         │
    │ Transactions: 0x111, 0x222, 0x333   │
    └──────┬───────────────────────────────┘
           │
           ▼
    ┌──────────────┐
    │ main.py      │
    │ Returns JSON │
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │ Frontend     │
    │ Displays msg │
    └──────────────┘
```

---

## SUMMARY

**The AI chatbot is a sophisticated system that:**
1. ✅ Listens to natural language commands
2. ✅ Loads conversation history to remember context
3. ✅ Validates inputs before execution
4. ✅ Converts units (CSPR ↔ motes)
5. ✅ Chains multiple blockchain operations
6. ✅ Handles errors gracefully
7. ✅ Tracks transaction hashes
8. ✅ Formats responses for user understanding

**For NFT operations specifically:**
- Can create collections with auto-generated URIs
- Can mint unlimited NFTs in parallel
- Can handle marketplace operations (buy, sell, transfer)
- Can track state across multiple messages
- Can guide users through complex workflows

**This enables users to manage entire NFT collections via simple chat commands!**
