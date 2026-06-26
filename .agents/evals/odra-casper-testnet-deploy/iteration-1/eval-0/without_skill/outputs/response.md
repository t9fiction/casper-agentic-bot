# Deploying Odra Greeter Contract to Casper Testnet

Below is a step-by-step walkthrough. All commands use Casper 2.0's `put-transaction` (the old `put-deploy` is deprecated).

---

## Prerequisites

Ensure you have:

- `casper-client` installed (`cargo install casper-client`)
- Your compiled wasm: `smart-contract/wasm/Greeter.wasm`
- Your secret key: `secret_key.pem`
- A funded testnet account (get CSPR from the [Casper Testnet Faucet](https://testnet.cspr.live/faucet))
- Node access: `http://65.109.115.124:7777`

---

## Step 1: Export Environment Variables

```bash
export NODE=http://65.109.115.124:7777
export CHAIN_NAME=casper-test
export WASM=smart-contract/wasm/Greeter.wasm
export KEY=secret_key.pem
```

---

## Step 2: Get Your Account Hash

```bash
casper-client account-address --public-key <(casper-client key-file-to-public-key --secret-key $KEY)
```

Or if you already know your account hash (from the secret key), you can derive it:

```bash
casper-client key-file-to-account-address --secret-key $KEY
```

Export it:

```bash
export ACCOUNT_HASH=account-hash-<YOUR_ACCOUNT_HASH>
```

---

## Step 3: Check Your Account Balance

```bash
casper-client get-balance \
    --node-address $NODE \
    --purse-uref "$(casper-client query-global-state \
        --node-address $NODE \
        --key $ACCOUNT_HASH \
        | jq -r '.result.stored_value.Account.main_purse')"
```

You need at least ~500 CSPR for deployment.

---

## Step 4: Deploy the Contract (Install-Upgrade)

This uses `put-transaction session` with the `--install-upgrade` flag. Odra requires several named configuration arguments.

```bash
casper-client put-transaction session \
    --node-address $NODE \
    --chain-name $CHAIN_NAME \
    --secret-key $KEY \
    --session-path $WASM \
    --session-arg "odra_cfg_package_hash_key_name:string='greeter'" \
    --session-arg "odra_cfg_allow_key_override:bool='true'" \
    --session-arg "odra_cfg_is_upgradable:bool='true'" \
    --session-arg "odra_cfg_is_upgrade:bool='false'" \
    --payment-amount 500000000000 \
    --standard-payment true \
    --gas-price-tolerance 1
```

### Explanation of Odra-specific args:

| Arg | Value | Purpose |
|---|---|---|
| `odra_cfg_package_hash_key_name` | `'greeter'` | Named key under your account that will store the contract package hash |
| `odra_cfg_allow_key_override` | `'true'` | Allows the named key to be set (needed on first deploy) |
| `odra_cfg_is_upgradable` | `'true'` | Makes this contract upgradable later |
| `odra_cfg_is_upgrade` | `'false'` | Set to `'false'` for first-time install; use `'true'` on subsequent upgrades |
| `payment-amount` | `500000000000` | 500 CSPR in motes (10^9 motes = 1 CSPR). The wasm (~280KB) consumed ~231 CSPR in a real deploy |

If your wasm has **init args** (e.g., a default greeting), add them here too. For example, if your `Greeter` has an `init` entry point that takes a `greeting` string:

```bash
    --session-arg "greeting:string='Hello from Odra!'"
```

---

## Step 5: Verify the Deploy Was Accepted

The command in Step 4 will return a **deploy hash**. Save it:

```bash
export DEPLOY_HASH=<deploy_hash_from_output>
```

Wait ~30-60 seconds for finalization, then check status:

```bash
casper-client get-transaction \
    --node-address $NODE \
    $DEPLOY_HASH
```

Look for `"execution_result": { "Success": ... }` — if you see `"error_message": null`, the deploy succeeded.

---

## Step 6: Verify Contract Was Installed

Check that the named key exists on your account:

```bash
casper-client query-global-state \
    --node-address $NODE \
    --key $ACCOUNT_HASH \
    -q "greeter"
```

You should see a `ContractPackage` with your package hash.

Query the contract entity directly:

```bash
casper-client query-global-state \
    --node-address $NODE \
    --key <contract_hash_returned_above>
```

This will list all entry points (`init`, `get_greeting`, `set_greeting`, `greet`, `get_greet_count`).

---

## Step 7: Export Contract Hashes for Interaction

```bash
export PACKAGE=hash-<contract_package_hash_from_step_6>
export CONTRACT=hash-<contract_hash_from_step_6>
```

---

## Step 8: Call Read Entry Point (get_greeting)

```bash
casper-client put-transaction package \
    --node-address $NODE \
    --chain-name $CHAIN_NAME \
    --secret-key $KEY \
    --contract-package-hash $PACKAGE \
    --session-entry-point get_greeting \
    --payment-amount 5000000000 \
    --standard-payment true \
    --gas-price-tolerance 1
```

Check the transaction result for `"error_message": null`.

---

## Step 9: Call Write Entry Point (set_greeting)

```bash
casper-client put-transaction package \
    --node-address $NODE \
    --chain-name $CHAIN_NAME \
    --secret-key $KEY \
    --contract-package-hash $PACKAGE \
    --session-entry-point set_greeting \
    --session-arg "greeting:string='GM Casper!'" \
    --payment-amount 5000000000 \
    --standard-payment true \
    --gas-price-tolerance 1
```

---

## Step 10: Call greet (returns greeting + increments counter)

```bash
casper-client put-transaction package \
    --node-address $NODE \
    --chain-name $CHAIN_NAME \
    --secret-key $KEY \
    --contract-package-hash $PACKAGE \
    --session-entry-point greet \
    --payment-amount 5000000000 \
    --standard-payment true \
    --gas-price-tolerance 1
```

---

## Troubleshooting

| Error | Likely Cause | Fix |
|---|---|---|
| `MissingArg` (64658) | Odra's `call()` expects named config args | Pass all 4 `odra_cfg_*` args |
| `CannotOverrideKeys` (64641) | Named key already exists | Set `odra_cfg_allow_key_override:bool='true'` |
| Out of gas | Wasm too large for default payment | Increase `--payment-amount` to `500000000000` (500 CSPR) |
| `-32602` on query | Wrong key prefix | Use `hash-` not `contract-` for state queries in Casper 2.0 |

---

## Quick Reference — All Commands in One Block

```bash
# 1. Env vars
export NODE=http://65.109.115.124:7777
export CHAIN_NAME=casper-test
export WASM=smart-contract/wasm/Greeter.wasm
export KEY=secret_key.pem
export ACCOUNT_HASH=$(casper-client key-file-to-account-address --secret-key $KEY)

# 2. Deploy
casper-client put-transaction session \
    --node-address $NODE \
    --chain-name $CHAIN_NAME \
    --secret-key $KEY \
    --session-path $WASM \
    --session-arg "odra_cfg_package_hash_key_name:string='greeter'" \
    --session-arg "odra_cfg_allow_key_override:bool='true'" \
    --session-arg "odra_cfg_is_upgradable:bool='true'" \
    --session-arg "odra_cfg_is_upgrade:bool='false'" \
    --payment-amount 500000000000 \
    --standard-payment true \
    --gas-price-tolerance 1

# 3. Check success (replace <DEPLOY_HASH>)
casper-client get-transaction --node-address $NODE <DEPLOY_HASH>
```
