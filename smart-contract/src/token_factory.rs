use odra::prelude::*;
use odra::casper_types::U256;

#[odra::odra_type]
pub struct TokenInfo {
    pub name: String,
    pub symbol: String,
    pub decimals: u8,
    pub total_supply: U256,
    pub deployer: Address,
}

#[odra::module]
pub struct TokenFactory {
    tokens: Mapping<u32, TokenInfo>,
    balances: Mapping<String, U256>,
    next_token_id: Var<u32>,
}

#[odra::module]
impl TokenFactory {
    #[odra(init)]
    pub fn init(&self) {}

    pub fn deploy_token(
        &mut self,
        name: String,
        symbol: String,
        decimals: u8,
        total_supply: U256,
    ) -> u32 {
        let caller = self.env().caller();
        let id = self.next_token_id.get_or_default();

        self.tokens.set(
            &id,
            TokenInfo {
                name,
                symbol,
                decimals,
                total_supply,
                deployer: caller,
            },
        );

        let key = Self::balance_key(id, &caller);
        self.balances.set(&key, total_supply);

        self.next_token_id.set(id + 1);
        id
    }

    pub fn transfer(&mut self, token_id: u32, recipient: Address, amount: U256) {
        let caller = self.env().caller();
        let sender_key = Self::balance_key(token_id, &caller);
        let sender_balance = self.balances.get(&sender_key).unwrap_or(U256::zero());

        if sender_balance < amount {
            self.env().revert(Error::InsufficientBalance);
        }

        let recipient_key = Self::balance_key(token_id, &recipient);
        let recipient_balance = self.balances.get(&recipient_key).unwrap_or(U256::zero());

        self.balances.set(&sender_key, sender_balance - amount);
        self.balances
            .set(&recipient_key, recipient_balance + amount);
    }

    pub fn balance_of(&self, token_id: u32, owner: Address) -> U256 {
        let key = Self::balance_key(token_id, &owner);
        self.balances.get(&key).unwrap_or(U256::zero())
    }

    pub fn token_info(&self, token_id: u32) -> Option<TokenInfo> {
        self.tokens.get(&token_id)
    }

    pub fn total_tokens(&self) -> u32 {
        self.next_token_id.get_or_default()
    }

    pub fn mint(&mut self, token_id: u32, recipient: Address, amount: U256) {
        let caller = self.env().caller();
        let info = self.tokens.get(&token_id);

        if info.is_none() {
            self.env().revert(Error::TokenNotFound);
        }
        let mut info = info.unwrap();

        if info.deployer != caller {
            self.env().revert(Error::NotAuthorized);
        }

        let new_supply = info.total_supply.checked_add(amount);
        if new_supply.is_none() {
            self.env().revert(Error::SupplyOverflow);
        }
        info.total_supply = new_supply.unwrap();
        self.tokens.set(&token_id, info);

        let key = Self::balance_key(token_id, &recipient);
        let balance = self.balances.get(&key).unwrap_or(U256::zero());
        self.balances.set(&key, balance + amount);
    }

    fn balance_key(token_id: u32, owner: &Address) -> String {
        let mut key = String::new();
        key.push_str(&token_id.to_string());
        key.push(':');
        key.push_str(&owner.to_string());
        key
    }
}

#[odra::odra_error]
pub enum Error {
    InsufficientBalance = 1,
    TokenNotFound = 2,
    NotAuthorized = 3,
    SupplyOverflow = 4,
}

// Tests require odra-test which needs a pinned nightly toolchain.
// Run with: cargo test --features testing on a compatible nightly.
// Current nightly (1.90.0) has serde_core alloc conflict.
// Move tests from token_factory.rs here when ready.
#[cfg(test)]
mod tests {
    #[test]
    fn placeholder() {
        // See tests/token_factory_integration.py or deploy to testnet
        assert!(true);
    }
}
