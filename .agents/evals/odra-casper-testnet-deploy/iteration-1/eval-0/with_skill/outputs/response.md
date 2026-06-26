# Deploying Odra Greeter to Casper Testnet — Step by Step

Based on your setup, here's the full walkthrough:

---

## 1. Set Environment Variables

```bash
export NODE=http://65.109.115.124:7777
export CHAIN=casper-test
export KEY=secret_key.pem
export WASM=smart-contract/wasm/Greeter.wasm
```

---

## 2. Deploy the Contract

This is the critical command. Odra's generated `call()` entrypoint **requires** four Odra configuration args plus your init argument:

```bash
casper-client put-transaction session \
    --node-address $NODE \
    --chain-name $CHAIN \
    --secret-key $KEY \
    --wasm-path $WASM \
    --payment-amount 500000000000 \
    --transferred-value 0 \
    --session-arg "odra_cfg_package_hash_key_name:string='greeter'" \
    --session-arg "odra_cfg_allow_key_override:bool='false'" \
    --session-arg "odra_cfg_is_upgradable:bool='true'" \
    --session-arg "odra_cfg_is_upgrade:bool='false'" \
    --session-arg "greeting:string='Hello World!'" \
    --install-upgrade \
    --standard-payment true \
    --gas-price-tolerance 1
```

Replace `'Hello World!'` with whatever initial greeting you want. If this is a **re-deploy** and the key `greeter` already exists, change `odra_cfg_allow_key_override:bool='false'` to `'true'`.

On success, the CLI prints a deploy hash. Save it as `$TX_HASH`.

---

## 3. Wait for Execution

```bash
casper-client get-transaction --node-address $NODE $TX_HASH
```

Look for `"error_message": null` inside the `execution_result.Version2` block. If you see an error, check the Troubleshooting section below.

---

## 4. Find the Contract Hash

Get your account hash from the secret key:

```bash
casper-client account-address --public-key <(casper-client key-to-public-key --secret-key $KEY 2>/dev/null)
```

Query the named key you used (`greeter`):

```bash
# Get account hash first
ACCOUNT_HASH=account-hash-<your_account_hash_here>
casper-client query-global-state \
    --node-address $NODE \
    --key $ACCOUNT_HASH \
    -q "greeter"
```

This returns the `ContractPackage`. Note the `contract_hash_hex` (without prefix). Then query the contract entity directly to see entry points:

```bash
casper-client query-global-state \
    --node-address $NODE \
    --key hash-<contract_hash_hex>
```

**Important:** Use the `hash-` prefix, NOT `contract-` (that's a Casper 2.0 change).

---

## 5. Save the Package Hash

```bash
export PACKAGE=hash-<contract_package_hash_hex>
```

You'll find the package hash in the output from step 4 — it's the top-level key under the `ContractPackage`.

---

## 6. Call Entry Points

Once deployed, you can interact with the contract.

**Read** — `get_greeting` (no args):

```bash
casper-client put-transaction package \
    --node-address $NODE --chain-name $CHAIN \
    --secret-key $KEY \
    --contract-package-hash $PACKAGE \
    --session-entry-point get_greeting \
    --payment-amount 5000000000 \
    --standard-payment true --gas-price-tolerance 1
```

**Write** — `set_greeting` (with arg):

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

**Call** — `greet` (no args, returns "Hello, {greeting}!" and increments counter):

```bash
casper-client put-transaction package \
    --node-address $NODE --chain-name $CHAIN \
    --secret-key $KEY \
    --contract-package-hash $PACKAGE \
    --session-entry-point greet \
    --payment-amount 5000000000 \
    --standard-payment true --gas-price-tolerance 1
```

Use `casper-client get-transaction --node-address $NODE <TX_HASH>` to check results for each call.

---

## Troubleshooting Common Errors

| Error | Likely Cause | Fix |
|---|---|---|
| `64658 (0xFC92)` — MissingArg | Odra cfg args not passed | Add all four `odra_cfg_*` args plus init args |
| Out of gas | WASM too large | Use `--payment-amount 500000000000` (500 CSPR) |
| `64641 (0xFC81)` — CannotOverrideKeys | Named key `greeter` already exists on account | Set `odra_cfg_allow_key_override:bool='true'` |
| `-32602` — Invalid query | Wrong key prefix | Use `hash-` prefix, never `contract-` |
| `Invalid transaction` | Payment too low | Minimum ~2.5 CSPR for calls; use `5000000000` motes |
