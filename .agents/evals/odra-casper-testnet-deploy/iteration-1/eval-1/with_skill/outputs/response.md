Error `64658` = **MissingArg** (discriminant 122). Odra's generated `call()` entry point expects specific named args that your command is missing.

**Problems in your command:**

1. **Missing all 4 Odra cfg args** — `odra_cfg_package_hash_key_name`, `odra_cfg_allow_key_override`, `odra_cfg_is_upgradable`, `odra_cfg_is_upgrade`
2. **Missing `--install-upgrade` flag** — required for contract installation in Casper 2.0
3. **Payment too low** — `100000000000` (100 CSPR) is not enough for a 280KB WASM; use `500000000000` (500 CSPR)

**Fixed command:**

```bash
casper-client put-transaction session \
  --node-address http://65.109.115.124:7777 \
  --chain-name casper-test \
  --secret-key secret_key.pem \
  --wasm-path Greeter.wasm \
  --payment-amount 500000000000 \
  --session-arg "odra_cfg_package_hash_key_name:string='greeter'" \
  --session-arg "odra_cfg_allow_key_override:bool='false'" \
  --session-arg "odra_cfg_is_upgradable:bool='true'" \
  --session-arg "odra_cfg_is_upgrade:bool='false'" \
  --session-arg "greeting:string='Hello World!'" \
  --install-upgrade \
  --standard-payment true \
  --gas-price-tolerance 1
```

Replace `greeting:string='Hello World!'` with your actual init parameter name and value. The 4 Odra cfg args and `--install-upgrade` are mandatory — the `call()` entry point will reject the deploy without them.
