import json, os, sys

# Define assertions per eval
assertions = [
    {
        "eval": 0,
        "name": "deploy-odra-greeter",
        "checks": [
            ("uses-put-transaction-session", "put-transaction session"),
            ("has-install-upgrade-flag", "--install-upgrade"),
            ("has-odra-cfg-package-hash-key-name", "odra_cfg_package_hash_key_name"),
            ("has-odra-cfg-allow-key-override", "odra_cfg_allow_key_override"),
            ("has-odra-cfg-is-upgradable", "odra_cfg_is_upgradable"),
            ("has-odra-cfg-is-upgrade", "odra_cfg_is_upgrade"),
            ("has-init-param-greeting", "greeting"),
            ("payment-is-500-cspr", "500000000000"),
            ("includes-get-transaction-verification", "get-transaction"),
            ("uses-standard-payment", "--standard-payment"),
            ("uses-gas-price-tolerance", "--gas-price-tolerance"),
        ]
    },
    {
        "eval": 1,
        "name": "troubleshoot-error-64658",
        "checks": [
            ("identifies-error-64658", "MissingArg"),
            ("mentions-odra-call-function", "call()"),
            ("suggests-all-odra-args", "odra_cfg_package_hash_key_name"),
            ("suggests-increase-payment", "500000000000"),
            ("provides-corrected-command", "put-transaction"),
        ]
    },
    {
        "eval": 2,
        "name": "call-contract-entrypoints",
        "checks": [
            ("uses-package-subcommand", "put-transaction package"),
            ("has-correct-package-hash-format", "hash-"),
            ("get-greeting-entry-point", "get_greeting"),
            ("set-greeting-entry-point", "set_greeting"),
            ("greet-entry-point", "greet"),
            ("set-greeting-arg-format", "session-arg"),
            ("uses-contract-package-hash-option", "--contract-package-hash"),
        ]
    }
]

base = "/home/sohail/mystuff/10-Work/11-Hackathons/casper-agentic-bot/.agents/evals/odra-casper-testnet-deploy/iteration-1"

for eval_def in assertions:
    eval_id = eval_def["eval"]
    eval_name = eval_def["name"]
    
    for config in ["with_skill", "without_skill"]:
        path = f"{base}/eval-{eval_id}/{config}/outputs/response.md"
        if not os.path.exists(path):
            print(f"MISSING: {path}")
            continue
        
        with open(path) as f:
            content = f.read().lower()
        
        results = []
        for check_name, keyword in eval_def["checks"]:
            passed = keyword.lower() in content
            results.append({
                "text": check_name,
                "passed": passed,
                "evidence": f"Contains '{keyword}': {passed}"
            })
        
        grading = {
            "eval_name": eval_name,
            "config": config,
            "assertions": results
        }
        
        grading_path = f"{base}/eval-{eval_id}/{config}/grading.json"
        os.makedirs(os.path.dirname(grading_path), exist_ok=True)
        with open(grading_path, 'w') as f:
            json.dump(grading, f, indent=2)
        
        passed = sum(1 for r in results if r["passed"])
        total = len(results)
        print(f"eval-{eval_id}/{config}: {passed}/{total} passed")
