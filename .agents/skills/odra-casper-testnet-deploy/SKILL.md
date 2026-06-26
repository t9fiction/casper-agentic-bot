---
name: odra-casper-testnet-deploy
description: "Deploy Odra smart contracts to Casper Testnet (protocol 2.0+) using the casper-client CLI. Covers WASM build with `cargo odra build`, deploy submission via `put-transaction session --install-upgrade` with Odra-required named args (`odra_cfg_package_hash_key_name`, `odra_cfg_allow_key_override`, `odra_cfg_is_upgradable`, `odra_cfg_is_upgrade`), calling entry points via `put-transaction package`, contract hash retrieval, and troubleshooting error codes 64658 (MissingArg), out-of-gas, and 64641 (CannotOverrideKeys). Use when deploying Odra contracts to Casper testnet, calling entry points, or debugging Odra deploy failures."
---

## Overview

Deploy Odra smart contracts to Casper Testnet using the `casper-client` CLI. This skill covers the full lifecycle: build WASM, deploy with all required Odra args, call entry points, and troubleshoot errors.

## Network Details

| Parameter | Testnet Value |
|---|---|
| Chain Name | `casper-test` |
| Node | `http://65.109.115.124:7777` (or `https://node.testnet.casper.network/rpc`) |
| Explorer | `https://testnet.cspr.live` |
| Faucet | `https://testnet.cspr.live/faucet` (browser required) |
| Protocol | 2.2.2 (as of June 2026) |
| Max Payment | `500000000000` motes (500 CSPR) — block gas limit |
| Payment (install) | `500000000000` motes (500 CSPR) — ~231 consumed for 280KB WASM |
| Payment (calls) | `5000000000` motes (5 CSPR) — plenty for entry point calls |

## Prerequisites

1. **Casper CLI client** — install from [docs.casper.network/developers/cli/setup](https://docs.casper.network/developers/cli/setup/)
2. **Odra** — `cargo install odra-cli`
3. **Rust** with `wasm32-unknown-unknown` target
4. **PEM key file** — Ed25519 or secp256r1 key for the deployer account
5. **CSPR test tokens** — at least 500 CSPR per contract deploy

## Step-by-Step

### 1. Build the Contract WASM

```bash
cd smart-contract
cargo odra build
```

The WASM output is at `smart-contract/wasm/<ContractName>.wasm`.

### 2. Set Environment Variables

```bash
export NODE=http://65.109.115.124:7777
export CHAIN=casper-test
export KEY=secret_key.pem
export WASM=smart-contract/wasm/Greeter.wasm
```

### 3. Deploy with `put-transaction session --install-upgrade`

**IMPORTANT:** Odra contracts require specific named args. The `call()` entrypoint that Odra generates expects these exact args:

```bash
casper-client put-transaction session \
    --node-address $NODE \
    --chain-name $CHAIN \
    --secret-key $KEY \
    --wasm-path $WASM \
    --payment-amount 500000000000 \
    --transferred-value 0 \
    --session-arg "odra_cfg_package_hash_key_name:string='<contract_name>'" \
    --session-arg "odra_cfg_allow_key_override:bool='false'" \
    --session-arg "odra_cfg_is_upgradable:bool='true'" \
    --session-arg "odra_cfg_is_upgrade:bool='false'" \
    --session-arg "<init_param_name>:<type>='<value>'" \
    --install-upgrade \
    --standard-payment true \
    --gas-price-tolerance 1
```

Replace:
- `<contract_name>` — the named key to store the package hash under (e.g., `greeter`)
- `<init_param_name>` — the init/constructor parameter name from your Odra contract (e.g., `greeting`)
- `<type>` — the CLType of the parameter (e.g., `string`)
- `<value>` — the parameter value (e.g., `'Hello World!'`)

### 4. Wait for Execution

```bash
casper-client get-transaction --node-address $NODE <TX_HASH>
```

Look for `"error_message": null` in the `execution_result.Version2` block.

### 5. Find the Contract Hash

```bash
casper-client query-global-state \
    --node-address $NODE \
    --key <ACCOUNT_HASH> \
    -q "<contract_name>"
```

The account hash is derived from your secret key. The result is a `ContractPackage`. To see entry points directly, query with `hash-<contract_hash_hex>`:

```bash
casper-client query-global-state \
    --node-address $NODE \
    --key hash-<contract_hash_hex>
```

**Note:** In Casper 2.0, use `hash-` prefix (NOT `contract-` prefix) for querying contracts.

### 6. Call Entry Points

Use `put-transaction package` with `--contract-package-hash`:

```bash
# Set these once
export PACKAGE=hash-<contract_package_hash_hex>

# Read entry point (no args)
casper-client put-transaction package \
    --node-address $NODE --chain-name $CHAIN \
    --secret-key $KEY \
    --contract-package-hash $PACKAGE \
    --session-entry-point <entry_point_name> \
    --payment-amount 5000000000 \
    --standard-payment true --gas-price-tolerance 1

# Write entry point (with args)
casper-client put-transaction package \
    --node-address $NODE --chain-name $CHAIN \
    --secret-key $KEY \
    --contract-package-hash $PACKAGE \
    --session-entry-point <entry_point_name> \
    --session-arg "<arg_name>:<type>='<value>'" \
    --payment-amount 5000000000 \
    --standard-payment true --gas-price-tolerance 1
```

## Troubleshooting

| Error | Discriminant | Meaning | Fix |
|---|---|---|---|
| `64658 (0xFC92)` | 122 | `MissingArg` — Odra's `call()` expects named args | Pass all Odra cfg args: `odra_cfg_package_hash_key_name`, `odra_cfg_allow_key_override`, `odra_cfg_is_upgradable`, `odra_cfg_is_upgrade`, plus init args |
| Out of gas | — | WASM too large for payment amount | Increase `--payment-amount` to 500 CSPR (500000000000 motes) |
| `64641 (0xFC81)` | 105 | `CannotOverrideKeys` — package hash key already exists | Set `odra_cfg_allow_key_override:bool='true'` |
| `-32602` | — | Invalid state query key format | Use `hash-` prefix for contracts (not `contract-`) in Casper 2.0 |
| `Invalid transaction` | — | Payment too low | Minimum payment for calls is ~2.5 CSPR (2500000000 motes). Use 5000000000. |
| `-32016` | — | Invalid transaction / payment | Transaction rejected on submission. Check balance, payment amount, and chain name. |

## Key Differences from Casper 1.x

- `put-deploy` is deprecated — use `put-transaction session` for installs and `put-transaction package` for entry point calls
- `--install-upgrade` flag is required for contract installation
- Contract queries use `hash-` prefix (not `contract-`)
- Execute results use `Version2` instead of `Success`/`Failure`
- No `--session-hash` flag — use `put-transaction package` with `--contract-package-hash` or `put-transaction invocable-entity` with `--entity-address`

## Useful Commands

**Check account balance:**
```bash
casper-client query-global-state \
    --node-address $NODE \
    --key $ACCOUNT_HASH \
    -q "balance"
```

**Get deploy details:**
```bash
casper-client get-transaction --node-address $NODE <TX_HASH>
```

**Query contract entry points:**
```bash
curl -s -H 'Content-Type: application/json' https://node.testnet.casper.network/rpc \
  -d '{"jsonrpc":"2.0","id":1,"method":"query_global_state","params":{"key":"hash-<contract_hash_hex>","path":[]}}'
```
