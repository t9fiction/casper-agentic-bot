use odra::prelude::*;
use odra::casper_types::U256;

#[odra::odra_type]
pub struct NftInfo {
    pub token_id: u64,
    pub owner: Address,
    pub creator: Address,
    pub metadata_uri: String,
    pub listed: bool,
    pub price: U256,
}

#[odra::module]
pub struct NftMarketplace {
    nfts: Mapping<u64, NftInfo>,
    next_token_id: Var<u64>,
}

#[odra::module]
impl NftMarketplace {
    #[odra(init)]
    pub fn init(&self) {}

    pub fn mint_nft(&mut self, metadata_uri: String, recipient: Address) -> u64 {
        let caller = self.env().caller();
        let token_id = self.next_token_id.get_or_default();

        self.nfts.set(
            &token_id,
            NftInfo {
                token_id,
                owner: recipient,
                creator: caller,
                metadata_uri,
                listed: false,
                price: U256::zero(),
            },
        );

        self.next_token_id.set(token_id + 1);
        token_id
    }

    pub fn transfer_nft(&mut self, token_id: u64, recipient: Address) {
        let caller = self.env().caller();
        let mut info = self.nfts.get(&token_id).unwrap_or_revert_with(&self.env(), Error::NftNotFound);

        if info.owner != caller {
            self.env().revert(Error::NotOwner);
        }

        info.owner = recipient;
        info.listed = false;
        info.price = U256::zero();
        self.nfts.set(&token_id, info);
    }

    pub fn list_nft(&mut self, token_id: u64, price: U256) {
        let caller = self.env().caller();
        let mut info = self.nfts.get(&token_id).unwrap_or_revert_with(&self.env(), Error::NftNotFound);

        if info.owner != caller {
            self.env().revert(Error::NotOwner);
        }

        info.listed = true;
        info.price = price;
        self.nfts.set(&token_id, info);
    }

    pub fn unlist_nft(&mut self, token_id: u64) {
        let caller = self.env().caller();
        let mut info = self.nfts.get(&token_id).unwrap_or_revert_with(&self.env(), Error::NftNotFound);

        if info.owner != caller {
            self.env().revert(Error::NotOwner);
        }

        info.listed = false;
        info.price = U256::zero();
        self.nfts.set(&token_id, info);
    }

    pub fn buy_nft(&mut self, token_id: u64, buyer: Address) {
        let mut info = self.nfts.get(&token_id).unwrap_or_revert_with(&self.env(), Error::NftNotFound);

        if !info.listed {
            self.env().revert(Error::NotListed);
        }

        info.owner = buyer;
        info.listed = false;
        info.price = U256::zero();
        self.nfts.set(&token_id, info);
    }

    pub fn nft_info(&self, token_id: u64) -> Option<NftInfo> {
        self.nfts.get(&token_id)
    }

    pub fn owner_of(&self, token_id: u64) -> Option<Address> {
        self.nfts.get(&token_id).map(|i| i.owner)
    }

    pub fn total_nfts(&self) -> u64 {
        self.next_token_id.get_or_default()
    }

    pub fn metadata_uri(&self, token_id: u64) -> Option<String> {
        self.nfts.get(&token_id).map(|i| i.metadata_uri)
    }
}

#[odra::odra_error]
pub enum Error {
    NftNotFound = 1,
    NotOwner = 2,
    NotListed = 3,
}

#[cfg(test)]
mod tests {
    #[test]
    fn placeholder() {
        assert!(true);
    }
}
