# Odra Contract Deploy Error 64658 — Fix

## Problem

Error code **64658 (0xFC92)** with discriminant 122 = **`MissingArg`** — Odra's `call()` function expects specific named configuration arguments that are missing from your `put-transaction session` command.

Your command also uses `--payment-amount 100000000000` (100 CSPR), which is too low. The ~280KB Greeter wasm consumes ~231 CSPR, so the transaction will run out of gas.

## Fix

Add the four required Odra configuration args and increase the payment amount.

### Correct Command

```bash
casper-client put-transaction session \
  --node-address http://65.109.115.124:7777 \
  --chain-name casper-test \
  --secret-key secret_key.pem \
  --wasm-path Greeter.wasm \
  --payment-amount 500000000000 \
  --standard-payment true --gas-price-tolerance 1 \
  --session-arg "odra_cfg_package_hash_key_name:string='greeter'" \
  --session-arg "odra_cfg_allow_key_override:bool='true'" \
  --session-arg "odra_cfg_is_upgradable:bool='true'" \
  --session-arg "odra_cfg_is_upgrade:bool='false'"
```

### Required Args Explained

| Argument | Purpose |
|---|---|
| `odra_cfg_package_hash_key_name` | Named key to store the contract package hash under (e.g. `'greeter'`) |
| `odra_cfg_allow_key_override` | Allow reusing an existing key (`true` for fresh deploys) |
| `odra_cfg_is_upgradable` | Whether the contract can be upgraded later |
| `odra_cfg_is_upgrade` | `false` for first-time install; `true` for upgrades |

### Additional Notes

- If this is **not** the first deploy (you already deployed and got error), set `odra_cfg_allow_key_override:bool='true'` to avoid `CannotOverrideKeys` (error 64641).
- Increase `--payment-amount` to **500 CSPR** (`500000000000` motes) — the 280KB wasm needs ~231 CSPR.
- After successful deploy, query named keys to find the contract package hash:
  ```bash
  casper-client query-global-state \
    --node-address http://65.109.115.124:7777 \
    --key account-hash-<YOUR_ACCOUNT_HASH> \
    -q "greeter"
  ```
