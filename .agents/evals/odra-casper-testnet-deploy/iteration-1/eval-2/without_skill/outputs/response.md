First, set up your env vars:

```bash
export NODE=http://65.109.115.124:7777
export CHAIN=casper-test
export PACKAGE=hash-ac102e24f6dc92e7e3b098f2af114817a67b62fe35764813854057a0859571f4
export KEY=secret_key.pem
```

(Note: package hash in `put-transaction` uses `hash-` prefix, not `contract-package-`.)

### 1. Call `get_greeting`

```bash
casper-client put-transaction package \
    --node-address $NODE --chain-name $CHAIN \
    --secret-key $KEY \
    --contract-package-hash $PACKAGE \
    --session-entry-point get_greeting \
    --payment-amount 5000000000 \
    --standard-payment true --gas-price-tolerance 1
```

### 2. Call `set_greeting` (write "GM Casper!")

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

### 3. Call `greet`

```bash
casper-client put-transaction package \
    --node-address $NODE --chain-name $CHAIN \
    --secret-key $KEY \
    --contract-package-hash $PACKAGE \
    --session-entry-point greet \
    --payment-amount 5000000000 \
    --standard-payment true --gas-price-tolerance 1
```

After each, check the result with:

```bash
casper-client get-transaction --node-address $NODE <TX_HASH>
```

**Note:** `get_greeting` and `greet` are read-like entry points but still use `put-transaction` (Casper 2.0 has no separate query entry point for session entry-point calls). The state changes are visible in the execution result.
