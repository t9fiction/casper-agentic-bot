Based on the skill's section 6, here are the commands using `put-transaction package`:

```bash
export NODE=http://65.109.115.124:7777
export CHAIN=casper-test
export KEY=secret_key.pem
export PACKAGE=hash-ac102e24f6dc92e7e3b098f2af114817a67b62fe35764813854057a0859571f4

# 1. Call get_greeting (read, no args)
casper-client put-transaction package \
    --node-address $NODE --chain-name $CHAIN \
    --secret-key $KEY \
    --contract-package-hash $PACKAGE \
    --session-entry-point get_greeting \
    --payment-amount 5000000000 \
    --standard-payment true --gas-price-tolerance 1

# 2. Call set_greeting (write, with arg)
casper-client put-transaction package \
    --node-address $NODE --chain-name $CHAIN \
    --secret-key $KEY \
    --contract-package-hash $PACKAGE \
    --session-entry-point set_greeting \
    --session-arg "greeting:string='GM Casper!'" \
    --payment-amount 5000000000 \
    --standard-payment true --gas-price-tolerance 1

# 3. Call greet (read, no args)
casper-client put-transaction package \
    --node-address $NODE --chain-name $CHAIN \
    --secret-key $KEY \
    --contract-package-hash $PACKAGE \
    --session-entry-point greet \
    --payment-amount 5000000000 \
    --standard-payment true --gas-price-tolerance 1
```

Check results with: `casper-client get-transaction --node-address $NODE <TX_HASH>`
